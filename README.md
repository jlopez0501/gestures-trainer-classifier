# Gestures Trainer & Classifier

Gym Sense, Inc. was a fitness technology startup built around solving a simple
problem: manually logging your workouts is tedious and easy to forget.
If you couldn't remember how many reps you did 10 minutes ago, you were
left guessing.

Our solution was a custom wristband built on a custom PCB ordered from
JLCPCB, housed in a 3D printed enclosure developed as a proof of concept.
The wristband collected inertial measurement data which was used to train
a machine learning model capable of classifying exercises in real time —
no manual logging required.

This repository contains the full ML pipeline: data collection via Arduino,
data cleaning, augmentation, model training, and both live and offline
inference.

## Data Preparation

The data preparation process involves several steps, which are implemented in the following Jupyter notebooks:

### 1. clean_data.ipynb

This notebook is used for data cleaning and accelerometer reading scaling. It performs the following tasks:

- Cuts the measurements, assuming the first 15 seconds are preparation before the exercise starts.
- Separates the data into `non_exercise` and `exercise` classes (e.g., curl, bench, front_raise, etc.).
- Scales the accelerometer readings for both `non_exercise` and `exercise` classes.
- Plots the exercise data and saves them as PNG files for manual inspection and review.

### 2. Manual inspection and review of data

After running `clean_data.ipynb`, you should manually inspect and review the generated PNG files in the `plot` directory. If there is noise in 5-10% of the file, remove it from the dataset.

### 3. augment_dataset.ipynb

This notebook is used to augment the dataset. It adds noise and scales the data in the time domain.

### 4. curation_dataset.ipynb

This notebook is used to estimate the mean and standard deviation over the dataset and split it into training and testing sets. It performs the following tasks:

- Calculates both the mean and standard deviation for every measurement channel.
- Adds the mean and standard deviation to the inference configuration. For example:
  - Means: [0.3213, 0.3953, 0.2408, 0.6125, 0.2481, 0.0299, 0.285]
  - Std devs: [0.8994, 0.5695, 0.5539, 0.2348, 0.4228, 0.3778, 0.3243]
- Prepares the training and testing sets.
- Stores Means and Std devs to configuration file `test.json`

## Training

### 1. train_model.ipynb

This notebook is used to train the model with the prepared training and testing sets.

- Stores model and update configuration file `test.json` with model name, class names, buffer size 


## Inference

To perform inference, you can use the following instructions:

### 1. Online inference
Capture data from IMU (connected USB device) speicified by --port and do inference using configuration file `../configs/test.json`
  
  `python serial_inference_custom.py online --port /dev/cu.usbmodem14201 --config ../configs/test.json`

### 2. Offline inference
Uses RAW captured data from IMU (path to file) specified by parameter --file  and do inference using configuration file specifiedy by parameter --config `../configs/test.json`

  `python serial_inference_custom.py offline --config ../configs/test.json --file ../DMP_9D_ACCEL_Logs/curl/curl_3_10_curl1.csv`


## Plot Data Graph

The `plot_graph.py` script is used to visualize gesture data using different dimensionality reduction techniques and 3D plotting. 

### Usage

`python plot_graph.py --csv_path <path_to_csv> --plot_type <plot_type>`

Arguments:
1. --csv_path: Path to the CSV file containing the gesture data.
2. --plot_type: Type of plot to generate. Choices are **pca**, **tsne**, **umap**, or **3d**.
