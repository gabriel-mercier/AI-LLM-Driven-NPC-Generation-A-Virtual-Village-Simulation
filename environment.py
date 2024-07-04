import time
import json
from back_end.useful_functions import get_duration, add_minutes_to_time
from back_end.map.functions import find_path, prepare_map, activate_perceive, nearby_events, nearby_agents

class Map:
    def __init__(self):
       self.agents = dict()
       self.width, self.height, self.case_details, self.coordinates, self.grid_roads, self.localisations = prepare_map()

    # Get the localisations of the map
    def get_localisations(self):
        return self.localisations
    
    # Get the coordinates of a place
    def get_coordinates(self, place):
        return self.coordinates[place]
    
    # Find a path from start to destination
    def find_path(self, start, destination):
        return find_path(self.grid_roads, start, destination)
    
    # Get the events nearby the agent
    def get_events_nearby(self, agent_name, position, radius=5):
        return nearby_events(self, agent_name, position, radius)
    
    # Get the agents nearby the agent
    def get_agents_nearby(self, agent_name, position, radius=2):
        return nearby_agents(self, agent_name, position, radius)
    
    # Remove event from the map and inform the rest of the agents
    def remove_event(self, event, agent):
        x = agent.position[0]
        y = agent.position[1]
        cases_matrix = self.case_details.get()
        
        case  = cases_matrix[x][y]
        if event in case["events"]:
            case["events"].remove(event)
        cases_matrix[x][y] = case
        self.case_details.put(cases_matrix)
        
    # Add event to the map and inform the rest of the agents
    def add_event(self, event, agent):
        x = agent.position[0]
        y = agent.position[1]
        cases_matrix = self.case_details.get()
        case  = cases_matrix[x][y]
        case["events"].append(event)
        cases_matrix[x][y] = case
        self.case_details.put(cases_matrix)
        activate_perceive(self, agent)

class Environment:
    def __init__(self):
        self.map = Map()

        self.front_end_time = 0
        
        self.start_env_time = "07:00 AM"

        self.back_end_time_velocity = 1
        
        # The ratio of the front_end time to the back_end time
        self.front_back_ratio = 1
        
        # The velocity of the simulation i.e 1 minute in real life takes velocity seconds in the simulation
        self.velocity = 2
                
        # The time when the environment started in form of seconds as a reference to the start_env_time
        self.start_env_time_seconds = time.time()
        
        self.front_end_time_velocity = self.front_back_ratio * self.velocity
        
        # The queue of configurations to be executed and the index of the last configuration
        self.queue_of_configurations = dict()
    
    # Get the time in the back_end in form of 'hh:mm AM/PM'
    def get_time_back_end(self):
        '''
        INTPUT: None
        OUTPUT: The time in the back_end in form of 'hh:mm AM/PM'
        '''
        # Time passed since the launch of the simulation in seconds
        time_passed = time.time() - self.start_env_time_seconds
        
        # Time passed in real life
        time_passed = time_passed // (self.back_end_time_velocity)
        
        return add_minutes_to_time(self.start_env_time, time_passed)
    
    # Get the duration between start and end in minutes
    def get_duration(self, start, end):
        '''
        INTPUT: start and end in form of 'hh:mm AM/PM'
        OUTPUT: The duration between start and end in minutes
        '''
        return get_duration(start, end)
    
    # Add a configuration to the queue
    def add_configuration_to_the_queue(self, agent_name, configuration):
        self.queue_of_configurations[agent_name].append(configuration)
