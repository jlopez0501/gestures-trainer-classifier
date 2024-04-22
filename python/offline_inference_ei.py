import numpy as np
import tensorflow as tf
import argparse
import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument("csv", type=str, help="File with readings", nargs=1)
args = parser.parse_args()
csv_file = args.csv
print("File : ", csv_file)
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

model_path = "ei-scaledaq-classifier-tensorflow-lite-float32-model.lite"
model_path = "ei-gym-sense-classifier-tensorflow-lite-float32-model.lite"

# setup model for prediction: setup buffer size, setup confidence, define class names, path to model
# takes time to load model
BUFFER_SIZE = 2184
confidence = 0.3

# 4 class dataset according to Edge Impulse
# 15 April 2024
#class_names = ['curl', 'non_exersice', 'shoulder_press']

# 18 April 2024
class_names = ['curl', 'front_raise', 'non_exersice', 'shoulder_press']

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

def read_csv_without_timestamp(filename):
    # Read the CSV file
    df = pd.read_csv(filename)
    
    # Remove the 'timestamp' column if it exists
    if 'timestamp' in df.columns:
        df.drop(columns=['timestamp'], inplace=True)
    
    # Remove the first row (header row)
    df = df.iloc[1:]
    
    return df

df = read_csv_without_timestamp(csv_file[0])

print(len(df))
def split_dataframe(df, chunk_size):
    # Calculate number of rows per chunk based on the chunk size
    rows_per_chunk = int(chunk_size / df.shape[1])

    # Split DataFrame into chunks of specified size
    chunks = [df.iloc[i:i+rows_per_chunk] for i in range(0, len(df), rows_per_chunk)]
    return chunks

cs = split_dataframe(df, BUFFER_SIZE)

print("Chunks : ", len(cs))

for i in cs:
    print(len(i))
    if len(i) == BUFFER_SIZE / df.shape[1]:        
        features = i.values.flatten().tolist()
        features = np.array(features).reshape(-1, 7)

        features = features - MEANS
        features = features / STD_DEVS

        features = features.flatten().tolist()

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