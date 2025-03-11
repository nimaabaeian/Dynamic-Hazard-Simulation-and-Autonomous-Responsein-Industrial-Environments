# Python client example to get Lidar data from a drone
 
#
 
import setup_path
import airsim

 
import math
import time 
import argparse
import pprint
import numpy
import numpy as np


import cv2
import multiprocessing

import pygame

 
 
# Makes the drone fly and get Lidar data
 
class LidarTest:
 
    def __init__(self):
 
        # connect to the AirSim simulator
 
        self.client = airsim.MultirotorClient()
 
        self.client.confirmConnection()
 
        self.client.enableApiControl(True)
 
        #self.origingps = self.client.getGpsData()
 
 
        # tasks waypoints
 
        self.wp1=(44.582410,8.941121,115)
 
        self.wp2=(44.582922,8.941083,20)
 
        self.wp3=(44.583430,8.941121,15)
 
   
    def execute(self):
 
        print("arming the drone...")
 
        self.client.armDisarm(True)  #Rotate the propellor
 
        #state = self.client.getMultirotorState()
 
        #s = pprint.pformat(state)
 
        #print("state: %s" % s)

        #self.client.simSetSubWindowSettings(1, 0.7, 0.1, 0.3, 0.3)
        #self.client.simSetSubWindowCamera(1,"thermal_camera",0)
        #self.client.simSetSubWindowVisible(1,True)
 
        airsim.wait_key('Press any key to takeoff')
 
        self.client.takeoffAsync().join()

        
        
 
        self.client.moveToGPSAsync(47.641200,-122.140910,130.887,8).join()
        print("This is the first container")
        #self.client.hoverAsync().join()
        #time.sleep(1)

        #self.thermal_camera()
 
        self.client.moveToGPSAsync(47.641150,-122.141690,130.887,8).join()
        print("This is the second container")
        #self.thermal_camera()
        #self.client.hoverAsync().join()
        #time.sleep(1)
        sensor_data = self.client.getDistanceSensorData("Distance_1")  
        self.get_theta()
        self.play_alarm()

 
        self.client.moveToGPSAsync(47.641150,-122.142460,130.887,8).join()
        print("This is the third container")
        #self.thermal_camera()
        #time.sleep(1)

        self.client.moveToGPSAsync(47.641150,-122.143200,130.887,5).join()
        print("This is the fourth container")
        #self.thermal_camera()
        #time.sleep(1)

        self.client.moveToGPSAsync(47.641150,-122.143900,130.887,5).join() 
        print("This is the fifth container")
        #self.thermal_camera()
 
        time.sleep(3)
 
        #print(self.origingps.gnss.geo_point.latitude,self.origingps.gnss.geo_point.longitude,self.origingps.gnss.geo_point.altitude)
 
        print(self.client.getGpsData())

    def play_alarm(self):
        pygame.mixer.init()
        file_path = r"D:\Robotics Engineering-UniGe\2 anno\First semester\Virtual Reality\Tutorial\Colosseum-main\PythonClient\multirotor\alarm.mp3"
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()


 
    def get_theta(self):
         
        sensor_data_1 = self.client.getDistanceSensorData("Distance_1")
        (x_1, y_1) = (sensor_data_1.relative_pose.position.x_val, sensor_data_1.relative_pose.position.y_val)
        sensor_data_3 = self.client.getDistanceSensorData("Distance_3")
        (x_3, y_3) = (sensor_data_3.relative_pose.position.x_val, sensor_data_3.relative_pose.position.y_val)
        diff_1 = abs(sensor_data_1.distance - sensor_data_3.distance) #Height
        hyp_1_3 = math.sqrt((x_1 - x_3)**2 + (y_1 - y_3)**2) #Hyptenuse
        theta_1_3 = math.asin(diff_1/hyp_1_3) 

        sensor_data_2 = self.client.getDistanceSensorData("Distance_2")
        (x_2, y_2) = (sensor_data_2.relative_pose.position.x_val, sensor_data_2.relative_pose.position.y_val)
        sensor_data_4 = self.client.getDistanceSensorData("Distance_4")
        (x_4, y_4) = (sensor_data_4.relative_pose.position.x_val, sensor_data_4.relative_pose.position.y_val)
        diff_2 = abs(sensor_data_2.distance - sensor_data_4.distance) #Height
        hyp_2_4 = math.sqrt((x_2 - x_4)**2 + (y_2 - y_4)**2) #Hyptenuse
        theta_2_4 = math.asin(diff_2/hyp_2_4)
        print (theta_1_3, theta_2_4)
        #return (theta_1_3, theta_2_4)





 
    def thermal_camera(self):
        """Capture thermal images for 10 seconds."""
        #end_time = time.time() + 10  # Set the time for 10 seconds from now
        while True:
            responses = self.client.simGetImages([airsim.ImageRequest("thermal_camera", airsim.ImageType.Scene, False, False)])
            if responses and responses[0].image_data_uint8:
                thermal_image = np.frombuffer(responses[0].image_data_uint8, dtype=np.uint8)
                thermal_image = thermal_image.reshape(responses[0].height, responses[0].width, 3)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Exiting thermal camera")
                    break

                #thermal_image_resized = cv2.resize(thermal_image, (640, 480))
                # Show the image
                thermal_image_copy = thermal_image.copy()
                hsv_image = cv2.cvtColor(thermal_image, cv2.COLOR_BGR2HSV)
                lower_oil = np.array([0, 0, 0])
                upper_oil = np.array([180, 255, 100])
                oil_mask = cv2.inRange(hsv_image, lower_oil, upper_oil)
                kernel = np.ones((5, 5), np.uint8)
                oil_mask = cv2.morphologyEx(oil_mask, cv2.MORPH_CLOSE, kernel)
                oil_mask = cv2.morphologyEx(oil_mask, cv2.MORPH_OPEN, kernel)
                contours, _ = cv2.findContours(oil_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    if cv2.contourArea(contour) > 500:
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.rectangle(thermal_image_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
                #cv2.namedWindow("Oil Leak Detection", cv2.WINDOW_NORMAL)
                #cv2.resizeWindow("Oil Leak Detection", 640, 480)
                #cv2.imshow("Oil Leak Detection", thermal_image_copy)

                


                
                self.client.simSetSegmentationObjectID("thermal_camera", 5, True)

                #self.client.simSetTextureFromImage("thermal_camera", thermal_image_copy)

            else:
                print("Error: Could not retrieve thermal image")
        
 
    def stop(self):
 
        airsim.wait_key('Press any key to reset to original state')
 
        self.client.armDisarm(False)
 
        self.client.reset()
 
        self.client.enableApiControl(False)
 
        print("Done!\n")
 
def thermal_camera_p1():
    lidar_test = LidarTest()
    lidar_test.thermal_camera()
def execute_p2():
    lidar_test = LidarTest()
    lidar_test.execute()

# main
 
if __name__ == "__main__":
  
    p1 = multiprocessing.Process(target=thermal_camera_p1)
    p2 = multiprocessing.Process(target=execute_p2)
 
    try:
        p1.start()
        p2.start()
        p1.join()
        p2.join()
    finally:
        lidar_test = LidarTest()
        print("Stopping the drone")
        lidar_test.stop()
 