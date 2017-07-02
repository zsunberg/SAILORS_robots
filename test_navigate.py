from sailorsbot import SBot
from sailorsmap import RoadMap
from my_graph_functions import shortest_path
from graph_util import turns
import time

graph = RoadMap('map_in_ASL.json')

start = 48 
end = 1

path = shortest_path(graph, start, end)
graph.highlight_path(path)
graph.plot()

turn_sequence = turns(graph, path)
print turn_sequence
raw_input("Press enter to go")

with SBot(3) as car:
    for i in range(len(turn_sequence)):
        car.set_mode(1)
        car.wait_for_manual()
        car.nudge(0.2)
        time.sleep(0.1)
        if turn_sequence[i] != 's':
            car.turn(turn_sequence[i])
            time.sleep(0.1)
    car.set_mode(1)
    car.wait_for_manual()
