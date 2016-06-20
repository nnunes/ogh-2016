import serial
import writefile
import settings
import numpy.polynomial.polynomial as poly
import logging

class Data():

    def __init__(self, websocket, user, client):
        self.ser = serial.Serial(settings.port, 9600)
        self.write = writefile.Write(settings.output)
        self.recording = False
        self.websocket = websocket
        self.user = user
        self.client = client

        y = [0, 30, 50, 70, 90]
        x = [700, 659, 645, 580, 535]

        self.coefs = poly.polyfit(x, y, 2)
        logging.debug(self.coefs)

    def start(self):
        if (self.ser.isOpen() == False):
            self.ser.open()
        if (self.readHeader()):
            logging.debug('header received')
            self.recording = True
            self.startAcquisition()
        else:
            raise ValueError('Error while trying to read the Header')

    def stop(self):
        self.recording = False
        self.ser.close()
        return

    def readHeader(self):
        counter = 0
        while True:
            try:
                if self.ser.inWaiting()>0:
                    counter += 1
                    line = self.ser.readline()
                    print line
                    if line[0:6]=="HEADER":
                        line_array = line.split("\t")[1:]
                        self.sensorList = line_array
                        logging.debug(self.sensorList)
                        return True
                    if counter==10:
                        #try just 10 times and then return
                        return False
            except serial.SerialException:
                logging.critical('Data could not be read from ' + settings.port)
            except Exception as e:
                logging.debug(str(e))
                logging.critical('Could not forward serial value of "' + line + '"')

    def startAcquisition(self):
        while self.recording:
            try:
                data = self.ser.readline()
                self.convertData(data)
            except serial.SerialException:
                logging.debug('Data could not be read from ' + settings.port)
            except Exception as e:
                logging.debug(str(e))
                logging.critical('Could not forward serial value of "' + data + '"')

    def convertData(self, data):
        data_string = '';
        data_array = data.split("\t");

        for i in range(len(data_array)):
            if ("G1" in self.sensorList[i]):
                data_string += str(self.gyro_calibration(data_array[i]))
            elif ("FLEX" in self.sensorList[i]):
                data_string += str(self.flex_calibration(data_array[i]))
            elif ("FSR" in self.sensorList[i]):
                data_string += str(self.fsr_calibration(data_array[i]))

            data_string += '\t';

        self.forwardSerial(data_string[:-1]);

    def gyro_calibration(self, value):
        calibrated = float(value) / -360.0
        return calibrated

    def flex_calibration(self, value):
        calibrated = poly.polyval(float(value), self.coefs)
        return calibrated

    def fsr_calibration(self, value):
        if (float(value) < 35):
            value = 0
        calibrated = float(value) / 1023.0
        return calibrated*100


    def forwardSerial(self, datastr):
        logging.debug('main.getData_ws\t'+datastr)
        print datastr
        self.write.appendLines(datastr)
        self.websocket.send_data(self.user, 'main.getData_ws\t'+datastr)
