from sailorsbot import SBot

#max and min speeds
MAX = 0.3
MIN = 0.0

#PID gains
P_TERM = 1.5
I_TERM = 0.00
D_TERM = 0

def follow_segment(car):
    #makes list of size 5 to hold sensor values
    sensors = [None]*5
    prev_position = 0.0
    derivative = 0.0
    proportional = 0.0
    integral = 0.0
    position = 0.0
    power = 0.0    #speed increase or decrease
    right = 0.0
    left = 0.0
    speed = MAX
    
    sensors = car.get_sensors()
    sensors = car.get_sensors()
    sensors = car.get_sensors()
    
    while True:
        
        #gets sensor values and puts into the list
        sensors = car.get_sensors()
        
        #prints the sensor readings
        #for value in sensors :
        #   print value
        
        #prints out the line position
        print car.get_line_position()
        
        #line position
        position = car.get_line_position()
        proportional = position
        
        #derivative
        derivative = position - prev_position
        
        #ingegral
        integral = integral + proportional

        #last position
        prev_position = position

        power = (proportional*P_TERM) + (integral * I_TERM) + (derivative * D_TERM)

        #new speeds
        right = speed + power
        left = speed - power
            
        if right < MIN:
            right = MIN
        elif right > MAX:
            right = MAX
            
        if left < MIN:
            left = MIN
        elif left > MAX:
            left = MAX

        car.set_left_motor(left)
        car.set_right_motor(right)
        

        
"""
        if sensors[0] < 1200 and sensors[1] < 1200 and sensors[2] < 1200 and sensors[3] < 1200 and sensors[4] < 1200:
            print"dead end"
            car.stop()
            print "stopped car"
            car.kill_comm()
            print "killed communication"
            #dead end
            return -1
        elif sensors[0] > 1800 or sensors[4] > 1800:
            #intersection
            print"intersection"
            return 0;
        else:
            car.stop()
            car.killcomm()

    return 0
    
"""
