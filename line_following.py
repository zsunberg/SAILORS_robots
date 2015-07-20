from sailorsbot import SBot
from line_follow_functions import follow_segment
import pdb

""" use python -m pdb myscript.py in the terminal to test debugging.
    follow this link for common commands:
    
    http://stackoverflow.com/questions/4929251/can-you-step-through-python-code-to-help-debug-issues
    
    this command sets a breakpoint on the following line:
    pdb.set_trace()
"""


with SBot(13) as car:
    print "created car"
    follow_segment(car)

