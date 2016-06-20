from struct import *
import threading
import hashlib
import socket
import time
import traceback
import struct
from numpy import *
from base64 import b64encode, b64decode
import actions


class User:
    user_id = 0
    socket = 0
    handshake = 0

    def __init__(self, socket, user_id):
        self.user_id = user_id
        self.socket = socket


class WebSocket():
    uid = 0
    users = []
    server = 0

    def __init__(self, address, port, connections, server):
        self.server = server

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # This enables the quick restart of the server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((address, port))
        server.listen(connections)

        while True:
            channel, details = server.accept()
            self.uid += 1
            self.users.append(User(channel, self.uid))

            ws = WebSocketThread(channel, details, self)
            result = ws.run()

            if result == False:
                quit()


class WebSocketThread(threading.Thread):
    def __init__(self, channel, details, websocket):
        self.channel = channel
        self.details = details
        self.websocket = websocket
        threading.Thread.__init__(self)

    def run(self):
        print ("Monty> Received connection ", self.details[0])

        self.handshake(self.channel)

        while True:
            result = self.interact(self.channel)

            if result == False:
                print ("Monty> closing connection")

                return True

    def find_user(self, client):
        for user in self.websocket.users:
            if user.socket == client:
                return user
        return 0

    def send_data(self, client, str):

        if (self.protocol == 'hybi-00'):
            str = self.encode_hybi00(str)
        elif (self.protocol == 'hybi-10'):
            str = self.encode_hybi10(str)

        try:
            return client.send(str)
        except IOError, e:
            if e.errno == 32:
                user = self.find_user(client)
                print ("Monty> pipe error")

    def recv_data(self, client, count):
        # acrescentar condicoes para protocolo
        try:
            buf = client.recv(count)
        except Exception:
            return False

        if (self.protocol == 'hybi-00'):
            data = buf.decode('utf-8', 'ignore')[1:]
        elif (self.protocol == 'hybi-10'):
            data = self.decode_hybi(buf)

        return data

    # This is used for older browsers - TODO Remove in the future
    def encode_hybi00(self, message):

        print "encode_hybi00"
        return b"\x00" + message.encode('utf-8') + b"\xff"

    def encode_hybi10(self, buf, opcode=0x01):

        b1 = 0x80 | (opcode & 0x0f)
        payload_len = len(buf)

        if payload_len <= 125:
            header = struct.pack('>BB', b1, payload_len)
        elif payload_len > 125 and payload_len < 65536:
            header = struct.pack('>BBH', b1, 126, payload_len)
        elif payload_len >= 65536:
            header = struct.pack('>BBQ', b1, 127, payload_len)

        return (header + str(buf))

    def decode_hybi(self, buf, base64=False):

        f = {'fin': 0,
             'opcode': 0,
             'mask': 0,
             'hlen': 2,
             'length': 0,
             'payload': None,
             'left': 0,
             'close_code': None,
             'close_reason': None}

        blen = len(buf)
        f['left'] = blen

        if blen < f['hlen']:
            # return f # Incomplete frame header
            return False

        b1, b2 = struct.unpack_from(">BB", buf)
        f['opcode'] = b1 & 0x0f
        f['fin'] = (b1 & 0x80) >> 7
        has_mask = (b2 & 0x80) >> 7

        f['length'] = b2 & 0x7f

        if f['length'] == 126:
            f['hlen'] = 4
            if blen < f['hlen']:
                # return f # Incomplete frame header
                return False
            (f['length'],) = struct.unpack_from('>xxH', buf)
        elif f['length'] == 127:
            f['hlen'] = 10
            if blen < f['hlen']:
                # return f # Incomplete frame header
                return False
            (f['length'],) = struct.unpack_from('>xxQ', buf)

        full_len = f['hlen'] + has_mask * 4 + f['length']

        if blen < full_len:  # Incomplete frame
            # return f # Incomplete frame header
            return False

        # Number of bytes that are part of the next frame(s)
        f['left'] = blen - full_len

        # Process 1 frame
        if has_mask:
            # unmask payload
            f['mask'] = buf[f['hlen']:f['hlen'] + 4]
            b = c = ''
            if f['length'] >= 4:
                mask = frombuffer(buf, dtype=dtype('<u4'),
                                  offset=f['hlen'], count=1)
                data = frombuffer(buf, dtype=dtype('<u4'),
                                  offset=f['hlen'] + 4, count=int(f['length'] / 4))
                b = bitwise_xor(data, mask).tostring()

            if f['length'] % 4:
                # print("Partial unmask")
                mask = frombuffer(buf, dtype=dtype('B'),
                                  offset=f['hlen'], count=(f['length'] % 4))
                data = frombuffer(buf, dtype=dtype('B'),
                                  offset=full_len - (f['length'] % 4),
                                  count=(f['length'] % 4))
                c = bitwise_xor(data, mask).tostring()
            f['payload'] = b + c
        else:
            print("Unmasked frame: %s" % repr(buf))
            f['payload'] = buf[(f['hlen'] + has_mask * 4):full_len]

        if base64 and f['opcode'] in [1, 2]:
            try:
                f['payload'] = b64decode(f['payload'])
            except Exception:
                print("Exception while b64decoding buffer: %s" %
                      repr(buf))
                raise

        if f['opcode'] == 0x08:
            if f['length'] >= 2:
                f['close_code'] = struct.unpack_from(">H", f['payload'])
            if f['length'] > 3:
                f['close_reason'] = f['payload'][2:]

        return f['payload']

    def recv_data_unencoded(self, client, count):

        data = client.recv(count)

        return data

    def handshake(self, client):
        shake = self.recv_data_unencoded(client, 550)

        time.sleep(0.5)
        final_line = ""
        lines = shake.splitlines()
        for line in lines:
            print line
            parts = line.partition(": ")
            if parts[0] == "Sec-WebSocket-Key1":
                key1 = parts[2]
                self.protocol = 'hybi-00'
            elif parts[0] == "Sec-WebSocket-Key2":
                key2 = parts[2]
            elif parts[0] == "Host":
                host = parts[2]
            elif parts[0] == "Origin":
                origin = parts[2]
            elif parts[0] == "Sec-WebSocket-Key":
                key = parts[2]
                self.protocol = 'hybi-10'
            final_line = line
        if self.protocol == 'hybi-00':
            spaces1 = key1.count(" ")
            spaces2 = key2.count(" ")
            num1 = int("".join([c for c in key1 if c.isdigit()])) / spaces1
            num2 = int("".join([c for c in key2 if c.isdigit()])) / spaces2
            hash = hashlib.md5(pack('>II8s', num1, num2, final_line)).digest()

            send_protocol = (
                                "HTTP/1.1 101 WebSocket Protocol Handshake\r\n"
                                "Upgrade: WebSocket\r\n"
                                "Connection: Upgrade\r\n"
                                "Sec-WebSocket-Origin: %s\r\n"
                                "Sec-WebSocket-Location: ws://%s/\r\n"
                                "\r\n"
                                "%s") % (origin, host, hash)


        elif self.protocol == 'hybi-10':

            hash = b64encode(hashlib.sha1(key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest())

            send_protocol = (
                                "HTTP/1.1 101 Switching Protocols\r\n"
                                "Upgrade: websocket\r\n"
                                "Connection: Upgrade\r\n"
                                "Sec-WebSocket-Accept: %s\r\n\r\n"
                            ) % (hash)

        client.send(send_protocol)

        self.this_user = self.find_user(client)
        self.action = actions.Action(self, self.this_user.socket, client)

    def interact(self, client):
        users = self.websocket.users
        data = self.recv_data(client, 500)

        try:
            data_line = data.split("\n")
        except Exception:
            return False

        for i in xrange(len(data_line) - 1):

            function = data_line[i].split("\t")[0].lower()
            arg = str(data_line[i].split("\t")[1:])

            print "> %s" % data_line[i]

            try:
                result = eval("self.action." + function + "(" + arg + ")")

            except Exception, e:
                print "error defining device __init__: ", str(e)
                print traceback.format_exc()
                self.send_data(self.this_user.socket, 'websocket.error_ws\t"' + str(e) + '"')
                result = True

            return result
