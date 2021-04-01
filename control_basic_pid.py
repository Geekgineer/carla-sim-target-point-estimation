
#!/usr/bin/env python

# Copyright (c) 2018 Intel Labs.
# authors: German Ros (german.ros@intel.com)
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""Example of automatic vehicle control from client side."""

from __future__ import print_function

import argparse
import collections
import datetime
import glob
import logging
import math
import os
import random
import re
import sys
import weakref


try:
    import pygame
    from pygame.locals import KMOD_CTRL
    from pygame.locals import K_ESCAPE
    from pygame.locals import K_q
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
    import numpy as np
except ImportError:
    raise RuntimeError(
        'cannot import numpy, make sure numpy package is installed')

# ==============================================================================
# -- Find CARLA module ---------------------------------------------------------
# ==============================================================================
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

# ==============================================================================
# -- Add PythonAPI for release mode --------------------------------------------
# ==============================================================================
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/carla')
except IndexError:
    pass

import carla

# ==============================================================================
# -- mc_args -------------------------------------------------------------
# ==============================================================================

#Start CARLA world 


class mc_args(object):
    def __init__(self):
        self.debug = True
        self.host = '127.0.0.1'
        self.port = 2000
        self.autopilot = True  # True
        self.width =  460  # 1280
        self.height = 360   # 720
args = mc_args()

client = carla.Client(args.host, args.port)
client.set_timeout(20)
client.load_world("Town04")
client.reload_world()

road_id = 10

world =client.get_world()


#run the simulation at a fixed time-step of 0.05 seconds (20 FPS) apply the following settings

# settings = world.get_settings()
# settings.fixed_delta_seconds = 0.05
# world.apply_settings(settings)



# Get the world waypoints and draw it

def draw_waypoints(waypoints, road_id=None, life_time=50.0):

  for waypoint in waypoints:

    if(waypoint.road_id == road_id):
        world.debug.draw_string(waypoint.transform.location, 'O', draw_shadow=False,
                                   color=carla.Color(r=0, g=255, b=0), life_time=life_time,
                                   persistent_lines=True)

                                   
waypoints = world.get_map().generate_waypoints(distance=1.0)
draw_waypoints(waypoints, road_id=road_id , life_time=20)


# Spawning a vehicle in CARLA
vehicle_blueprint = world.get_blueprint_library().filter('model3')[0]


filtered_waypoints = []
for waypoint in waypoints:
    if(waypoint.road_id == road_id):
      filtered_waypoints.append(waypoint)


spawn_point = filtered_waypoints[0].transform
spawn_point.location.z += 2
vehicle = world.spawn_actor(vehicle_blueprint, spawn_point)


# Controlling the spawned car

from agents.navigation.controller import VehiclePIDController
custom_controller = VehiclePIDController(vehicle, args_lateral = \
                    {'K_P': 1, 'K_D': 0.01, 'K_I': 0.01}, args_longitudinal = {'K_P': 1, 'K_D': 0.01, 'K_I': 0.01})


target_waypoint = filtered_waypoints[20]

# print(target_waypoint.transform.location)

world.debug.draw_string(target_waypoint.transform.location, 'O', draw_shadow=False,
                           color=carla.Color(r=255, g=0, b=0), life_time=50,
                           persistent_lines=True)


ticks_to_track = 20
target_speed_th = 5

for i in range(ticks_to_track):
	control_signal = custom_controller.run_step(target_speed_th, target_waypoint)
	vehicle.apply_control(control_signal)
	print(control_signal)



