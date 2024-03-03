import pandas as pd
import sys
import matplotlib.pyplot as plt

# Replace 'data.csv' with the actual name of your CSV file
file_path = 'data.csv'

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)

    # Plot the data
    plt.figure(figsize=(10, 6))

    # Plot each column
    tSec = (df['timeMs'] - df['timeMs'].iloc[0])/1000
    plt.plot(tSec, df['ax'], label='q0')
    plt.plot(tSec, df['ay'], label='q1')
    plt.plot(tSec, df['az'], label='q2')
    plt.plot(tSec, df['q0'], label='q3')

    # Add labels and title
    plt.xlabel('Index')
    plt.ylabel('Values')
    plt.title('Plotting Data from CSV File')
    plt.legend()

    # Show the plot
    plt.show()

