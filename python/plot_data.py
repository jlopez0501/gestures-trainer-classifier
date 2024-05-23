import pandas as pd
import sys
import matplotlib.pyplot as plt

# Replace 'data.csv' with the actual name of your CSV file
file_path = '../DMP_9D_ACCEL_Logs/TEST/front_raise_3_30_front_raise2.csv'

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)

    # Plot the data
    plt.figure(figsize=(10, 6))

    # Plot each column
    # Remove the 'timestamp' column if it exists
    if 'timestamp' in df.columns:
        tSec = (df['timestamp'] - df['timestamp'].iloc[0])/1000
    elif 'timeMs' in df.columns:
        tSec = (df['timeMs'] - df['timeMs'].iloc[0])/1000

    plt.plot(tSec, df['ax'], label='ax')
    plt.plot(tSec, df['ay'], label='ay')
    plt.plot(tSec, df['az'], label='az')
    plt.plot(tSec, df['q0'], label='q0')
    plt.plot(tSec, df['q1'], label='q1')
    plt.plot(tSec, df['q2'], label='q2')
    plt.plot(tSec, df['q3'], label='q3')

    plt.grid()

    # Add labels and title
    plt.xlabel('Index')
    plt.ylabel('Values')
    plt.title('Plotting Data from CSV File')
    plt.legend()

    # Show the plot
    plt.show()

