import argparse
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
import matplotlib.pyplot as plt
import ast
import plotly.graph_objs as go
import plotly.express as px

# Mapping gesture labels to class names
gesture_mapping = {
    0: 'curl',
    1: 'dumbell_row',
    2: 'front_raise',
    3: 'hammer_curl',
    4: 'non_exersice',
    5: 'shoulder_press'
}

# Define colors for different gestures
gesture_colors = {
    0: 'yellow',
    1: 'red',
    2: 'green',
    3: 'blue',
    4: 'black',
    5: 'magenta'
}

def convert_to_list(acceleration_str):
    """
    Convert string representation of list to an actual list.
    
    Args:
        acceleration_str (str): String representation of the list.
        
    Returns:
        list: The converted list.
    """
    return ast.literal_eval(acceleration_str)

def plot_pca(data):
    """
    Plot PCA of gesture data.

    Args:
        data (pd.DataFrame): Data containing gesture labels and acceleration data.
    """
    gestures = data['gesture']
    acceleration_data = data['acceleration'].apply(eval).tolist()
    acceleration_data = np.array([np.mean(sample, axis=0) for sample in acceleration_data])

    # Perform PCA
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(acceleration_data)

    # Create class labels
    class_labels = [gesture_mapping[gesture] for gesture in gestures]

    # Create PCA plot
    plt.figure(figsize=(12, 10))

    for i, class_name in gesture_mapping.items():
        idx = np.where(gestures == i)
        plt.scatter(pca_result[idx, 0], pca_result[idx, 1], label=class_name, alpha=0.6, edgecolors='w', s=100)

    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.title('PCA of Gestures with Class Labels')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_tsne(data):
    """
    Plot t-SNE of gesture data.

    Args:
        data (pd.DataFrame): Data containing gesture labels and acceleration data.
    """
    gestures = data['gesture']
    acceleration_data = data['acceleration'].apply(eval).tolist()
    acceleration_data = np.array([np.mean(sample, axis=0) for sample in acceleration_data])

    # Perform t-SNE
    tsne = TSNE(n_components=2, random_state=42, perplexity=30)
    tsne_result = tsne.fit_transform(acceleration_data)

    # Create class labels
    class_labels = [gesture_mapping[gesture] for gesture in gestures]

    # Create t-SNE plot
    plt.figure(figsize=(12, 10))

    for i, class_name in gesture_mapping.items():
        idx = np.where(gestures == i)
        plt.scatter(tsne_result[idx, 0], tsne_result[idx, 1], label=class_name, alpha=0.6, edgecolors='w', s=100)

    plt.xlabel('t-SNE Component 1')
    plt.ylabel('t-SNE Component 2')
    plt.title('t-SNE of Gestures with Class Labels')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_umap(data):
    """
    Plot UMAP of gesture data.

    Args:
        data (pd.DataFrame): Data containing gesture labels and acceleration data.
    """
    gestures = data['gesture']
    acceleration_data = data['acceleration'].apply(eval).tolist()
    acceleration_data = np.array([np.mean(sample, axis=0) for sample in acceleration_data])

    # Perform UMAP
    umap_model = umap.UMAP(n_components=2, random_state=42)
    umap_result = umap_model.fit_transform(acceleration_data)

    # Create class labels
    class_labels = [gesture_mapping[gesture] for gesture in gestures]

    # Create UMAP plot
    plt.figure(figsize=(12, 10))

    for i, class_name in gesture_mapping.items():
        idx = np.where(gestures == i)
        plt.scatter(umap_result[idx, 0], umap_result[idx, 1], label=class_name, alpha=0.6, edgecolors='w', s=100)

    plt.xlabel('UMAP Component 1')
    plt.ylabel('UMAP Component 2')
    plt.title('UMAP of Gestures with Class Labels')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_3d(data):
    """
    Plot 3D scatter plot of gesture data.

    Args:
        data (pd.DataFrame): Data containing gesture labels and acceleration data.
    """
    data['acceleration'] = data['acceleration'].apply(convert_to_list)

    # Prepare data for Plotly
    plot_data = []
    for gesture in data['gesture'].unique():
        gesture_data = data[data['gesture'] == gesture]
        x_vals = []
        y_vals = []
        z_vals = []
        for idx, row in gesture_data.iterrows():
            acceleration = row['acceleration']
            x_vals.extend([point[0] for point in acceleration])
            y_vals.extend([point[1] for point in acceleration])
            z_vals.extend([point[2] for point in acceleration])
        
        plot_data.append(go.Scatter3d(
            x=x_vals,
            y=y_vals,
            z=z_vals,
            mode='markers',
            marker=dict(size=2, color=gesture_colors.get(gesture, 'black')),
            name=gesture_mapping.get(gesture, f'Gesture {gesture}')
        ))

    # Create the layout
    layout = go.Layout(
        scene=dict(
            xaxis_title='X Axis',
            yaxis_title='Y Axis',
            zaxis_title='Z Axis'
        )
    )

    # Create the figure
    fig = go.Figure(data=plot_data, layout=layout)

    # Show the figure
    fig.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot graphs with data')
    parser.add_argument("--csv_path", type=str, help="Path to csv to visualize", required=True)
    parser.add_argument('--plot_type', type=str, required=True, choices=['pca', 'tsne', 'umap', '3d'],
                        help='Type of plot to generate: pca, tsne, umap, or 3d')

    args = parser.parse_args()

    # Load data from CSV
    data = pd.read_csv(args.csv_path)

    # Plot based on the specified plot type
    if args.plot_type == 'pca':
        plot_pca(data)
    elif args.plot_type == 'tsne':
        plot_tsne(data)
    elif args.plot_type == 'umap':
        plot_umap(data)
    elif args.plot_type == '3d':
        plot_3d(data)
    else:
        print(f"Unknown plot type: {args.plot_type}")
