# Dynamic Hazard Simulation and Autonomous Response in Industrial Environments (IPLOM Oil refinery)
---
## Project description
This project presents the design of the IPLOM oil refinery industrial area, including the simulation of the refinery with floating roof storage tanks, pipelines, and containment zones.

A dynamic system is implemented to track the movement of the floating storage tank roof during the inflow and outflow of oil. A UAV (Unmanned Aerial Vehicle) follows predefined flight paths to detect roof inclination and identify any other potential anomalous situations. It provides real-time feedback, enabling continuous adjustments to monitoring strategies during the simulation.

Additionally, the project includes the development of a UGV (Unmanned Ground Vehicle) that can communicate in real-time with the UAV

---
## Tools
### Unreal Engine 5.2
Unreal Engine 5.2 was the primary tool for creating the environment, modeling the landscape, and integrating various systems, such as the floating roof tanks, UAV, and UGV. 
### AirSim
AirSim is a plugin for Unreal Engine used to simulate UAVs or UGVs in the Unreal Engine environment. It is provided by Microsoft but was forked to Colosseum for the latest versions of Unreal Engine. For Unreal Engine 5.2, it can be obtained from the [Colosseum GitHub repository](https://github.com/CodexLabsLLC/Colosseum) main branch.
### Blender 4.3
Blender 4.3 was used to model custom assets, such as the containment barriers, which were missing from the available asset packs. These assets were then integrated into the Unreal Engine environment to complete the refinery setup. It was also used to obtain the raw version of the Unmanned Ground Vehicle(UGV) model and export it to UE's specifications.

---
## Installation and Procedure
### UAV
- Install Visual Studio Community 2022 along with necessary components, including Desktop Development with C++, the Windows 11 SDK, and the latest .NET Framework SDK
- Clone the AirSim
```bash
git clone https://github.com/CodexLabsLLC/Colosseum.git
```
- Build AirSim in Developer Command Prompt for VS 2022
```bash
dir your_directory/Colosseum
```
```bash
build.cmd
```
- Create a C++ Unreal Engine project
- Copy the Plugin from your_directory/unreal/AirSim to your_project folder
- Modify the Python Client and JSON File
- Create a Python environment setup
- Use the multiprocessing Python module for real-time data processing
 ### UGV
The UGV was used to demonstrate real-time communication and coordination with the UAV 
- Add the UGV model to the Unreal Engine project
- Create the Spline Blueprint
- Create the Rover (UGV) Blueprint
### Real-time Communication
- Enable the OSC plugin to create a UDP socket server with a specific name, IP address, and port number that helps the real-time communication between UAV and UGV.
## Result
### Cinematic Graphic view of the environment
https://github.com/user-attachments/assets/60b22580-89cb-4d7a-ab49-d0d0461e9d55
### Control Widget of the environment
https://github.com/user-attachments/assets/edff99fe-8463-43d5-9d90-60f9e2354e8b
### From the UAV Perspective
https://github.com/user-attachments/assets/07fb9748-cbe4-4483-9443-df15e597bc39
### From the UGV Perspective
https://github.com/user-attachments/assets/0ceb7702-e05e-436e-bd82-d73ab061bf58


