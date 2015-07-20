import ast
import dijkstras_functions

print "This program is intended to demonstrate the Dijkstras algorithm" + "\n"

#user enters the nodes
dictionary = raw_input("Enter the graph in the following format: " + "\n" +
                       "{'node':{'node':dist,'node':dist}," + "\n" +
                       "'node':{'node':dist,'node':dist}}" + "\n")
graph = {}
graph = ast.literal_eval(dictionary)

#prints out the nodes
for node in graph:
    print (node)
    for consec_node in graph[node]:
        print (consec_node,":",graph[node][consec_node])

starting_node = raw_input("Enter starting node: " + "\n")
ending_node = raw_input("Enter ending node: " + "\n")

dijkstras_functions.calc_shortest_path(graph,starting_node,ending_node)

#dijkstras_functions.calc_shortest_path(graph,'s','t')
