import json
import os


def init():
    # open json file
    # save globals

    with open(os.getcwd() + os.sep + 'config.json') as data_file:
        data = json.load(data_file)

    global logging
    global input_type
    global port
    global filename
    global output

    logging = data["logging"]
    input_type = data["input_type"]
    port = data["port"]
    filename = data["file"]
    output = data["output"]
