from datetime import datetime
from numpy import reshape, array, zeros, uint16, uint8, maximum, delete
import os
import json
import threading


class Write(threading.Thread):

    def __init__(self, filename):
    	self.filename = filename

        print filename

        self.f = open('data/'+self.filename, 'w')

    	self.MAXBUFFER = 2**15
    	self.start_sample = 0

    	self.nframes  = 0
    	#pointers
    	self.suspend = 0
    	self.tail = 0
    	self.head = 0
    	self.recording = 0

    	#lists of data
    	self.frames = [0]*self.MAXBUFFER
    	self.data = [0]*self.MAXBUFFER

    	threading.Thread.__init__( self )

    def closefile():
        self.f.close()

    def appendLines(self, data):
    	self.f.write(data)
    	self.f.write("\n")
    	return
