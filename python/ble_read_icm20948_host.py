import os, sys
import asyncio
import platform
from datetime import datetime
from typing import Callable, Any

from aioconsole import ainput
from bleak import BleakClient, discover
import struct


root_path = os.environ["USERPROFILE"]

set_number = input("Input the current shoulder press set number: ")
output_file = "../DMP_9D_ACCEL_Logs/shoulder_press/shoulder_press_3_29_shoulder_press" + str(set_number) + ".csv"

selected_device = []

class DataToFile:

    column_names = ["timeMs", "ax", "ay", "az", "q0","q1", "q2", "q3"]

    def __init__(self, write_path):
        self.path = write_path

    def write_to_csv(self, data_values: [Any]):
        with open(self.path, "a+") as f:
            if os.stat(self.path).st_size == 0:
                print("Created file.")
                f.write(",".join([str(name) for name in self.column_names]) + ",\n")
            else:
                f.write(",".join(str(number) for number in data_values[0]) + "\n")

class Connection:
    
    client: BleakClient = None
    
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        read_characteristic: str,
        write_characteristic: str,
        data_dump_handler: Callable[[str, Any], None],
        data_dump_size: int = 20,
    ):
        self.loop = loop
        self.read_characteristic = read_characteristic
        self.write_characteristic = write_characteristic
        self.data_dump_handler = data_dump_handler

        self.last_packet_time = datetime.now()
        self.dump_size = data_dump_size
        self.connected = False
        self.connected_device = None

        self.rx_data = []
        self.rx_timestamps = []
        self.rx_delays = []
        self.sensorstructdata = []

    def on_disconnect(self, client: BleakClient, future: asyncio.Future):
        self.connected = False
        # Put code here to handle what happens on disconnet.
        print(f"Disconnected from {self.connected_device.name}!")

    async def cleanup(self):
        if self.client:
            await self.client.stop_notify(read_characteristic)
            await self.client.disconnect()

    async def manager(self):
        print("Starting connection manager.")
        while True:
            if self.client:
                await self.connect()
            else:
                await self.select_device()
                await asyncio.sleep(15.0)       

    async def connect(self):
        if self.connected:
            return
        try:
            await self.client.connect()
            self.connected = await self.client.is_connected()
            if self.connected:
                print(F"Connected to {self.connected_device.name}")
                self.client.set_disconnected_callback(self.on_disconnect)
                await self.client.start_notify(
                    self.read_characteristic, self.notification_handler,
                )
                while True:
                    if not self.connected:
                        break
                    await asyncio.sleep(3.0)
            else:
                print(f"Failed to connect to {self.connected_device.name}")
        except Exception as e:
            print(e)

    async def select_device(self):
        print("Bluetooh LE hardware warming up...")
        await asyncio.sleep(2.0) # Wait for BLE to initialize.
        devices = await discover()

        print("Please select device: ")
        for i, device in enumerate(devices):
            print(f"{i}: {device.name}")

        response = -1
        while True:
            response = await ainput("Select device: ")
            try:
                response = int(response.strip())
            except:
                print("Please make valid selection.")
            
            if response > -1 and response < len(devices):
                break
            else:
                print("Please make valid selection.")

        print(f"Connecting to {devices[response].name}")
        self.connected_device = devices[response]
        self.client = BleakClient(devices[response].address, loop=self.loop)

    def record_time_info(self):
        present_time = datetime.now()
        self.rx_timestamps.append(present_time)
        self.rx_delays.append((present_time - self.last_packet_time).microseconds)
        self.last_packet_time = present_time

    def clear_lists(self):
        self.rx_timestamps.clear()
        self.rx_delays.clear()
        self.sensorstructdata.clear()

    def notification_handler(self, sender: str, data: Any):
        """Simple notification handler which prints the data received."""
        
        # NOTE:  IT IS CRITICAL THAT THE UNPACK BYTE STRUCTURE MATCHES THE STRUCT
        #        CONFIGURATION SHOWN IN THE ARDUINO C PROGRAM.
        
        # <hh meaning:  <=little endian, h=short (2 bytes), b=1 byte, i=int 4 bytes, unsigned long = 4 bytes

        #Scale factor used in Arduino to convert floats to ints.
        scale=10000

        # Main Sensor struct
        t,ax,ay,az,qw,qx,qy,qz = struct.unpack('<8i', data)

        self.sensorstructdata.append([t,ax,ay,az,qw/scale,qx/scale,qy/scale,qz/scale])

        print(f'timeMs:{t}, accel_x:{ax}, accel_y:{ay}, accel_z={az}, quat_w={qw/scale}, quat_x={qx/scale}, quat_y={qy/scale}, quat_z={qz/scale}')

        self.data_dump_handler(self.sensorstructdata)
        self.record_time_info()
        self.clear_lists()


async def main():
    while True:
        # YOUR APP CODE WOULD GO HERE.
        await asyncio.sleep(5)



#############
# App Main
#############
write_characteristic = ""
read_characteristic = "00001143-0000-1000-8000-00805f9b34fb"

if __name__ == "__main__":

    # Create the event loop.
    loop = asyncio.get_event_loop()

    data_to_file = DataToFile(output_file)
    connection = Connection(
        loop, read_characteristic, write_characteristic, data_to_file.write_to_csv
    )
    try:
        asyncio.ensure_future(connection.manager())
        asyncio.ensure_future(main())
        loop.run_forever()
    except KeyboardInterrupt:
        print()
        print("User stopped program.")
    finally:
        print("Disconnecting...")
        loop.run_until_complete(connection.cleanup())
