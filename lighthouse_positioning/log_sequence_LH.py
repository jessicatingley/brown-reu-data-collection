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

deck_attached_event = Event()


def square_move_sequence(scf):
    # Moves drone in a square, maintaining same height throughout
    commander = scf.cf.high_level_commander
    square = [(0.0, 0.0, 0.5),
              (0.0, 0.5, 0.5),
              (0.5, 0.5, 0.5),
              (0.5, 0.0, 0.5),
              (0.0, 0.0, 0.5)]

    commander.takeoff(absolute_height_m=0.5, duration_s=1.5)
    time.sleep(5)
    for pos in square:
        commander.go_to(pos[0], pos[1], pos[2], yaw=0, duration_s=2.0)
        time.sleep(2)

    commander.land(absolute_height_m=0.0, duration_s=1.5)


def up_down_move_sequence(scf):
    # Moves drones in a wave-like formation
    commander = scf.cf.high_level_commander
    commander.takeoff(absolute_height_m=0.5, duration_s=1.5)
    time.sleep(5)
    for i in range(2):
        commander.go_to(x=0, y=0.3, z=0.5, yaw=0, duration_s=1)
        time.sleep(1)
        commander.go_to(x=0, y=0.3, z=-0.5, yaw=0, duration_s=1)
        time.sleep(1)

    time.sleep(2)
    commander.go_to(x=-0.5, y=0, z=0, yaw=0, duration_s=2)
    time.sleep(2)

    for i in range(2):
        commander.go_to(x=0, y=-0.3, z=0.5, yaw=0, duration_s=1)
        time.sleep(1)
        commander.go_to(x=0, y=-0.3, z=-0.5, yaw=0, duration_s=1)
        time.sleep(1)

    time.sleep(2)
    commander.go_to(x=0.5, y=0, z=0, yaw=0, duration_s=2)
    time.sleep(2)

    commander.land(absolute_height_m=0.0, duration_s=1.5)


def log_pos_callback(timestamp, data, logconf):
    print(data)
    global positions
    positions.append([data['stateEstimate.x'], data['stateEstimate.y'], data['stateEstimate.z']])


def param_deck(_, value_str):
    value = int(value_str)
    print(value)
    if value:
        deck_attached_event.set()
        print('Deck is attached!')
    else:
        print('Deck is NOT attached!')


if __name__ == '__main__':
    csv_file_name = sys.argv[1]

    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        # 1 = PID, 2 = Mellinger
        scf.cf.param.set_value('stabilizer.controller', 1)
        scf.cf.param.add_update_callback(group='deck', name='bcLighthouse4',
                                         cb=param_deck)
        time.sleep(1)

        logconf = LogConfig(name='Position', period_in_ms=10)
        logconf.add_variable('stateEstimate.x', 'float')
        logconf.add_variable('stateEstimate.y', 'float')
        logconf.add_variable('stateEstimate.z', 'float')
        scf.cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(log_pos_callback)

        if not deck_attached_event.wait(timeout=5):
            print('No flow deck detected!')
            sys.exit(1)

        logconf.start()

        # Specify sequence to be used here
        up_down_move_sequence(scf)

        logconf.stop()

    with open(os.path.join('lighthouse_csv_files', csv_file_name), 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['State Estimate X', 'State Estimate Y', 'State Estimate Z'])
        writer.writerows(positions)
