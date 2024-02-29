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
    plt.plot(df['timeMs'], df['q0'], label='q0')
    plt.plot(df['timeMs'], df['q1'], label='q1')
    plt.plot(df['timeMs'], df['q2'], label='q2')
    plt.plot(df['timeMs'], df['q3'], label='q3')

    # Add labels and title
    plt.xlabel('Index')
    plt.ylabel('Values')
    plt.title('Plotting Data from CSV File')
    plt.legend()

    # Show the plot
    plt.show()

