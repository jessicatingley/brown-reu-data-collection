import logging
import sys
import time
import csv
import os
from threading import Event

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.utils import uri_helper

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E70A')

logging.basicConfig(level=logging.ERROR)
positions = []

# deck_attached_event = Event()


def square_move_sequence(scf):
    # Moves drone in a square, maintaining same height throughout
    with PositionHlCommander(scf, controller=PositionHlCommander.CONTROLLER_PID, default_height=0.5) as pc:
        time.sleep(5)
        pc.forward(distance_m=0.5)
        time.sleep(2)
        pc.left(distance_m=0.5)
        time.sleep(2)
        pc.back(distance_m=0.5)
        time.sleep(2)
        pc.right(distance_m=0.5)


def up_down_move_sequence(scf):
    # Moves drones in a wave-like formation
    with PositionHlCommander(scf, controller=PositionHlCommander.CONTROLLER_PID, default_height=0.5) as pc:
        time.sleep(5)
        for i in range(6):
            pc.move_distance(distance_x_m=0, distance_y_m=0.2, distance_z_m=0.5)
            time.sleep(2)
            pc.move_distance(distance_x_m=0, distance_y_m=0.2, distance_z_m=-0.5)
            time.sleep(2)
        pc.move_distance(distance_x_m=-0.5, distance_y_m=0, distance_z_m=0)
        for i in range(6):
            pc.move_distance(distance_x_m=0, distance_y_m=-0.2, distance_z_m=0.5)
            time.sleep(2)
            pc.move_distance(distance_x_m=0, distance_y_m=-0.2, distance_z_m=-0.5)
            time.sleep(2)
        pc.move_distance(distance_x_m=-0.5, distance_y_m=0, distance_z_m=0)


def log_pos_callback(timestamp, data, logconf):
    print(data)
    global positions
    positions.append([data['stateEstimate.x'], data['stateEstimate.y'], data['stateEstimate.z']])


# def param_deck_flow(_, value_str):
#     value = int(value_str)
#     print(value)
#     if value:
#         deck_attached_event.set()
#         print('Deck is attached!')
#     else:
#         print('Deck is NOT attached!')


if __name__ == '__main__':
    csv_file_name = sys.argv[1]

    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:

        # TO DO: safety to ensure necessary deck is attached
        # scf.cf.param.add_update_callback(group='deck', name='bcFlow2',
        #                                  cb=param_deck_flow)
        time.sleep(1)

        logconf = LogConfig(name='Position', period_in_ms=10)
        logconf.add_variable('stateEstimate.x', 'float')
        logconf.add_variable('stateEstimate.y', 'float')
        logconf.add_variable('stateEstimate.z', 'float')
        scf.cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(log_pos_callback)

        # if not deck_attached_event.wait(timeout=5):
        #     print('No flow deck detected!')
        #     sys.exit(1)

        logconf.start()

        # Specify sequence to be used here
        square_move_sequence(scf)

        logconf.stop()

    with open(os.path.join('lighthouse_csv_files', csv_file_name), 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['State Estimate X', 'State Estimate Y', 'State Estimate Z'])
        writer.writerows(positions)
