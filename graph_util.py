turn_dict = {'north':{'north':'s',
                      'east':'r',
                      'west':'l'},
             'east': {'east':'s',
                      'south':'r',
                      'north':'l'},
             'south':{'south':'s',
                      'east':'l',
                      'west':'r'},
             'west' :{'west':'s',
                      'south':'l',
                      'north':'r'}
             }

opposite_dir = {'north':'south',
                'south':'north',
                'east':'west',
                'west':'east'}

def incoming_direction(graph, u, v):
    for d in ['north', 'east', 'south', 'west']:
        if graph[v][d] == u:
            return opposite_dir[d]

def outgoing_direction(graph, u, v):
    for d in ['north', 'east', 'south', 'west']:
        if graph[u][d] == v:
            return d

def turns(graph, vertex_sequence):
    t = ''
    current_dir = incoming_direction(graph, vertex_sequence[0],vertex_sequence[1])

    for i in range(1,len(vertex_sequence)-1):
        next_dir = outgoing_direction(graph, vertex_sequence[i], vertex_sequence[i+1])
        if not graph[vertex_sequence[i]]['passthrough']:
            t += turn_dict[current_dir][next_dir]
        # except KeyError as e:
        #     print e
        #     print current_dir
        #     print next_dir
        #     print vertex_sequence
        #     print i
        #     raise e
        current_dir = incoming_direction(graph, vertex_sequence[i], vertex_sequence[i+1])

    return t

def orientation_turns(graph, current_vertex, current_direction, next_vertex):
    """Return a string consisting of 'r', 'l', or 'll' or '' of turns to be executed in-place to orient correctly to begin a sequence of turns."""
    next_dir = outgoing_direction(graph, current_vertex, next_vertex)
    if opposite_dir[current_direction] == next_dir:
        return 'll'
    turn = turn_dict[current_direction][next_dir]
    if turn == 's':
        return ''
    else:
        return turn
