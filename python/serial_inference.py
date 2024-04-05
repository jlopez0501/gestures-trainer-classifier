# SPDX-FileCopyrightText: 2021 Carter Nelson for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import argparse
import re
import serial
import time
import json
import numpy as np
from tensorflow import keras

parser = argparse.ArgumentParser()
parser.add_argument("port", type=str, help="Serial port of the board", nargs=1)
args = parser.parse_args()
port = args.port

# setup model for prediction: setup buffer size, setup confidence, define class names, path to model
# takes time to load model
BUFFER_SIZE = 500
confidence = 0.3

# Full dataset
class_names = ['barbell_bench_press', 'curl', 'dumbell_row', 'french_press', 'front_raise', 'non_exersice', 'rope_tricep_pushdown', 'shoulder_press', 'side_raise']

# 4 class dataset
class_names = ['curl', 'front_raise', 'non_exersice', 'shoulder_press']
gesture_model_path = './weights.best.hdf5'
gesture_model = keras.models.load_model(gesture_model_path)

# open serial port (NOTE: change location as needed)
ss = serial.Serial(args.port[0])

# read string
_ = ss.readline() # first read may be incomplete, just toss it

# Initialize a buffer to collect Qs for inference
buffer = []

print("Start real-time predicitions")
while True:
    # New try statement
    try:
        raw_string = ss.readline().strip().decode()
        
        j = json.loads(raw_string)
        # print(j)
        # get quarternions values
        ax, ay, az, q0, q1, q2, q3 = j['accel_x'], j['accel_y'], j['accel_x'], j['quat_w'], j['quat_x'], j['quat_y'], j['quat_z']

        # add quarternions to buffer
        buffer.append([ax, ay, az, q0, q1, q2, q3])

        # buffer has reached BUFFER_SIZE rows
        if len(buffer) >= BUFFER_SIZE:
            
            # run inference on the buffer
            print("Performing inference on %d rows of data" % (BUFFER_SIZE))
            print("BUFFER SHAPE: " + str(np.array(buffer).shape))
            
            # run inference and post process
            y_pred = gesture_model.predict(np.array(buffer)[np.newaxis, :, :])
            print("Y PRED: " + str(y_pred))
            max_confidence_index = np.argmax(y_pred, axis=1)[0]  # index with max confidence
            max_confidence_value = np.max(y_pred, axis=1)[0]  # max confidence
            print("MAX CONFIDENCE: " + str(max_confidence_value))
            # Check confidence threshold
            if max_confidence_value > confidence:
                y_pred_label = class_names[max_confidence_index]
                print('GESTURE: ', y_pred_label)

            # clear the buffer to start collecting another 500 rows
            buffer.clear()

    except KeyboardInterrupt:
        break
