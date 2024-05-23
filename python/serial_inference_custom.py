import argparse
import serial
import json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from drawnow import *
import pandas as pd


# Sensor sensitivities
# Incoming Accel data is in fixed point. Where 1g = 2^16.
# ACCEL_CONVERSION = 9.80665 / 2^16 (converting g to m/s^2)
ACCEL_CONVERSION = 0.000149637603759766

features = []
dist_array = [] # for updating values
confidence = 0.3

def load_config(config):
    # Load the configuration from a JSON file
    with open(config, 'r') as f:
        config = json.load(f)

    # Access the values in the dictionary
    model_path = config["model_path"]

    # Means and std devs ('ax', 'ay', 'az', 'q0', 'q1', 'q2', 'q3')
    means = config["means"]
    std_devs = config["std_devs"]
    buffer_size = config["buffer_size"]
    class_names = config["class_names"]

    print(model_path)
    print(means)
    print(std_devs)
    print(buffer_size)
    print(class_names)

    return model_path, means, std_devs, buffer_size, class_names


def load_model(model_path):
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

    return interpreter


def makeFig(): #Create a function that makes our desired plot
    plt.ylim(-2, 2)           #Set y min and max values
    plt.title('Acc + Q')      #Plot the title
    plt.grid(True)            #Turn the grid on
    plt.ylabel('Temp F')      #Set ylabels
    plt.plot(dist_array, 'g',)#plot the IMU data


def online_inference(interpreter, port, means, std_devs, buffer_size, class_names):
    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    # open serial port (NOTE: change location as needed)
    ss = serial.Serial(port)

    # read string
    _ = ss.readline() # first read may be incomplete, just toss it

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
            features.extend([(ax*ACCEL_CONVERSION - means[0]) / std_devs[0],
                            (ay*ACCEL_CONVERSION - means[1]) / std_devs[1], 
                            (az*ACCEL_CONVERSION - means[2]) / std_devs[2],
                            (q0 - means[3]) / std_devs[3], 
                            (q1 - means[4]) / std_devs[4],
                            (q2 - means[5]) / std_devs[5],
                            (q3 - means[6]) / std_devs[6]])

            #print(len(features))
            # buffer has reached buffer_size rows
            if len(features) >= buffer_size:

                drawnow(makeFig)                       #Call drawnow to update our live graph
                
                # run inference on the buffer
                print("Performing inference on %d rows of data" % (buffer_size))
                print("BUFFER SHAPE: " + str(np.array(features).shape))
                
                # Convert the feature list to a NumPy array of type float32
                np_features = np.array(features, dtype=np.float32)
                np_features = np_features.reshape((1, int(buffer_size/7), 7, 1))
                # Add dimension to input sample (TFLite model expects (# samples, data))
                #np_features = np.expand_dims(np_features, axis=0)


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
                features.clear();
                dist_array.clear();
        except json.JSONDecodeError:
            print("Invalid JSON received. Skipping this line.")
        except KeyboardInterrupt:
            ss.close()
            plt.close()
            break


def read_csv_without_timestamp(filename):
    # Read the CSV file
    df = pd.read_csv(filename)
    
    # Remove the 'timestamp' column if it exists
    if 'timestamp' in df.columns:
        df.drop(columns=['timestamp'], inplace=True)
    elif 'timeMs' in df.columns:
        df.drop(columns=['timeMs'], inplace=True)

    # Remove the first row (header row)
    df = df.iloc[1:]
    
    return df


def split_dataframe(df, chunk_size):
    # Calculate number of rows per chunk based on the chunk size
    rows_per_chunk = int(chunk_size / df.shape[1])

    # Split DataFrame into chunks of specified size
    chunks = [df.iloc[i:i+rows_per_chunk] for i in range(0, len(df), rows_per_chunk)]
    return chunks


def offline_inference(interpreter, file, means, std_devs, buffer_size, class_names):
    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    df = read_csv_without_timestamp(file)

    cs = split_dataframe(df, buffer_size)

    for i in cs:
        print(len(i))
        print(np.floor(buffer_size / df.shape[1]))
        if len(i) == np.floor(buffer_size / df.shape[1]):        
            features = i.values.flatten().tolist()
            features = np.array(features).reshape(-1, 7)

            features = features - means
            features = features / std_devs

            features = features.flatten().tolist()

            # Convert the feature list to a NumPy array of type float32
            np_features = np.array(features, dtype=np.float32)
            np_features = np_features.reshape((1, int(buffer_size/7), 7, 1))
            # Add dimension to input sample (TFLite model expects (# samples, data))
            #np_features = np.expand_dims(np_features, axis=0)

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='mode', help='Mode: offline or online')

    # Offline mode
    offline_parser = subparsers.add_parser('offline', help='Offline mode')
    offline_parser.add_argument("--config", type=str, help="Path to config", required=True)
    offline_parser.add_argument("--file", type=str, help="Path to RAW data file", required=True)

    # Online mode
    online_parser = subparsers.add_parser('online', help='Online mode')
    online_parser.add_argument("--config", type=str, help="Path to config", required=True)
    online_parser.add_argument("--port", type=str, help="Serial port of the board", required=True)

    args = parser.parse_args()
    mode = args.mode

    if mode == 'offline':
        config = args.config
        file = args.file
        model_path, means, std_devs, buffer_size, class_names = load_config(config)
        interpreter = load_model(model_path)
        offline_inference(interpreter, file, means, std_devs, buffer_size, class_names)
    elif mode == 'online':
        config = args.config
        port = args.port
        model_path, means, std_devs, buffer_size, class_names = load_config(config)
        interpreter = load_model(model_path)
        online_inference(interpreter, port, means, std_devs, buffer_size, class_names)