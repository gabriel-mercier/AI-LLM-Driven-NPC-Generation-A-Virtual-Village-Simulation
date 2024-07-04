import json
import numpy as np
from multiprocessing import Queue

'''
Here is some auxilary functions that help to get works done, but not important in the whole project.
'''


def find_path(grid_roads, start, destination):
    '''

    A* algorithm: it returns the path from start to destination only destination included. 0 represents a road and 1 represents a wall

    INPUT : 

    grid_roads : a np 2d array consists of 0 or non-zero numbers indicating where the roads are
    start : (x1, y1) indicating the starting point
    destination : (x2, y2) indicating the destination point

    OUTPUT: 

    path: A list of coordinates (x, y) from start to destination, only destination included
   
    '''
    
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    def heuristic(p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        return abs(x1 - x2) + abs(y1 - y2)

    def astar(grid_roads, start, end):
        stack = [start]
        origin = {}
        g_score = {(x, y): float('inf') for x in range(grid_roads.shape[0]) for y in range(grid_roads.shape[1])}
        g_score[start] = 0
        f_score = {(x, y): float('inf') for x in range(grid_roads.shape[0]) for y in range(grid_roads.shape[1])}
        f_score[start] = heuristic(start, end)

        while stack:
            current = min(stack, key=lambda p: f_score[p])

            if current == end:
                path = []
                while current in origin:
                    path.append(current)
                    current = origin[current]
                return path[::-1]  # Reversed to get the correct path order

            stack.remove(current)

            for direction in directions:
                x, y = current
                neighbor = (x + direction[0], y + direction[1])

                if (
                    0 <= neighbor[0] < grid_roads.shape[0] and
                    0 <= neighbor[1] < grid_roads.shape[1] and
                    grid_roads[neighbor[0]][neighbor[1]] != 0
                ):
                    tentative_g_score = g_score[current] + 1

                    if tentative_g_score < g_score.get(neighbor, float('inf')):
                        origin[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)

                        if neighbor not in stack:
                            stack.append(neighbor)

        return None

    return astar(grid_roads, start, destination)


def nearby_events(map, agent_name, position, radius=5):
    '''
    Get the events nearby the agent in a block of radius

    INPUT: 

    map: classe map
    agent: string agent name
    position: tuple (x, y)
    radius: int

    OUTPUT: 

    a set of events nearby the agent
    '''
    x = position[0]
    y = position[1]
    cases_matrix = map.case_details.get()
    map.case_details.put(cases_matrix)
    case = cases_matrix[x][y]
    agent_building = case["building"]

    events = set()

    for i in range(x - radius, x + radius + 1):
        for j in range(y - radius, y + radius + 1):
            if 0 <= i < map.height and 0 <= j < map.width:
                case = cases_matrix[i][j]
                if case["building"] == agent_building:
                    for event in case["events"]:
                        events.add(event)
    
    return events


def nearby_agents(map, agent_name, position, radius=1):
    '''
    Get the agents nearby the agent in a block of radius

    INPUT: 
    
    map: class map
    agent_name: string agent name
    position: tuple (x,y)
    radius: int

    OUTPUT: 
    a set of agents nearby the agent without the agent 
    '''
    x = position[0]
    y = position[1]
    
    cases_matrix = map.case_details.get()
    map.case_details.put(cases_matrix)
    case = cases_matrix[x][y]

    agents = set()

    for i in range(max(x-radius, 0), min(x+radius+1, map.height)):
        for j in range(max(0, y-radius), min(y+radius+1, map.width)):
            case = cases_matrix[i][j]
            for agent in case["agents"]:
                if agent != agent_name and agent not in  [event.split(",")[0] for event in case["events"] ]:
                    agents.add(map.agents[agent])
    return agents


# Not used
def activate_perceive(map, agent):
    '''
    looks for all the agents in a block of radius 5 cases around the position specified
    and activate their perceive function
    '''
    near_agents = nearby_agents(map, agent.name, agent.position)
    for near_agent in near_agents:
        if near_agent.name != agent.name:
            near_agent.perceive(map)


def prepare_map(map_file="back_end/map/map.json"):
    '''
    Prepare the map: Generate the case_details, map_dict, coordinates and grid_roads
    INPUT: 

    map_file

    OUTPUT:

    width: int
    height: int
    case_details: a 2D array of dictionaries, each dictionary contains the details of a case
    map_dict: a dictionary of dictionaries, each dictionary contains the objects in a hall
        example: {"building":{"hall_1":{"object_1","object_2"},"hall_2":{"object_3"}}}
    coordinates: a dictionary of sets, each set contains the coordinates of a localisation 
        either is type uiding, building:hall or building:hall:object
    grid_roads: a np 2D array of integers, each integer represents 1 if the case is a road and 0 otherwise
    '''
    
    with open(map_file) as json_file:
        data = json.load(json_file)
        json_file.close()

    height, width, tilewidth = data["height"], data["width"], data["tilewidth"]
    
    # map to dict : building -> hall -> object
    case_details = Queue()
    cases_matrix = [[dict() for i in range(width)] for j in range(width)]
    for i in range(height):
        for j in range(width):
            cases_matrix[i][j] = {"building":None, "hall":None, "object":[], "agents":[], "events":[]}
    
    case_details.put(cases_matrix)
    
    # example: {"building":{"hall_1":{"object_1","object_2"},"hall_2":{"object_3"}}}
    map_dict = dict()
    
    layers = data["layers"]
    
    # get the grid_roads
    for layer in layers:
        layer_name = layer["name"]
        if layer_name == "road":
            grid = layer["data"]
        if layer_name == "Building":
            Buildings = layer["objects"]
        if layer_name == "Hall":
            Halls = layer["objects"]
        if layer_name == "Object":
            objects = layer["objects"]
    grid_roads = np.array([[grid[i+j*width] for i in range(width)] for j in range(height)])
        
    # convert pixels to cases
    def get_cases(x, y, width, height): 
        xmin=int(x/tilewidth)
        ymin=int(y/tilewidth)
        xmax=int((x+width)/tilewidth)
        ymax=int((y+height)/tilewidth)
        cases = set()
        for i in range(xmin,xmax+1):
            for j in range(ymin,ymax+1):
                cases.add((j,i))
        return cases
    
    # update the case details with the places and objects from the json file 
    Instances = [Buildings, Halls, objects]
    cases_matrix = case_details.get()

    for i in range(len(Instances)):
        for instance in Instances[i]:
            x = instance["x"]
            y = instance["y"]
            width_ = instance["width"]
            height_ = instance["height"]
            cases = get_cases(x, y, width_, height_)
            if i == 0:
                for case in cases:
                    tile = cases_matrix[case[0]][case[1]]
                    tile["building"] = instance["name"]
                    cases_matrix[case[0]][case[1]] = tile
            elif i == 1:
                for case in cases:
                    tile = cases_matrix[case[0]][case[1]]
                    tile["hall"] = instance["name"]
                    cases_matrix[case[0]][case[1]] = tile
            elif i == 2:
                for case in cases:
                    tile = cases_matrix[case[0]][case[1]]
                    tile["object"].append(instance["name"])
                    cases_matrix[case[0]][case[1]] = tile

    case_details.put(cases_matrix)
    

    # update the building dict
    cases_matrix = case_details.get()
    case_details.put(cases_matrix)

    for i in range(height):
        for j in range(width):
                case = cases_matrix[i][j]
                building = case["building"]
                hall = case["hall"]
                objects = case["object"]
                if building is not None:
                    if building not in map_dict.keys():
                        map_dict[building] = dict()
                    if hall is not None: 
                        if hall not in map_dict[building].keys():
                            map_dict[building][hall] = set()
                        if len(objects) != 0:
                            for object in objects:
                                map_dict[building][hall].add(object)
                    
    # Create a list that contains all the possible localisations in form of building:hall and building:hall:object
    localisations = dict()
    for building in map_dict.keys():
        for hall in map_dict[building]:
            localisations[building+":"+hall] = map_dict[building][hall]

    # Coordinates of each place in form of building, building:hall and building:hall:object containing the coordinates (i,j) of the place in the map
    cases_matrix = case_details.get()
    case_details.put(cases_matrix)

    coordinates = dict()
    for i in range(height):
        for j in range(width):
            case = cases_matrix[i][j]
            building = case["building"]
            hall = case["hall"]
            objects = case["object"]
            if building != None:
                if building not in coordinates:
                    coordinates[building] = {(i,j)}
                else :
                    coordinates[building].add((i,j))
                if hall != None:
                    if building+":"+hall not in coordinates:
                        coordinates[building+":"+hall] = {(i,j)}
                    else :
                        coordinates[building+":"+hall].add((i,j))
                    if len(objects) != 0:
                        for object in objects:
                            if building+":"+hall+":"+object not in coordinates:
                                coordinates[building+":"+hall+":"+object] = {(i,j)}
                            else :
                                coordinates[building+":"+hall+":"+object].add((i,j))

    return width, height, case_details, coordinates, grid_roads, localisations