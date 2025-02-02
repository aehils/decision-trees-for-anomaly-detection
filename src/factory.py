import os
import asyncio
import signal
import sys
from threading import Thread
from enum import Enum
import logging

import numpy as np
from opcua import ua, Server
from opcua import Client, ua
import inquirer
import math
import random
import time
import socket
import json
import threading

import csv
import datetime

from recipe import RobotPosition, recipe_data, Recipe, get_enum_by_value

logging.basicConfig(level=logging.WARN)
# OPCUA server address
SERVER_ENDPOINT = "opc.tcp://localhost:4841/freeopcua/server/"

# The minimum log level to be recorded (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOGGING_LEVEL = logging.INFO

# OPCUA object details
OBJECT_NAME = "MyObject"
NAMESPACE_URI = "http://examples.freeopcua.github.io"

# Initialize variables
counter = 10

# sleep durations
sleep_duration = [4, 8, 5]

# variables for anomaly
anomaly_coordinates = [None, None, None]
anomaly_sleep_durations = [None, None, None]

# current position of the robot
current_position = RobotPosition.IDLE

# current recipe and process state
recipe = "--NA--"
process_state_value = False
stop_flag = False

server = Server()
server.set_endpoint(SERVER_ENDPOINT)
    # Setup namespace
uri = NAMESPACE_URI
server_idx = server.register_namespace(uri)
# Get objects node
objects = server.get_objects_node()
   # Create new object
myobject = objects.add_object(server_idx, OBJECT_NAME)


def handle_client(client_socket):
    global anomaly_coordinates, anomaly_sleep_durations
    data = client_socket.recv(1024)
    data_json = json.loads(data)
    if data_json.get('anomaly_coordinates', anomaly_coordinates):
        anomaly_coordinates = data_json.get('anomaly_coordinates', anomaly_coordinates)
        print(f"Received {anomaly_coordinates=}")
    if data_json.get('anomaly_sleep_durations', anomaly_sleep_durations):
        anomaly_sleep_durations = data_json.get('anomaly_sleep_durations', anomaly_sleep_durations)
        print(f"Received {anomaly_sleep_durations=}")
    client_socket.close()


def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 9999))
    server.listen(5)

    print("Listening on localhost:9999")

    while True:
        client, addr = server.accept()
        print("Accepted connection from: %s:%d" % (addr[0], addr[1]))
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    global stop_flag
    stop_flag = True
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


# All stages combined
def forward_kinematics_simulation(joint_angles):
    """
    Convert joint angles into a simple representation of an end effector position.

    This function assumes each joint contributes to the position equally,
    which is not the case for a real 6 DOF robot arm, but will serve for this simulation.

    Arguments:
    joint_angles -- a 6-element list-like object containing the angles for each joint in degrees.

    Returns:
    A tuple containing the X, Y, Z position of the end effector.
    """
    joint_angles = np.deg2rad(np.array(joint_angles))  # Convert to radians

    # The position is simply the sum of the joint angles, treating them as if they are spherical coordinates
    r = np.sum(
        joint_angles)  # In a real arm, this might be the length of the arm segments or some function of the joint angles
    theta = joint_angles[1]  # Polar angle, just choose one of the angles for simplicity
    phi = joint_angles[2]  # Azimuthal angle, again just choose one of the angles for simplicity

    # Convert from spherical to Cartesian coordinates
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)

    return x, y, z

def initialize_variables(myobject, server_idx):
    return {
        'robot_vars': [
            myobject.add_variable(server_idx, "ArmX", 0.0),
            myobject.add_variable(server_idx, "ArmY", 0.0),
            myobject.add_variable(server_idx, "ArmZ", 0.0),
        ],
        'joint_vars': [
            myobject.add_variable(server_idx, "Joint1Angle", 0),
            myobject.add_variable(server_idx, "Joint2Angle", 0),
            myobject.add_variable(server_idx, "Joint3Angle", 0),
            myobject.add_variable(server_idx, "Joint4Angle", 0),
            myobject.add_variable(server_idx, "Joint5Angle", 0),
            myobject.add_variable(server_idx, "Joint6Angle", 0),
        ],
        'robot_state': myobject.add_variable(server_idx, "robot_state", "idle"),
        'oven_state': myobject.add_variable(server_idx, "oven_state", "idle"),
        'proximity_sensor': myobject.add_variable(server_idx, "ProximitySensor", False),
        'gripper_state': myobject.add_variable(server_idx, "VacuumGripperState", False),
        'gripper_force': myobject.add_variable(server_idx, "GripperForce", 0),
        'process_state': myobject.add_variable(server_idx, "ProcessState", False),
        'recipe': myobject.add_variable(server_idx, "Recipe", "--NA--"),
    }
    


def initialize_csv():
    try:
        with open('operation_log.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Robot State", "Robot Position X", "Robot Position Y", "Robot Position Z", "Proximity Sensor",
                            "Gripper State"])
    except Exception as e:
        print("Failed to initialize CSV file:", e)

def log_data(variables):
    log_file_path = 'operation_log.csv'
    try:
        with open(log_file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                variables['robot_state'].get_value(),
                variables['robot_vars'][0].get_value(),
                variables['robot_vars'][1].get_value(),
                variables['robot_vars'][2].get_value(),
                variables['proximity_sensor'].get_value(),
                variables['gripper_state'].get_value(),
        ])
    except IOError as e:
        # Handle error in case file can't be accessed or opened
        print(f"Error opening or writing to file: {e}") 
        
