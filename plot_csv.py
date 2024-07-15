import pandas as pd
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from fastdtw import fastdtw


def create_subplots(num_subplots, index, x_data, estimate_data, truth_data, estimate_label, truth_label, y_axis_label):
    plt.subplot(num_subplots, 1, index)
    plt.plot(x_data, estimate_data, label=estimate_label, color='blue')
    plt.plot(x_data, truth_data, label=truth_label, color='red')
    plt.xlabel('Time (Seconds)')
    plt.ylabel(y_axis_label)
    plt.title('State Estimate and Ground Truth vs Time')
    plt.legend()
    plt.grid(True)


def align_data(vicon_data, estimate_data, vicon_time):
    # Align data using FastDTW
    distance, path = fastdtw(vicon_data, estimate_data, dist=2)
    aligned_vicon_data = np.array([vicon_data[i] for i, j in path])
    aligned_state_est = np.array([estimate_data[j] for i, j in path])
    aligned_vicon_time = np.array([vicon_time[i] for i, j in path])
    return aligned_vicon_data, aligned_state_est, aligned_vicon_time


if __name__ == '__main__':
    # Change file paths for different sensor types
    file_name = os.path.join('lighthouse_positioning/lighthouse_csv_files', sys.argv[1])
    vicon_file_name = os.path.join('lighthouse_positioning/lighthouse_vicon_csv_files', sys.argv[2])
    output_name = os.path.join('lighthouse_positioning/lighthouse_plots', sys.argv[3])

    # Read data from csv files
    state_estimate_data = pd.read_csv(file_name)
    vicon_data = pd.read_csv(vicon_file_name)

    # Get pose from state estimate
    state_estimate_x = state_estimate_data['State Estimate X'].values
    state_estimate_y = state_estimate_data['State Estimate Y'].values
    state_estimate_z = state_estimate_data['State Estimate Z'].values

    # Get pose from VICON data
    vicon_x = vicon_data['TX'].values / 1000
    vicon_y = vicon_data['TY'].values / 1000
    vicon_z = vicon_data['TZ'].values / 1000
    vicon_time = vicon_data['Time'].values

    # Align data using FastDTW
    aligned_vicon_x, aligned_state_est_x, aligned_vicon_time_x = align_data(vicon_x, state_estimate_x, vicon_time)
    aligned_vicon_y, aligned_state_est_y, aligned_vicon_time_y = align_data(vicon_y, state_estimate_y, vicon_time)
    aligned_vicon_z, aligned_state_est_z, aligned_vicon_time_z = align_data(vicon_z, state_estimate_z, vicon_time)

    plt.figure(figsize=(15, 10))

    # Create subplots
    create_subplots(3, 1, aligned_vicon_time_x[:len(aligned_state_est_x)], aligned_state_est_x,
                    aligned_vicon_x[:len(aligned_state_est_x)], 'State Estimate', 'Ground Truth',
                    'X Position (meters)')
    create_subplots(3, 2, aligned_vicon_time_y[:len(aligned_state_est_y)], aligned_state_est_y,
                    aligned_vicon_y[:len(aligned_state_est_y)], 'State Estimate', 'Ground Truth',
                    'Y Position (meters)')
    create_subplots(3, 3, aligned_vicon_time_z[:len(aligned_state_est_z)], aligned_state_est_z,
                    aligned_vicon_z[:len(aligned_state_est_z)], 'State Estimate', 'Ground Truth',
                    'Z Position (meters)')

    plt.tight_layout()

    plt.savefig(output_name)
    plt.show()
