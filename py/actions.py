"""
Data has to be passed through the websocket as a STRING always.
We will have the following convention:
1. TO RECEIVE DATA FROM WEB
   The name of each function here, is the first argument sent in javascript
   with websocket.send_request("FUNCTION", "ARGUMENT1 \t ARGUMENT2")
   ex:
   >>> websocket.send_request('TEST','\t'); in main.js
   >>> this request will end up in the 'test' function of this file

2. TO SEND DATA TO THE WEB
   Use always command self.websocket.send_data(self.user, 'data_to_send')
   'Data_to_send' should be in the following format:
   js_module_name.js_module_function_ws\targ1,arg2,arg3
  ex:
  self.websocket.send_data(self.user, "main.start_page_ws\t'" + res1 + "','" + res2 + "','" + \
          res3 + "','" +  res4 + "','" + res5 + "'")
  self.websocket.send_data(self.user, "main.progress_ws\t" + "[" + str(percentage) + "]")
"""
import communication
import logging

class Action:

    def __init__(self, websocket, user, client):
        self.websocket = websocket
        self.user = user
        self.client = client

    def test(self, data):
        logging.debug('received > test')
        self.websocket.send_data(self.user, 'websocket.test_ws\t')
        return True

    def browser_ready(self, data):
        logging.debug('received > browser ready')

        self.strm = communication.Communication(self.websocket, self.user, self.client)
        return True
