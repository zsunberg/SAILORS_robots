'''
A class for representing a road map for sailors - uses igraph under the hood

usage:

    map = RoadMap('file.json')

    map[n] # returns dictionary-like object with all the properties of node n

    map[1]['best_distance'] = 2.0 # set the 'best_distance' attribute of vertex 1

    map.neighbors(n) # return a list of the neighbors of n

    map[1,2] # return the weight (distance between vertices) between 1 and 2

    for i in map:
        print i      # print the indices of all of the vertices in the map
    
    map.highlight_vertex(2) # will highlight vertex 2 the next time the graph is plotted
    map.plot() # plots the map using matplotlib

    map.detect_roadblocks() # detects road blocks


Each node has a
number
x and y location
best_distance value initially set to infinity
pointer to optimal predecessor

json file looks like:
{"vertices":
    [
     ...
        {"num":2,
         "x":1.2,
         "y":2.3,
         "north":3
         "south":3
         "east":4
         "west":5
        },
     ...
    ],
 "curved":
    [
        [[1,2],14.7],
     ...   
    ]
}
'''

import igraph
import json
import math
import pdb
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
import numpy as np
import time
import socket

#plt.ion()

class RoadMap(object):
    def __init__(self, input_file='map_in_ASL.json'):
        
        
        with open(input_file) as file:
            input = file.read()

        graph_dict = json.loads(input.replace('\r\n', ''))
        #converted_string = byteify(parsed_json)
        
        
        #with open(input_file) as ifile:
        #    graph_dict = json.load(ifile)
        self.g = igraph.Graph()
        vertices = graph_dict['vertices']

        # check that all the numbers are right
        for i in range(len(vertices)):
            assert vertices[i]["num"] == i

        # add all the vertices and attributes
        self.g.add_vertices(len(vertices))
        for attribute in ['x', 'y', 'north', 'south', 'east', 'west']:
            self.g.vs[attribute] = [v[attribute] for v in vertices]
        self.g.vs['best_distance'] = self.g.vcount()*[float('inf')]
        self.g.vs['predecessor'] = self.g.vcount()*[None]

        # add the edges
        for v in vertices:
            for d in ['north', 'east', 'south', 'west']:
                if v[d] is not None:
                    self.g.add_edge(v['num'], v[d])
        assert self.g.is_directed() == False

        # weight the edges by distance
        self.g.es['weight'] = 1.0
        for e in self.g.es:
            v1 = self.g.vs[e.source]
            v2 = self.g.vs[e.target]
            e['weight'] = math.sqrt((v1['x']-v2['x'])**2
                               + (v1['y']-v2['y'])**2)
        # set the curved ones
        for c in graph_dict['curved']:
            self.g[c[0][0], c[0][1]] = c[1]

        self.highlighted_vertex = None
        self.highlighted_edge = None
        self.detected_cars = dict()

    def __getitem__(self, v):
        """Bracket operator. map[1] gets node 1, map[1,2] gets the edge weight between 1 and 2"""
        # if only one argument provided, return the vertex
        if type(v)==int:
            return self.g.vs[v]
        else:
            return self.g[v[0], v[1]]

    def neighbors(self, v):
        """Return a list of neighbors."""
        return list(set(self.g.neighbors(v)))

    def __len__(self):
        """Return the number of nodes."""
        return self.g.vcount()

    def __iter__(self):
        """Allow map to be used in a for loop."""
        return iter(range(len(self)))

    def plot(self):
        plt.clf()
        def label(xy, text, lowertext):
            y = xy[1] -.05 # shift y-value for label so that it's below the artist
            plt.text(xy[0], y, text, ha="center", family='sans-serif', size=8, zorder = 15)
            y = xy[1] - 0.3 # shift y-value for label so that it's below the artist
            plt.text(xy[0], y, lowertext, ha="center", family='sans-serif', size=8)
        """Plot the graph."""
        ax = plt.gca()
        # fig, ax = plt.subplots()
        xcoord = []
        ycoord = []
        title_coord = {}
        patches = []

        # plot cars
        for key in self.detected_cars:
            car = mpatches.Rectangle(xy=self.detected_cars[key],
                                     width=.1, height=.1,
                                     angle=45, color='green')
            plt.text(self.detected_cars[key][0],
                     self.detected_cars[key][1],
                     str(key))
            ax.add_patch(car)

        for i in range(self.g.vcount()):
            #gets the x and y coordinates
            dict = self.g.vs[i].attributes()
            x = dict['x']
            y = dict['y']
            xcoord.append(x)
            ycoord.append(y)
            #plots it
            circle = mpatches.Circle([x,y],0.15,color='yellow',hatch = '*', zorder = 3)
            ax.add_patch(circle)
            #labels the node
            label_text = str(i)
            label_lower_text = self.g.vs[i]['best_distance']
            label([x,y], label_text, label_lower_text)
            #adds coord and title to dictionary
            title_coord[i] = [x,y]

        if self.highlighted_vertex is not None:
            circle = mpatches.Circle([self.highlighted_vertex[0],
                                      self.highlighted_vertex[1]],
                                     0.15,color='red',hatch = 'o',
                                     zorder = 9)
        ax.add_patch(circle)

    
        for i in range(self.g.vcount()):
            neighbor_list = []
            dict = self.g.vs[i].attributes()
            #gets the current x and y coordinates
            x = dict.get('x')
            y = dict.get('y')
            
            #gets the neighbors
            if dict['north'] is not None:
                neighbor_list.append(dict['north'])
            if dict['south'] is not None:
                neighbor_list.append(dict['south'])
            if dict['east'] is not None:
                neighbor_list.append(dict['east'])
            if dict['west'] is not None:
                neighbor_list.append(dict['west'])
           
           
            for k in range(len(neighbor_list)):
                node_name = neighbor_list[k]
                temp = title_coord.get(node_name)
                x2 = temp[0]+0.0
                y2 = temp[1]+0.0
                #adds the lines
                ax.arrow(x, y, x2-x, y2-y, color = 'pink',zorder = 1)
                #gets the distance
                distance = self.g[i,node_name]
                #adds the distance between the nodes
                plt.text((x+x2)/2.0, (y+y2)/2.0, distance,size=5,zorder = 11)

            if self.highlighted_edge is not None:
                ax.arrow(self.highlighted_edge[0],
                         self.highlighted_edge[1],
                         self.highlighted_edge[2] - self.highlighted_edge[0],
                         self.highlighted_edge[3] - self.highlighted_edge[1],
                         color = 'blue',zorder = 2)

        #graphs/displays the plot
        #plt.plot(xcoord, ycoord)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.autoscale(enable=True, axis='both', tight=False)

        plt.show()
        # print "done agin"
        pass

    def highlight_vertex(self, vertex):
        """Highlight a vertex when the graph is plotted."""
        dict = self.g.vs[vertex].attributes()
        x = dict['x']
        y = dict['y']
        self.highlighted_vertex = [x,y]
        pass

    def highlight_edge(self, v1, v2):
        """Highlight an edge when the graph is plotted."""
        dict = self.g.vs[v1].attributes()
        x = dict['x']
        y = dict['y']
        dict = self.g.vs[v2].attributes()
        x2 = dict['x']
        y2 = dict['y']
        self.highlighted_edge = [x,y,x2,y2]
        pass

    def detect_cars(self, timeout=1):
        self.detected_cars = dict()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(('', 1930))
            s.settimeout(timeout)
            start = time.time()

            while time.time() < start + timeout:
                data = s.recv(1024)
                for d in data.split('\n'):
                    parts = d.split(':')
                    if parts[0] == 'c':
                        # convert to feet
                        self.detected_cars[int(parts[1])] = [float(x)*3.28 for x in parts[3].split(',')[0:2]]
                        # print "got one"
                    elif d[0] == '\x00':
                        # don't understand what this is
                        pass
                    else:
                        print parts

        except socket.timeout as e:
            print(e)
            print("Didn't get any data from Vicon.")

        finally:
            s.close()

if __name__ == "__main__":
    map = RoadMap()
    map.highlight_vertex(1)
    map.highlight_edge(0, 1)
    map.plot()
