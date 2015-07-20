from sailorsbot import SBot
from line_follow_functions import follow_segment

with SBot(3) as car:
    print "created car"
    follow_segment(car)

