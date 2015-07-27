'''
A class for representing a road map for sailors - uses igraph under the hood

Each node has a
number
x and y location
value initially set to infinity
pointer to optimal

TODO left, right turning information

json file needs nodes 
{"vertices":
    [
        {"num":1,
         "x":1.2,
         "y":2.3,
         "north":2
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

class RoadMap(object):
    def __init__(self, input_file='sailorsmap.json'):
        with open(input_file) as ifile:
            graph_dict = json.load(ifile)
        self.g = igraph.Graph()
        vertices = graph_dict['vertices']

        # check that all the numbers are right
        for i in 1:len(vertices):
            assert vertices[i]["num"] == i

        # add all the vertices and attributes
        g.add_vertices(len(vertices))
        for attribute in ['x', 'y', 'north', 'south', 'east', 'west']:
            g.vs[attribute] = [v[attribute] for v in vertices]
        g.vs['distance'] = g.vcount()*[float('inf')]
        g.vs['next'] = g.vcount()*[None]

        # add the edges
        for v in vertices:
            for d in ['north', 'east', 'south', 'west']:
                g.add_edge((v['num'], v[d]))
        assert g.is_directed() == False

        # weight the edges by distance
        g.es['weight'] = 1.0
        for e in g.es:
            e['weight'] = sqrt((e.source['x']-e.target['x'])**2
                               + (e.source['y']-e.target['y'])**2)
        # set the curved ones
        for c in graph_dict['curved']:
            edge = g[c[1][1], c[1][2]]
            edge['weight'] = c[2]

    def set_next(self, vertex, value)
    """Set the optimal next node to go to."""
        g.vs[vertex]['next'] = value

    def set_distance(self, vertex, value):
    """Set estimate of distance to goal."""
        g.vs[vertex]['distance'] = value

    def plot()
    """Plot the graph."""
        pass

    def select_vertex_for_plot(self, vertex):
    """Highlight a vertex when the graph is plotted."""
        pass

    def select_edge_for_plot(self, v_num):
    """Highlight an edge when the graph is plotted."""
        pass
