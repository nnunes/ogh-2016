import settings
from os import getcwd
from numpy import loadtxt
import threading
import datafile
import logging

class Communication:
    def __init__(self, websocket, user, client):
        self.websocket = websocket
        self.user = user
        self.client = client
        self.recording = False

        if settings.input_type == "serial":
            self.Data = datafile.Data(self.websocket, self.user, self.client)
            self.Data.start()
        elif settings.input_type == "file":
            data = loadtxt(getcwd() + '/data/' + settings.filename)
            self.counter = 0
            self.data = data
            self.forwardDataFile()
        else:
            raise ValueError('Config error: input_type should be "serial" or "file"')

    def forwardDataFile(self):
        if self.counter == len(self.data[:, 0]) - 1:
            self.t.cancel()
        else:
            ch1 = self.data[self.counter, 0]
            ch2 = self.data[self.counter, 1]
            ch3 = self.data[self.counter, 2]
            self.websocket.send_data(self.user, 'main.getAngles_ws\t%s\t%s\t%s' % (ch1, ch2, ch3))

            self.counter += 1
            self.t = threading.Timer(1, self.forwardDataFile)
            self.t.start()
