
def length_of_path(graph, vertex_sequence):
    pass

def end_up_at(graph, initial_vertex, initial_direction, turn_sequence):
    pass

def turns(graph, vertex_sequence):
    pass
    
def shortest_path(graph, start, end):
    """Return a vertex sequence representing the shortest path from start to end"""
    
    # Dijkstra's algorithm

    # initialize visited, best_distances, predecessors
    current = start
    visited = []
    best_distances = len(graph)*[float('inf')]
    best_distances[start] = 0.0
    predecessors = len(graph)*[None]

    # loop until current = end
    while current != end:
        visited += [current]

        # update distances and predecessors
        for i in graph.neighbors(current):
            new_dist = graph[current, i] + best_distances[current]
            if new_dist < best_distances[i]:
                best_distances[i] = new_dist
                predecessors[i] = current

        # select the next node to be current
        min_ind = 0
        min_best_dist = float('inf')
        for i in graph:
            if i not in visited and best_distances[i] < min_best_dist:
                min_best_dist = best_distances[i]
                min_ind = i

        current = min_ind

    # reconstruct the path
    backwards_path = []
    while current != start:
        backwards_path += [current]
        current = predecessors[current]
    backwards_path += [start]

    return list(reversed(backwards_path))
