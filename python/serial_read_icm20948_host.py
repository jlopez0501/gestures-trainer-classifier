# SPDX-FileCopyrightText: 2021 Carter Nelson for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import argparse
import re
import serial
import time
import json

parser = argparse.ArgumentParser()
parser.add_argument("port", type=str, help="Serial port of the board", nargs=1)
args = parser.parse_args()
port = args.port

# open serial port (NOTE: change location as needed)
ss = serial.Serial(args.port[0])

loop_counter = 0
set_number = 0

while True:
    try:
        # read string
        _ = ss.readline() # first read may be incomplete, just toss it

        # Set number logic
        if loop_counter == 0:
            set_number = int(input("Specify initial set number: "))
            print(set_number)
        else:
            new_set_number = input("New set number (Press enter to increment): ")
            if new_set_number == "":
                set_number += 1
                print(set_number)
            else:
                set_number = new_set_number

        
        ##### Exercise ###

        # file_name = f"hammer_curl_4_11_hammer_curl{set_number}.csv"
        # file_name = f"pullup_4_12_pullup{set_number}.csv"
        # file_name = f"pushups_4_7_pushups{set_number}.csv"
        # file_name = f"front_raise_3_30_front_raise{set_number}.csv"
        # file_name = "shoulder_press_3_29_shoulder_press" + input("Shoulder press set number: ") + ".csv"
        # file_name = f"curl_4_5_curl{set_number}.csv"
        # file_name = f"side_raise_4_6_side_raise{set_number}.csv"
        # file_name = f"french_press_4_6_french_press{set_number}.csv"
        # file_name = f"dumbell_row_4_5_dumbell_row{set_number}.csv"
        # file_name = f"barbell_bench_press_4_12_barbell_bench_press{set_number}.csv"
        # file_name = f"rope_tricep_pushdown_4_12_rope_tricep_pushdown{set_number}.csv"
        file_name = f"gyro{set_number}.csv"
        ##################



        #### Exercise Directory ####

        # f = open("../DMP_9D_ACCEL_Logs/hammer_curl/" + file_name, 'w')
        # f = open("../DMP_9D_ACCEL_Logs/pullup/" + file_name, 'w')
        # f = open("../DMP_9D_ACCEL_Logs/pushups/" + file_name, 'w')
        # f = open("../DMP_9D_ACCEL_Logs/front_raise/" + file_name, 'w')
        # f = open("../DMP_9D_ACCEL_Logs/shoulder_press/" + file_name, 'w')
        # f = open("../DMP_9D_ACCEL_Logs/curl/" + file_name, 'w')
        # f = open("../DMP_9D_ACCEL_Logs/side_raise/" + file_name, 'w')
        # f = open("../DMP_9D_ACCEL_Logs/french_press/" + file_name, 'w')
        # f = open("../DMP_9D_ACCEL_Logs/dumbell_row/" + file_name, 'w')
        # f = open("../DMP_9D_ACCEL_Logs/barbell_bench_press/" + file_name, 'w')
        # f = open("../DMP_9D_ACCEL_Logs/rope_tricep_pushdown/" + file_name, 'w')
        f = open("../DMP_9D_ACCEL_Logs/TEST/" + file_name, 'w')
        #f = open("../DMP_9D_ACCEL_Logs/static_non_exercise/" + file_name, 'w')
        ############################

        f.write("timeMs,ax,ay,az,gx,gy,gz,q0,q1,q2,q3\n")
        
        while True:
            # New try statement
            try:
                raw_string = ss.readline().strip().decode()
                
                j = json.loads(raw_string)
                print(j)
                s = str(j['timeMs']) + ',' + str(j['accel_x']) + ',' + str(j['accel_y']) + ',' + str(j['accel_z']) + ',' + str(j['gyro_x']) + ',' + str(j['gyro_y']) + ',' + str(j['gyro_z']) + ',' + str(j['quat_w']) + ',' + str(j['quat_x']) + ',' + str(j['quat_y']) + ',' + str(j['quat_z']) + '\n'
                f.write(s)

                '''
                # create list of floats
                data = [float(x) for x in raw_string.split(',')]

                # print them
                print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" %(data[0], data[1], data[2])) 
                '''
            except ValueError:
                print("ValueError")
                continue
            except KeyboardInterrupt:
                loop_counter += 1
                break
    except KeyboardInterrupt:
        print("Exiting...")
        exit(1)