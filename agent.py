from back_end.agent.plan import create_initial_plan, create_sub_plan, get_object_for, insert_discussion
from back_end.agent.get import get_identity, get_current_event, change_current_event, get_relationship
from back_end.agent.memory_extraction import think
from back_end.agent.detect import perceive, interact
from back_end.agent.discussion import get_discussion
from back_end.agent.functions import filter_sensory_memory, delete, end_of_the_day
from back_end.useful_functions import add_episodic, retrieve_episodic
from back_end.agent.execute import execute_sub_task
from back_end.long_term_memory.emotion import Emotion
from back_end.long_term_memory.personality import Personality


class Agent:
    def __init__(self, name):
        # the agent information
        self.name = name
        self.file_path = f'back_end/memory/{name}/'
        self.position = (self.get_identity()[
                         'initial_position']['x'], self.get_identity()['initial_position']['y'])
        self.first_time = True
        # The sensory memory of the agent
        self.sensory_memory = set()

        # The emotions and the personality of the agent
        self.emotion = Emotion(self.name)
        self.personality = Personality(self.name)

    # Get identity info from memory to create initial plan
    def get_identity(self):
        return get_identity()[self.name]

    # Get identity info from memory to create initial plan
    def get_info(self):
        info = self.get_identity()
        info.pop('initial_position', None)
        return str(info).replace(
            "{", " ").replace("}", " ").replace("'", "") + self.print_personality()

    def delete(self):
        return delete(self.name)

    def think(self, event):
        return think(self, event)

    def change_current_event(self, event, lock):
        return change_current_event(self.name, event, lock)

    def get_current_event(self, lock):
        return get_current_event(self.name, lock)

    # Get the relation between the agent and an other agent
    def get_relationship(self, other_agent_name):
        return get_relationship(self.file_path, self.name, other_agent_name)

    # Get the discussion between the agent and the other agent
    def get_discussion(self, other_agent, lock):
        return get_discussion(self, other_agent, lock)

    # Create initial plan and save it in memory
    def create_initial_plan(self):
        return create_initial_plan(self.get_info(), self.file_path)

    # Create sub plan for task_i and save it in memory
    def create_sub_plan(self, i, localisations, lock):
        return create_sub_plan(i, self, localisations, lock)

    # Insert discussion in memory
    def insert_discussion(self, disc_discription, disc_length):
        return insert_discussion(self, disc_discription, disc_length)

    # Get object for task at localisation to have a complete localisation : building:hall:object
    def get_object_for(self, task, localisation, objects):
        return get_object_for(task, localisation, objects)

    # Execute sub task task between start and end at localisation in environment
    def execute_sub_task(self, sub_task, environment, index_of_task, index_of_sub_task, lock):
        execute_sub_task(self, sub_task, environment,
                         index_of_task, index_of_sub_task, lock)

    # Perceive the environment by updating the sensory memory of the agent
    def perceive(self, map):
        return perceive(self, map)

    # Filter the sensory memory
    def filter_sensory_memory(self, events, environment, lock, discussions=None):
        filter_sensory_memory(self, events, environment, discussions, lock)

    # Clear the sensory memory
    def clear_sensory_memory(self):
        self.sensory_memory = set()

    # Get the answer if the agent should interact with the other agents
    def interact(self, other_agents, lock):
        return interact(self, other_agents, lock)

    def add_episodic(self, event, time, importance):
        add_episodic(self, event, time, importance)

    def retrieve_episodic(self, context, n):
        return retrieve_episodic(self, context, n)

    def update_emotion(self, lock):
        return self.emotion.update_emotion(self, self.get_current_event(lock))

    def update_personality(self, event):
        return self.personality.update_personality(self, event)

    def print_emotions(self):
        return self.emotion.print_emotions()

    def print_personality(self):
        return self.personality.print_personality()

    def end_of_the_day(self, env):
        return end_of_the_day(self, env)
