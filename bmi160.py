#!/usr/bin/env python3
from time import sleep
from BMI160_i2c import Driver
import math


class gyro():
	def __init__(self):
		print('Trying to initialize the sensor...')
		self.sensor = Driver(0x69) # change address if needed
		print('Initialization done')
		self.pitch = 0
		self.roll = 0
		self.yaw = 0
	def getData(self):
		data = self.sensor.getMotion6()
		# fetch all gyro and acclerometer values
		gx = data[0]
		gy = data[1]
		gz = data[2]
		ax = data[3]
		ay = data[4]
		az = data[5]

		self.pitch = math.atan2(ax,math.sqrt(ay*ay+az*az))
		self.roll = math.atan2(ay,math.sqrt(ax*ax+az*az))
		self.yaw = math.atan2(ay,math.sqrt(gx*gx+gz*gz))

		self.pitch = self.pitch*180.0/math.pi
		self.roll = self.roll*180.0/math.pi
		self.yaw = self.yaw*180.0/math.pi	

		return self.pitch,self.roll,self.yaw		
	
	def printData(self):
		print({'pitch' :round(self.pitch,3),
		'roll' :round(self.roll,3),
		'yaw' :round(self.yaw,3)

		})
		  

