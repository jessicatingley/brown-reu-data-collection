import pandas as pd
import sys
import os
import matplotlib.pyplot as plt
import numpy as np


def create_subplots(num_subplots, index, x_data, estimate_data, truth_data, estimate_label, truth_label, y_axis_label):
    plt.subplot(num_subplots, 1, index)
    plt.plot(x_data, estimate_data, label=estimate_label, color='blue')
    plt.plot(x_data, truth_data, label=truth_label, color='red')
    plt.xlabel('Time (Seconds)')
    plt.ylabel(y_axis_label)
    plt.title('State Estimate and Ground Truth vs Time')
    plt.legend()
    plt.grid(True)


if __name__ == '__main__':
    file_name = sys.argv[1]
    vicon_file_name = sys.argv[2]
    output_name = sys.argv[3]
    output_directory = sys.argv[4]

    # Read data from csv files
    state_estimate_data = pd.read_csv(file_name)
    vicon_data = pd.read_csv(vicon_file_name)

    # Get pose from state estimate
    state_estimate_x = state_estimate_data['State Estimate X'].values
    state_estimate_y = state_estimate_data['State Estimate Y'].values
    state_estimate_z = state_estimate_data['State Estimate Z'].values
    avg_state_estimate_x = np.mean(state_estimate_x[:10])
    avg_state_estimate_y = np.mean(state_estimate_y[:10])
    avg_state_estimate_z = np.mean(state_estimate_z[:10])

    # Get pose from VICON data
    vicon_x = vicon_data['TX'].values / 1000
    vicon_y = vicon_data['TY'].values / 1000
    vicon_z = vicon_data['TZ'].values / 1000
    vicon_time = vicon_data['Time'].values
    avg_vicon_x = np.mean(vicon_x[:20])
    avg_vicon_y = np.mean(vicon_y[:20])
    avg_vicon_z = np.mean(vicon_z[:20])

    # Get standard deviation of first ten values -- acts as threshold
    threshold_state_est_x = np.std(state_estimate_x[:20])
    threshold_state_est_y = np.std(state_estimate_y[:20])
    threshold_state_est_z = np.std(state_estimate_z[:20])
    threshold_vicon_x = np.std(vicon_x[:20])
    threshold_vicon_y = np.std(vicon_y[:20])
    threshold_vicon_z = np.std(vicon_z[:20])
    print(threshold_state_est_x, threshold_state_est_y)

    # Find point at which movement starts - iterate through data until value surpasses threshold + avg of first 10 vals
    state_est_start_x = None
    for i in range(len(state_estimate_x)):
        if state_estimate_x[i] > avg_state_estimate_x + 5*threshold_state_est_x:
            state_est_start_x = i
            break
    state_est_start_y = None
    for i in range(len(state_estimate_y)):
        if state_estimate_y[i] > avg_state_estimate_y + 5*threshold_state_est_y:
            state_est_start_y = i
            break
    state_est_start_z = None
    for i in range(len(state_estimate_z)):
        if state_estimate_z[i] > avg_state_estimate_z + 5*threshold_state_est_z:
            state_est_start_z = i
            break
    vicon_start_val_x = None
    for i in range(len(vicon_x)):
        if vicon_x[i] > avg_vicon_x + 20*threshold_vicon_x:
            vicon_start_val_x = i
            break
    vicon_start_val_y = None
    for i in range(len(vicon_y)):
        if vicon_y[i] > avg_vicon_y + 15*threshold_vicon_y:
            vicon_start_val_y = i
            break
    vicon_start_val_z = None
    for i in range(len(vicon_z)):
        if vicon_z[i] > avg_vicon_z + 6*threshold_vicon_z:
            vicon_start_val_z = i
            break

    # Truncated data to be plotted
    new_state_estimate_x = state_estimate_x[state_est_start_x:]
    new_state_estimate_y = state_estimate_y[state_est_start_y:]
    new_state_estimate_z = state_estimate_z[state_est_start_z:]
    new_vicon_x = vicon_x[vicon_start_val_x:]
    new_vicon_y = vicon_y[vicon_start_val_y:]
    new_vicon_z = vicon_z[vicon_start_val_z:]

    plt.figure(figsize=(15, 10))

    # Create subplots
    create_subplots(3, 1, vicon_time[:len(new_state_estimate_x)], new_state_estimate_x,
                    new_vicon_x[:len(new_state_estimate_x)],'State Estimate', 'Ground Truth',
                    'X Position (meters)')
    create_subplots(3, 2, vicon_time[:len(new_state_estimate_y)], new_state_estimate_y,
                    new_vicon_y[:len(new_state_estimate_y)], 'State Estimate', 'Ground Truth',
                    'Y Position (meters)')
    create_subplots(3, 3, vicon_time[:len(new_state_estimate_z)], new_state_estimate_z,
                    new_vicon_z[:len(new_state_estimate_z)], 'State Estimate', 'Ground Truth',
                    'Z Position (meters)')

    plt.tight_layout()

    plt.savefig(os.path.join(output_directory, output_name))
    plt.show()
