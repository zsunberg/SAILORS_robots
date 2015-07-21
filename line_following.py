from sailorsbot import SBot
from line_follow_functions import follow_segment
from ipdb import set_trace as bp

with SBot(11) as car:
    print "created car"
    follow_segment(car)

