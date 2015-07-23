import matplotlib.pyplot as plt
import math
import json
import pdb
from pprint import pprint

##################################################################################
#   byteify:
#   function for converting any decoded JSON object from using unicode strings to UTF-8-encoded byte strings
##################################################################################

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

##################################################################################
#   calc_dist:
#   returns distance between two points
##################################################################################

def calc_dist(x1,y1,x2,y2):
    dist = math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )
    return dist


#opens the input file and reads everything in, using json to convert it
with open("input.txt", "r") as file:
    input = file.read()

parsed_json = json.loads(input)
converted_string = byteify(parsed_json)

xcoord = []
ycoord = []

#sorts the data into x and y coordinates
i = 0
title_coord = {}
while i < len(converted_string):
    curr_dict = parsed_json[i]
    
    #gets the x and y coordinates
    x = curr_dict.get('x')
    y = curr_dict.get('y')
    xcoord.append(x)
    ycoord.append(y)
    
    #labels the node
    title = curr_dict.get('name')
    plt.text (x, y, title)
    
    #adds coord and title to dictionary
    title_coord[title] = [x,y]
    
    #adds one to the counter
    i = i + 1;

#adds the arrows and the distance between nodes
j = 0
while j < len(converted_string):
    curr_dict = parsed_json[j]
    
    #gets the x and y coordinates
    x = curr_dict.get('x')
    y = curr_dict.get('y')
    
    #gets the neighbors
    neighbor_list = curr_dict.get('neighbors')
    k = 0
    
    while k < len(neighbor_list):
        node_name = neighbor_list[k]
        temp = title_coord.get(node_name)
        x2 = temp[0]
        y2 = temp[1]

        #adds the arrows
        ax = plt.axes()
        ax.arrow(x, y, x2-x, y2-y, head_width=0.05, head_length=0.1, fc='k', ec='k')
        
        #calculates the distance
        distance = calc_dist(x,y,x2,y2)
        
        #adds the distance between the nodes
        plt.text((x+x2)/2, (y+y2)/2, distance)
        k=k+1
    j=j+1

#graphs the plot
plt.plot(xcoord, ycoord, 'ro')
plt.autoscale(enable=True, axis='both', tight=False)
print"created plot"

#displays the graph
plt.show()

