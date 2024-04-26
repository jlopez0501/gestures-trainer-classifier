import argparse
import serial
import json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from drawnow import *


parser = argparse.ArgumentParser()
parser.add_argument("port", type=str, help="Serial port of the board", nargs=1)
args = parser.parse_args()
port = args.port

# Sensor sensitivities
# Incoming Accel data is in fixed point. Where 1g = 2^16.
# ACCEL_CONVERSION = 9.80665 / 2^16 (converting g to m/s^2)
ACCEL_CONVERSION = 0.000149637603759766

#('ax', 'ay', 'az', 'q0', 'q1', 'q2', 'q3')
# 15 April 2024
#MEANS = [0.1432, 0.3892, 0.157, 0.5813, 0.2167, 0.0768, 0.2132]
#STD_DEVS = [0.8514, 0.5977, 0.5952, 0.2345, 0.4629, 0.4047, 0.3618]

# Location of tflite model file (float32 or int8 quantized)
#model_path = "ei-scaledstandartizedaq-classifier-tensorflow-lite-float32-model.lite"

# 18 April 2024
MEANS = [0.3605, 0.469, 0.2769, 0.6313, 0.292, 0.0011, 0.2809]
STD_DEVS = [0.8195, 0.5526, 0.5483, 0.2238, 0.3929, 0.367, 0.3133]

# 25 April 2024
#MEANS =  [0.3213, 0.3953, 0.2408, 0.6125, 0.2481, 0.0299, 0.285]
#STD_DEVS = [0.8994, 0.5695, 0.5539, 0.2348, 0.4228, 0.3778, 0.3243]

model_path = "ei-scaledaq-classifier-tensorflow-lite-float32-model.lite"
model_path = "ei-gym-sense-classifier-tensorflow-lite-float32-model_2sec250_lr1-4.lite"
#model_path = 'ei-gym-sense-inc.-project-1-classifier-tensorflow-lite-float32-model.lite'

# setup model for prediction: setup buffer size, setup confidence, define class names, path to model
# takes time to load model
# 18 April 2024
BUFFER_SIZE = 875
confidence = 0.3

# 4 class dataset according to Edge Impulse
# 15 April 2024
#class_names = ['curl', 'non_exersice', 'shoulder_press']

# 18 April 2024
class_names = ['curl', 'front_raise', 'non_exersice', 'shoulder_press']


dist_array = [] # for updating values

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
dist_array = []


def makeFig(): #Create a function that makes our desired plot
    plt.ylim(-2, 2)                                 #Set y min and max values
    plt.title('Acc + Q')      #Plot the title
    plt.grid(True)                                  #Turn the grid on
    plt.ylabel('Temp F')                            #Set ylabels
    plt.plot(dist_array, 'g',)       #plot the temperature
      

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
        dist_array.append([ax*ACCEL_CONVERSION , ay*ACCEL_CONVERSION, az*ACCEL_CONVERSION, q0, q1, q2, q3])
        plt.pause(.000001)      
        features.extend([(ax*ACCEL_CONVERSION - MEANS[0]) / STD_DEVS[0],
                         (ay*ACCEL_CONVERSION - MEANS[1]) / STD_DEVS[1], 
                         (az*ACCEL_CONVERSION - MEANS[2]) / STD_DEVS[2],
                         (q0 - MEANS[3]) / STD_DEVS[3], 
                         (q1 - MEANS[4]) / STD_DEVS[4],
                         (q2 - MEANS[5]) / STD_DEVS[5],
                         (q3 - MEANS[6]) / STD_DEVS[6]])

        #print(len(features))
        # buffer has reached BUFFER_SIZE rows
        if len(features) >= BUFFER_SIZE:
            
            drawnow(makeFig)                       #Call drawnow to update our live graph
            
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
            dist_array.clear();

    except KeyboardInterrupt:
        ss.close()
        plt.close()
        break