async def update_robot_positions(robot_vars, joint_vars):
    prev_state = None
    counter_idx = 0
    global recipe
    variables = initialize_variables(myobject,server_idx)
    while not stop_flag:
        current_state = current_position
        if recipe == '--NA--' or recipe is None or current_position == RobotPosition.IDLE:
            for idx, angle in enumerate([0, 0, 0, 0, 0]):
                joint_vars[idx].set_value(angle)
                await asyncio.sleep(0.3)
            continue
        print(f"{current_position=}")
        angles = recipe_data[recipe][current_state]['angles'][counter_idx]
        for idx, angle in enumerate(angles):
            joint_vars[idx].set_value(angle)
        # log_data(variables)

        x, y, z = forward_kinematics_simulation(angles)
        if anomaly_coordinates[0]:
            robot_vars[0].set_value(anomaly_coordinates[0])
        else:
            robot_vars[0].set_value(x)
        # log_data(variables)
        if anomaly_coordinates[1]:
            robot_vars[1].set_value(anomaly_coordinates[1])
        else:
            robot_vars[1].set_value(y)
        # log_data(variables)
        if anomaly_coordinates[2]:
            robot_vars[2].set_value(anomaly_coordinates[2])
        else:
            robot_vars[2].set_value(z)
        log_data(variables)
        counter_idx += 1
        await asyncio.sleep(0.3)
        if current_state != prev_state or counter_idx > 9:
            counter_idx = 0
        prev_state = current_state


async def update_values(server, variables):
    asyncio.create_task(update_robot_positions(variables['robot_vars'], variables['joint_vars']))
    global current_position
    global recipe
    robot_actions = None
    prev_state = None
    prev_recipe = None
    while not stop_flag:
        log_data(variables)
        if variables['process_state'].get_value():
            recipe_str = variables['recipe'].get_value()
            print(f"{recipe_str=}")
            recipe = get_enum_by_value(recipe_str)
            if recipe != prev_recipe:
                robot_actions = [RobotPosition.PICK_FROM_CONVEYOR,
                                 RobotPosition.PLACE_IN_OVEN,
                                 RobotPosition.PICK_FROM_OVEN,
                                 RobotPosition.PLACE_IN_CONVEYOR,
                                 RobotPosition.MOVE_TO_REST]
                prev_recipe = recipe
            print(recipe)
            if recipe != '--NA--' and recipe is not None:
                for idx, state in enumerate(robot_actions):
                    log_data(variables)
                    current_position = state
                    if prev_state != state:
                        if state == RobotPosition.PICK_FROM_CONVEYOR:
                            """ simulating when object is available in the conveyor, it triggers the pick"""
                            variables['proximity_sensor'].set_value(True)
                            log_data(variables)
                            variables['proximity_sensor'].set_value(False)
                            log_data(variables)
                        variables['robot_state'].set_value(state.value)
                        sleep_dur = recipe_data[recipe][state]['sleep_duration']
                        if state == RobotPosition.PICK_FROM_CONVEYOR or state == RobotPosition.PICK_FROM_OVEN:
                            variables['gripper_state'].set_value(True)
                            log_data(variables)
                            variables['gripper_force'].set_value(recipe_data[recipe]['gripper_force'])
                        await asyncio.sleep(sleep_dur)
                        if state == RobotPosition.PICK_FROM_CONVEYOR or state == RobotPosition.PICK_FROM_OVEN:
                            variables['gripper_state'].set_value(False)
                            log_data(variables)
                            variables['gripper_force'].set_value(0)
                        if state == RobotPosition.PLACE_IN_OVEN:
                            variables['oven_state'].set_value("ON")
                            variables['gripper_force'].set_value(recipe_data[recipe]['heating_duration'])
                            await asyncio.sleep(recipe_data[recipe]['heating_duration'])
                            variables['oven_state'].set_value("OFF")
                    prev_state = state
                    log_data(variables)
            else:
                variables['robot_state'].set_value(RobotPosition.IDLE.value)
                current_position = RobotPosition.IDLE
                await asyncio.sleep(sleep_duration[2])
            log_data(variables)
        else:
            print(f"idle........................")
            variables['robot_state'].set_value(RobotPosition.IDLE.value)
            current_position = RobotPosition.IDLE
            await asyncio.sleep(sleep_duration[2])
        
async def periodic_log(variables, interval=0.5):
    """ Log data at fixed intervals regardless of state changes. """
    while not stop_flag:
        log_data(variables)
        await asyncio.sleep(interval)

def main():
    #intialise CSV
    initialize_csv()

    # Start the TCP server in a separate thread
    tcp_server_thread = threading.Thread(target=start_tcp_server)
    tcp_server_thread.start()

    """Entry point of the program."""
    logging.basicConfig(level=LOGGING_LEVEL)

    
    variables = initialize_variables(myobject,server_idx)
    for var in variables['robot_vars']:
        var.set_writable()
    for var in variables['joint_vars']:
        var.set_writable()
    variables['robot_state'].set_writable()
    variables['oven_state'].set_writable()
    variables['proximity_sensor'].set_writable()
    variables['gripper_state'].set_writable()
    variables['gripper_force'].set_writable()
    variables['process_state'].set_writable()
    variables['recipe'].set_writable()

    # Starting!
    server.start()

    logging.info(f"Server started at {SERVER_ENDPOINT}")

    try:
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(periodic_log(variables))
        loop.run_until_complete(update_values(server, variables))
    finally:
        server.stop()
        logging.info("Server stopped")


if __name__ == "__main__":
    main()
