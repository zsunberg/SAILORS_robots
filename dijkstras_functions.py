

"""
    
calculate_shortest_path(name of dictionary containing node information,
                        starting node name,
                        ending node name)
Using Dijkstras Algorithm, this function will calculate the shortest path from the starting node to the ending node

output: shortest path: *prints shortest path* cost= *prints shortest distance*

"""

def calc_shortest_path(graph,start_node,end_node,visited_nodes=[],distances={},predecessors={}):

    #checking if the start/end node is in the graph
    if start_node not in graph:
        print "start node not in graph!"
    if end_node not in graph:
        print "end node not in graph!"

    #if the path is built, add the current node to the list of paths and print result
    if start_node == end_node:
        # We build the shortest path and display it
        path=[]
        pred=end_node
        while pred != None:
            path.append(pred)
            pred=predecessors.get(pred,None)
        print('shortest path: '+str(path)+" distance = "+str(distances[end_node]))
    else :
        #if this is the first loop, makes the distane 0
        if not visited_nodes:
            distances[start_node]=0
        #visits the connected nodes
        for neighbor in graph[start_node] :
            if neighbor not in visited_nodes:
                new_distance = distances[start_node] + graph[start_node][neighbor]
                
                #if the current distance is less than the previous distance, and if the node has not been visited before, if the current distance is less than infinity
                
                if new_distance < distances.get(neighbor,float('inf')):
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = start_node
        # mark as visited
        visited_nodes.append(start_node)
        
        #the program recurses until all the nodes have been visited, takes the lowest unvisted node and recurses with that
        unvisited={}
        for k in graph:
            if k not in visited_nodes:
                unvisited[k] = distances.get(k,float('inf'))
        x=min(unvisited, key=unvisited.get)
        calc_shortest_path(graph,x,end_node,visited_nodes,distances,predecessors)


                                                                        
                                                                         
                                                                         
                                                                         
                                                                         
                                                                         
                                                                         
                                                                         
                                                                         
                                                                         
                                                                         
                                                                         
                                                                         
                                                                         
                                                                         
                                                                         
                                                                         
                                                                         
                                                                         
                                                                         
                                                                         

