from sailorsbot import SBot
from sailorsmap import RoadMap
from my_graph_functions import shortest_path
from graph_util import turns
import time

graph = RoadMap('map_in_ASL.json')
while True:
    graph.detect_cars()
    print graph.detected_cars
