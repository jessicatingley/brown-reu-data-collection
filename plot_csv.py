import pandas as pd
import sys
import os
import matplotlib.pyplot as plt


def truncate_array(arr1, arr2):
    min_length = min(len(arr1), len(arr2))
    return arr1[-min_length:], arr2[-min_length:]


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

    # Get pose from VICON data
    vicon_x = vicon_data['TX'].values / 1000
    vicon_y = vicon_data['TY'].values / 1000
    vicon_z = vicon_data['TZ'].values / 1000
    vicon_time = vicon_data['Time'].values

    # Truncate data arrays to match in size
    state_estimate_x, vicon_time = truncate_array(state_estimate_x, vicon_time)
    state_estimate_y, vicon_time = truncate_array(state_estimate_y, vicon_time)
    state_estimate_z, vicon_time = truncate_array(state_estimate_z, vicon_time)
    vicon_x, vicon_time = truncate_array(vicon_x, vicon_time)
    vicon_y, vicon_time = truncate_array(vicon_y, vicon_time)
    vicon_z, vicon_time = truncate_array(vicon_z, vicon_time)

    plt.figure(figsize=(15, 10))

    # Create subplots
    create_subplots(3, 1, vicon_time, state_estimate_x, vicon_x,
                    'State Estimate', 'Ground Truth', 'X Position (meters)')
    create_subplots(3, 2, vicon_time, state_estimate_y, vicon_y,
                    'State Estimate', 'Ground Truth', 'Y Position (meters)')
    create_subplots(3, 3, vicon_time, state_estimate_z, vicon_z,
                    'State Estimate', 'Ground Truth', 'Z Position (meters)')

    plt.tight_layout()

    plt.savefig(os.path.join(output_directory, output_name))
    plt.show()
