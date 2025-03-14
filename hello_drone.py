
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


        self.flight_data = [
            ["Position", "X:", "Y:", "Z:"],  # Headers (Fixed)
            ["Orientation", "Roll:", "Pitch:", "Yaw:"]
        ]

        self.CELL_WIDTH = 180
        self.CELL_HEIGHT = 60
        self.START_X = 10  # Starting position (x)
        self.START_Y = 30  # Starting position (y)
        #define the starting position (top-left corner) for rendering the table on the Pygame window.
        self.WHITE = (255, 255, 255)
        self.GRAY = (128,128,128)
        self.BLACK = (0, 0, 0)
        self.COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Red, Green, Blue
        

  
        

   
    def execute(self,q):
        print("arming the drone...")
        self.client.armDisarm(True)  #Rotate the propellor
        start_pose = self.client.simGetVehiclePose().position
        airsim_start_x = start_pose.x_val
        airsim_start_y = start_pose.y_val

        airsim.wait_key('Press any key to takeoff')
        self.client.takeoffAsync().join()
        start_pose = self.client.simGetVehiclePose().position
        airsim_start_x = start_pose.x_val
        airsim_start_y = start_pose.y_val
        intial_pose = (998.300, 2467, -44.6)
        tank_positions = [
            (952.05094124, 2425.23966258),
            (942.95094124, 2367.83966258),
            (934.11540034, 2307.80857353),
            (925.50094124, 2248.85023421),
            (918.35094124, 2193.88966258)
        ]
        airsim_positions = []
       
        for i, (x, y) in enumerate(tank_positions, start=1):
            x = x - intial_pose[0]
            y = y -  intial_pose[1]
            self.client.moveToPositionAsync(x, y, -30, 8).join()
            print(f"This is tank {i}")
            theta_1_3, theta_2_4 = self.get_theta()
            updated_row = self.update_table(i, max(theta_1_3, theta_2_4))
            


            q.put({
                "updated_row": updated_row,  # Store updated table row
            })
  
    def fight_pose(self,q):
        
        self.pose = self.client.getMultirotorState().kinematics_estimated
        updated_drone_position =self.pose.position
        updated_drone_orientation = self.pose.orientation
        roll,pitch,yaw = airsim.to_eularian_angles(updated_drone_orientation)

        
        q.put({
                "orientation":
                {
                    "roll": roll,
                    "pitch": pitch,
                    "yaw": yaw
                },
                "position": {
                    "x": updated_drone_position.x_val,
                    "y": updated_drone_position.y_val,
                    "z": updated_drone_position.z_val
                }
            })

    def play_alarm(self):
        pygame.mixer.init()
        file_path = r"D:\Robotics Engineering-UniGe\2 anno\First semester\Virtual Reality\Tutorial\Colosseum-main\PythonClient\multirotor\alarm.mp3"
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

    def draw_table(self):
        # Create a smaller, more aesthetic table
        cell_width = 100  # Reduced cell width
        cell_height = 40  # Reduced cell height
        start_x = 20           
        start_y = 20

        # Styling
        header_bg = (81, 67, 168)  # Dark gray for header
        row_gap = 5  # Extra space between rows
        border_radius = 8  # Small curve for edges

        # Function to draw a row with rounded left/right edges only
        def draw_row(y, bg_color, text_data, is_header=False):
            # Full row rect with border_radius for left & right edges
            full_rect = pygame.Rect(start_x, y, cell_width * 3, cell_height)
            pygame.draw.rect(self.screen, bg_color, full_rect, border_radius=border_radius)

            # Overlap a straight rectangle in the middle to remove top/bottom curves
            middle_rect = pygame.Rect(start_x + border_radius, y, (cell_width * 3) - (2 * border_radius), cell_height)
            pygame.draw.rect(self.screen, bg_color, middle_rect)  # No border_radius here

            # Draw text
            for col in range(3):
                text_surface = self.font.render(text_data[col], True, (0,25,51))
                text_rect = text_surface.get_rect(center=(start_x + col * cell_width + cell_width // 2, y + cell_height // 2))
                self.screen.blit(text_surface, text_rect)

        # Draw Header (with curved edges)
        draw_row(start_y, header_bg, self.table_data[0], is_header=True)

        # Draw Data Rows (with curved edges)
        for row in range(1, 6):
            bg_color = (204,229, 255) if row % 2 == 0 else (204, 204, 255)
            row_y = start_y + row * (cell_height + row_gap)  # Adjust row position with gap
            draw_row(row_y, bg_color, self.table_data[row])
    def draw_flight_data_table(self):
        # Create a smaller, more aesthetic table
        cell_width = 105  # Reduced cell width
        cell_height = 20  # Reduced cell height
        start_x = 100           
        start_y = 320

        for row in range(2):
            for col in range(4):
                rect = pygame.Rect(start_x + col * cell_width, start_y + row * cell_height, cell_width, cell_height)
                #pygame.draw.rect(self.screen, self.BLACK, rect, 2) #To create lines (borders) between the rectangles:
                text_surface = self.font.render(self.flight_data[row][col], True, self.WHITE) #This line creates a text image that can be displayed on the screen.
                if col == 0:
                    text_rect = text_surface.get_rect(midleft=rect.midleft)
                else:
                    text_rect = text_surface.get_rect(center=rect.center) #positions the text in the center of the rectangle (table cell).
                self.screen.blit(text_surface, text_rect) #displays the text on the screen 

    def draw_gauge(self): 
        # Position the gauge on the right side
        gauge_center_x = 635 - 190 #self.WIDTH - 150
        gauge_center_y = self.HEIGHT // 2
        radius = 80
        
        # Function to draw a filled arc section
        def draw_filled_arc(color, start_angle, end_angle):
            points = [(gauge_center_x, gauge_center_y)]  # Start with center point

            # Add points along the arc
            for i in range(21):  # More points = smoother arc
                angle = -start_angle + (-end_angle + start_angle) * (i / 20)
                x = gauge_center_x + radius * math.cos(angle)
                y = gauge_center_y + radius * math.sin(angle)
                points.append((x, y))

             # Draw the filled polygon
            pygame.draw.polygon(self.screen, color, points)

            # Draw the colored sections as filled arcs
            # Green section (0-5 degrees)
        draw_filled_arc((0, 200, 0), math.pi - math.pi/3, math.pi)

            # Yellow section (5-10 degrees)
        draw_filled_arc((255, 255, 0), math.pi - 2*math.pi/3, math.pi - math.pi/3)
            # Red section (10-15 degrees)
        draw_filled_arc((255, 0, 0), 0, math.pi - 2*math.pi/3)

        # Draw the gauge markings
        self.draw_gauge_markings(gauge_center_x, gauge_center_y, radius)
    
        # Draw the gauge needle for the current value (for demonstration)
        # For actual use, you'd use the current tank's theta value
        current_theta = 0  # Default value
        # Get the current tank's theta value if available
        for row in self.table_data[1:]: #Exclude Header and Start from the Tank ID 1
            if row[2] != "0": #This checks the last column of the table
                try:
                    current_theta = float(row[1])
                    break
                except ValueError:
                    pass
    
        # Calculate angle for the needle
        if current_theta > 15:
            current_theta = 15  # Cap at max value
        needle_angle = 0 + (current_theta / 15) * math.pi
        needle_length = radius - 10
    
        # Draw needle
        end_x = gauge_center_x - needle_length * math.cos(needle_angle)
        end_y = gauge_center_y - needle_length * math.sin(needle_angle)
        pygame.draw.line(self.screen, (255, 255, 255), (gauge_center_x, gauge_center_y), 
                        (end_x, end_y), 3)
    
        # Draw center circle
        pygame.draw.circle(self.screen, (100, 100, 100), (gauge_center_x, gauge_center_y), 5)
    
        # Draw legend
        legend_y = gauge_center_y + 10
        font = pygame.font.Font(None, 18)
    
        # Draw the legend
        pygame.draw.rect(self.screen, (0, 200, 0), (gauge_center_x - 70, legend_y, 15, 15))
        text = font.render("Safe", True, self.BLACK)
        self.screen.blit(text, (gauge_center_x - 50, legend_y))
    
        pygame.draw.rect(self.screen, (255, 255, 0), (gauge_center_x - 70, legend_y + 20, 15, 15))
        text = font.render("First Alarm", True, self.BLACK)
        self.screen.blit(text, (gauge_center_x - 50, legend_y + 20))
    
        pygame.draw.rect(self.screen, (255, 0, 0), (gauge_center_x - 70, legend_y + 40, 15, 15))
        text = font.render("Danger", True, self.BLACK)
        self.screen.blit(text, (gauge_center_x - 50, legend_y + 40))
    
        # Draw title
        title_font = pygame.font.Font(None, 32)
        title = title_font.render("Inclination", True, self.BLACK)
        self.screen.blit(title, (gauge_center_x - 50, gauge_center_y - radius - 40))

    def draw_gauge_markings(self, center_x, center_y, radius):
            # Draw tick marks and labels
        font = pygame.font.Font(None, 24)
    
        # Major ticks at 0, 5, 10, 15
        for i in range(4):
            angle = math.pi + (i * math.pi / 3)
            outer_x = center_x + radius * math.cos(angle)
            outer_y = center_y + radius * math.sin(angle)
            inner_x = center_x + (radius - 10) * math.cos(angle)
            inner_y = center_y + (radius - 10) * math.sin(angle)
        
            # Draw tick mark
            pygame.draw.line(self.screen, self.BLACK, (inner_x, inner_y), (outer_x, outer_y), 2)
        
            # Draw label
            label = str(i * 5)
            label_surface = font.render(label, True, self.BLACK)
            label_x = center_x + (radius + 15) * math.cos(angle) - label_surface.get_width() / 2
            label_y = center_y + (radius + 15) * math.sin(angle) - label_surface.get_height() / 2
            self.screen.blit(label_surface, (label_x, label_y))

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
        self.WIDTH, self.HEIGHT = 570, 365  # Window size
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Tank Inclination Monitor")
       
        self.font = pygame.font.Font(None, 24)
        running = True

        while running:
            self.screen.fill(self.GRAY)  # Clear screen
            self.fight_pose(q)
            
            self.update_table_from_queue(q)
            self.draw_table()  # Draw the compact table
            self.draw_gauge()  # Draw the semi-circular gauge
            self.draw_flight_data_table()
            pygame.display.flip()  # Refresh display

 
            # Handle quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
 
        pygame.quit()
        sys.exit()
    def update_table_from_queue(self, q):
        while not q.empty():
            data = q.get()
        
            # Check if this data has updated_row info
            if "updated_row" in data:
                updated_row = data["updated_row"]
                tank_id, inclination, risk_level = updated_row
                self.table_data[tank_id][1] = inclination
                self.table_data[tank_id][2] = risk_level
            
            # Check if this data has position and orientation info
            if "position" in data and "orientation" in data:
                self.flight_data[0][1] = f"X: {data['position']['x']:.2f}"
                self.flight_data[0][2] = f"Y: {data['position']['y']:.2f}"
                self.flight_data[0][3] = f"Z: {data['position']['z']:.2f}"
                self.flight_data[1][1] = f"\u03C6: {data['orientation']['roll']:.2f}"
                self.flight_data[1][2] = f"θ: {data['orientation']['pitch']:.2f}"
                self.flight_data[1][3] = f"ψ: {data['orientation']['yaw']:.2f}"


 
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