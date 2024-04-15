import numpy as np
import tensorflow as tf

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

# Sensor sensitivities
# Incoming Accel data is in fixed point. Where 1g = 2^16.
# ACCEL_CONVERSION = 9.80665 / 2^16 (converting g to m/s^2)
ACCEL_CONVERSION = 0.000149637603759766

# Location of tflite model file (float32 or int8 quantized)
model_path = "ei-scaledaq-classifier-tensorflow-lite-float32-model.lite"

# setup model for prediction: setup buffer size, setup confidence, define class names, path to model
# takes time to load model
BUFFER_SIZE = 2184
confidence = 0.3

# 4 class dataset according to Edge Impulse
class_names = ['curl', 'non_exersice']

# Load TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path=model_path)

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Allocate tensors
interpreter.allocate_tensors()

# Print the input and output details of the model
print(input_details)
print(output_details)

# open serial port (NOTE: change location as needed)
ss = serial.Serial(args.port[0])

# read string
_ = ss.readline() # first read may be incomplete, just toss it

# Processed features (copy from Edge Impulse project)
features = []

print("Start real-time predicitions")
while True:
    # New try statement
    try:
        raw_string = ss.readline().strip().decode()
        
        j = json.loads(raw_string)
        # print(j)
        # get accelerometer and quarternions values
        ax, ay, az, q0, q1, q2, q3 = j['accel_x'], j['accel_y'], j['accel_x'], j['quat_w'], j['quat_x'], j['quat_y'], j['quat_z']

        # add accelerometer and quarternions to buffer
        features.extend([ax*ACCEL_CONVERSION, ay*ACCEL_CONVERSION, az*ACCEL_CONVERSION, q0, q1, q2, q3])
        #print(len(features))
        # buffer has reached BUFFER_SIZE rows
        if len(features) >= BUFFER_SIZE:
            
            # run inference on the buffer
            print("Performing inference on %d rows of data" % (BUFFER_SIZE))
            print("BUFFER SHAPE: " + str(np.array(features).shape))
            
            # Convert the feature list to a NumPy array of type float32
            np_features = np.array(features, dtype=np.float32)

            # Add dimension to input sample (TFLite model expects (# samples, data))
            np_features = np.expand_dims(np_features, axis=0)

            # Create input tensor out of raw features
            interpreter.set_tensor(input_details[0]['index'], np_features)

            # Run inference
            interpreter.invoke()

            # output_details[0]['index'] = the index which provides the input
            output_data = interpreter.get_tensor(output_details[0]['index'])

            # Print the results of inference
            print("Inference output is {}".format(output_data))

            max_confidence_index = np.argmax(output_data, axis=1)[0]  # index with max confidence
            max_confidence_value = np.max(output_data, axis=1)[0]  # max confidence
            print("MAX CONFIDENCE: " + str(max_confidence_value))
            
            # Check confidence threshold
            if max_confidence_value > confidence:
                y_pred_label = class_names[max_confidence_index]
                print('GESTURE: ', y_pred_label)

            # clear the buffer to start collecting another 500 rows
            features.clear()

    except KeyboardInterrupt:
        break