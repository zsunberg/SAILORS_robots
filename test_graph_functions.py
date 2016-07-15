import my_graph_functions
from sailorsmap import RoadMap

graph = RoadMap('bay_area.json')

vertex_sequence = [1,5,7,6]
length = my_graph_functions.length_of_path(graph, vertex_sequence)
if length is not None and float(length) == 79.0:
    print 'length_of_path() worked!'
else:
    print "length_of_path() didn't work. You returned a length of {} for {}".format(length, vertex_sequence)

vertex_sequence = [5,4,3,2,6]
length = my_graph_functions.length_of_path(graph, vertex_sequence)
if length is not None and float(length) == 17+34+10+25:
    print 'length_of_path() worked!'
else:
    print "length_of_path() didn't work. You returned a length of {} for {}".format(length, vertex_sequence)

short_path = my_graph_functions.shortest_path(graph, 1, 6)
if short_path == [1,5,7,6]:
    print 'shortest_path() worked!'
else:
    print "shortest_path() didn't work. You returned a path of {} for starting at 1 and ending at 6".format(short_path)
