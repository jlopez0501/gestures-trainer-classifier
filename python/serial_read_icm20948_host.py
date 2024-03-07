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

# read string
_ = ss.readline() # first read may be incomplete, just toss it

#### Exercise ####
# file_name = "front_raise" + input("Front raise set number: ") + ".csv"
# file_name = "shoulder_press" + input("Shoulder press set number: ") + ".csv"
file_name = "curl" + input("Curl set number: ") + ".csv"
# file_name = "side_raise" + input("Side raise set number: ") + ".csv"

##################

#### Exercise Directory ####
# f = open("../DMP_9D_ACCEL_Logs/front_raise/" + file_name, 'w')
# f = open("../DMP_9D_ACCEL_Logs/shoulder_press/" + file_name, 'w')
f = open("../DMP_9D_ACCEL_Logs/curl/" + file_name, 'w')
# f = open("../DMP_9D_ACCEL_Logs/side_raise/" + file_name, 'w')

############################

f.write("timeMs,ax,ay,az,q0,q1,q2,q3\n")

while True:
    # New try statement
    try:
        raw_string = ss.readline().strip().decode()
        
        j = json.loads(raw_string)
        print(j)
        s = str(j['timeMs']) + ',' + str(j['accel_x']) + ',' + str(j['accel_y']) + ',' + str(j['accel_z']) + ',' + str(j['quat_w']) + ',' + str(j['quat_x']) + ',' + str(j['quat_y']) + ',' + str(j['quat_z']) + '\n'
        f.write(s)

        '''
        # create list of floats
        data = [float(x) for x in raw_string.split(',')]

        # print them
        print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" %(data[0], data[1], data[2])) 
        '''
    except KeyboardInterrupt:
        break