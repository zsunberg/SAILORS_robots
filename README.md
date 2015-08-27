# SAILORS_robots

Code for controlling Pololu m3pi robots for the SAILORS summer program.

The code for the project includes

1. Python class for a robot, with all helper functions such as turn_left_motor, turn_right_motor, stop, forward, get_sensor_readings, etc. This is in sailorsbot.py.

2. Communication infrastructure: Each robot is equipped with an XBee WIFI module, which routes serial communication over a WIFI network. We wrote functions in Python that would communicate with a robot using TCP over the WIFI network at 10 Hz (I think) and relay commands (mentioned above) to the robot, which then parses the commands and executes them. The laptop side of this code is included at the end of sailorsbot.py.

3. The robot firmware: Each robot is controlled by an MBED module, which conveniently has an online IDE/compiler so we don't need to install special software to write code for it. The code is written in C, and the students used this online interface to write the PID controller that would allow the robot to follow a line. We wrote the code that did everything else (communication, interrupts, etc.). This is available at [https://developer.mbed.org/users/zsunberg/code/SAILORSbot/]

4. Graph visualization: We wrote Python code that would take a definition file for a graph, load it into memory, and output a visualization of the graph. The code also contains helper functions such as converting a list of nodes into a sequence of turns, etc. The students were able to import this package and add their Dijkstra's implementation directly to make everything work. This is contained in sailorsmap.py.

5. Data streaming from Motion capture: We didn't get into this as much as we wanted to. We have a Vicon motion capture system in our lab, which can track multiple objects (robots) to sub-millimeter accuracy. We wrote code that would detect robots in the environment, and broadcast the positions of the robots onto the WIFI network. On the laptop, we would then be able to receive this information about other robots, find the nearest edge to the robot, and delete that edge so that Dijkstra's algorithm will not plan a path through a road that is blocked. We only had a chance to go through this briefly with the students on the last day (Thursday). Given more time, we would have liked to explore more scenarios with this capability (imagine having one robot as the police car and another robot trying to get away from it). This code is not published online, but it works by broadcasting UDP packets containing each cars position over the network.

The instructors wrote the code above. The students wrote their own PID control by filling in a section of the robot firmware, and they wrote Dijkstra's algorithm in python. A sample implementation of Dijkstras for this framework is included in my_graph_functions.py.
