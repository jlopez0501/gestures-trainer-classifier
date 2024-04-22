import pandas as pd
import sys
import matplotlib.pyplot as plt
import glob

def plot_graph(file_path):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)

    # Plot the data
    plt.figure(figsize=(10, 6))

    # Plot each column
    tSec = (df['timeMs'] - df['timeMs'].iloc[0])/1000
    plt.plot(tSec, df['ax'], label='ax')
    plt.plot(tSec, df['ay'], label='ay')
    plt.plot(tSec, df['az'], label='az')
    plt.plot(tSec, df['q0'], label='q0')
    plt.plot(tSec, df['q1'], label='q1')
    plt.plot(tSec, df['q2'], label='q2')
    plt.plot(tSec, df['q3'], label='q3')

    # Add labels and title
    plt.xlabel('Index')
    plt.ylabel('Values')
    plt.title('Plotting Data from CSV File')
    plt.legend()

    # Show the plot
    plt.show()

if __name__ == "__main__":
    # Replace the directory path with the actual directory containing your CSV files
    directory_path = '../DMP_9D_ACCEL_Logs/TEST/'
    
    # Get a list of all CSV files in the directory
    csv_files = glob.glob(directory_path + '*.csv')

    # Plot graphs for each CSV file
    for file_path in csv_files:
        plot_graph(file_path)
