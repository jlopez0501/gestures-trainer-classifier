import os
import glob
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, filtfilt, argrelextrema


def butter_lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y


def count_repetitions(timestamp:list, ax:list, ay:list, az:list, fs:float, cutoff_low:float, order=10) -> int:
    df = pd.DataFrame({'timestamp': timestamp, 'ax': ax, 'ay': ay, 'az': az})
    df['aMagnitude'] = np.sqrt(df['ax']**2 + df['ay']**2 + df['az']**2)
    df['aMagnitudeFiltered'] = lowpass_filter(df['aMagnitude'], cutoff_low, fs, order=order)

    indecies = argrelextrema(df['aMagnitudeFiltered'].values, np.greater)
    print("Instant repetition number : ", len(indecies[0]))

    peaks = df.iloc[indecies]

    # Calculate the intervals between peaks to determine repetitions
    peak_intervals = np.diff(peaks['timestamp'])
    print("Peak intervals : ", peak_intervals/1000.)

    # Get mean of intervals
    mean_interval = np.mean(peak_intervals)

    tolerance = 0.8 * mean_interval  # 20% tolerance
    repetitions = np.sum((peak_intervals > (mean_interval - tolerance)) & (peak_intervals < (mean_interval + tolerance)))
    print(f"Number of repetitions: {repetitions}")

    return repetitions


if __name__ == '__main__':
    df = pd.read_csv("../DMP_9D_ACCEL_Logs/cleaned_new/front_raise/front_raise.1.csv") # cut off freq = 1

    tSec = (df['timestamp'] - df['timestamp'].iloc[0])/1000
    fs = 1 / (tSec[1] - tSec[0])  # Sampling frequency
    print(fs)
    cutoff_low = .7 # Lowpass filter cutoff frequency (Hz)

    ax = df['ax'].tolist()
    ay = df['ay'].tolist()
    az = df['az'].tolist()
    timestamp = df['timestamp'].tolist()

    reps_num = count_repetitions(timestamp, ax, ay, az, fs, cutoff_low)
    print(f"Number of repetitions: {reps_num}")