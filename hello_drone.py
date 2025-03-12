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

import sys
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

        #pygame intialisation
        
           
        self.table_data = [
            ["Tank ID", "Inclination", "Risk Level"],  # Headers (Fixed)
            ["Tank 1", "0", "0"],
            ["Tank 2", "0", "0"],
            ["Tank 3", "0", "0"],
            ["Tank 4", "0", "0"],
            ["Tank 5", "0", "0"]
        ]

        self.CELL_WIDTH = 180
        self.CELL_HEIGHT = 60
        self.START_X = 10  # Starting position (x)
        self.START_Y = 30  # Starting position (y)
        #define the starting position (top-left corner) for rendering the table on the Pygame window.
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        

   
    def execute(self,q):
        print("arming the drone...")
        self.client.armDisarm(True)  #Rotate the propellor
        airsim.wait_key('Press any key to takeoff')
        self.client.takeoffAsync().join()
        tank_positions = [
            (47.641200, -122.140910),
            (47.641150, -122.141690),
            (47.641150, -122.142460),
            (47.641150, -122.143200),
            (47.641150, -122.143900)
        ]
        for i, (lat, lon) in enumerate(tank_positions, start=1):
            self.client.moveToGPSAsync(lat, lon, 200, 8).join()
            print(f"This is tank {i}")
            theta_1_3, theta_2_4 = self.get_theta()
            updated_row = self.update_table(i, max(theta_1_3, theta_2_4))
            q.put(updated_row)
  
        print(self.client.getGpsData())

    def play_alarm(self):
        pygame.mixer.init()
        file_path = r"D:\Robotics Engineering-UniGe\2 anno\First semester\Virtual Reality\Tutorial\Colosseum-main\PythonClient\multirotor\alarm.mp3"
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

    def draw_table(self):
        
        for row in range(6):
            for col in range(3):
                rect = pygame.Rect(self.START_X + col * self.CELL_WIDTH, self.START_Y + row * self.CELL_HEIGHT, self.CELL_WIDTH, self.CELL_HEIGHT)
                pygame.draw.rect(self.screen, self.BLACK, rect, 2) #To create lines (borders) between the rectangles:
                text_surface = self.font.render(self.table_data[row][col], True, self.BLACK) #This line creates a text image that can be displayed on the screen.
                text_rect = text_surface.get_rect(center=rect.center) #positions the text in the center of the rectangle (table cell).
                self.screen.blit(text_surface, text_rect) #displays the text on the screen 
                
    def update_table(self, tank_id, theta):
        risk_level = "Low" if theta < 0.1 else "Medium" if theta < 0.2 else "High"
        self.table_data[tank_id][1] = f"{theta:.2f}"
        self.table_data[tank_id][2] = risk_level

        #print(f"Updated Tank {tank_id}: Inclination = {theta:.2f}, Risk Level = {risk_level}")
        #print(self.table_data)
        return [tank_id, f"{theta:.2f}", risk_level]
    


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
        return theta_1_3, theta_2_4



    def run(self,q):
        """Runs the Pygame window with dynamic table updates."""
        pygame.init()
        self.WIDTH, self.HEIGHT = 600, 400  # Window size
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Data")
       
        self.font = pygame.font.Font(None, 40)
        running = True

        while running:
            self.screen.fill(self.WHITE)  # Clear screen
            self.update_table_from_queue(q)
            self.draw_table()  # Draw the updated table
            pygame.display.flip()  # Refresh display
 
            # Handle quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
 
        pygame.quit()
        sys.exit()

    def update_table_from_queue(self, q):
        while not q.empty():
            tank_id, inclination, risk_level = q.get()
            self.table_data[tank_id][1] = inclination
            self.table_data[tank_id][2] = risk_level
 
    def thermal_camera(self):
        while True:
            responses = self.client.simGetImages([airsim.ImageRequest("thermal_camera", airsim.ImageType.Scene, False, False)])
            if responses and responses[0].image_data_uint8:
                thermal_image = np.frombuffer(responses[0].image_data_uint8, dtype=np.uint8)
                thermal_image = thermal_image.reshape(responses[0].height, responses[0].width, 3)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Exiting thermal camera")
                    break

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
                cv2.namedWindow("Oil Leak Detection", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Oil Leak Detection", 640, 480)
                cv2.imshow("Oil Leak Detection", thermal_image_copy)

                


                
                self.client.simSetSegmentationObjectID("thermal_camera", 5, True)


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
def execute_p2(q):
    lidar_test = LidarTest()
    lidar_test.execute(q)
def draw_table_p3(q):
    lidar_test = LidarTest()
    lidar_test.run(q)
       
 
 
# main
if __name__ == "__main__":
    q = multiprocessing.Queue()

    p1 = multiprocessing.Process(target=thermal_camera_p1)
    p2 = multiprocessing.Process(target=execute_p2, args=(q,))
    p3 = multiprocessing.Process(target=draw_table_p3, args=(q,))
    try:
        p1.start()
        p2.start()
        p3.start()
        p1.join()
        p2.join()
        p3.join()
    finally:
        lidar_test = LidarTest()
        print("Stopping the drone")
        lidar_test.stop()