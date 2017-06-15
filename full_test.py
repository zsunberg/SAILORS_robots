from sailorsbot import SBot
import time
import sys

if len(sys.argv) <= 1:
    num = 7
else:
    num = int(sys.argv[1])

print "trying with car "+str(num)


with SBot(num) as car:
    car.nudge(0.2)
    car.turn("left")
    car.turn("right")
    car.forward(0.3)
    time.sleep(1.0)
    car.stop()
