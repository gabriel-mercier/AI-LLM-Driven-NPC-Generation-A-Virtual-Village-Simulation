import json
from back_end.useful_functions import get_completion
from back_end.agent.get import get_current_event


def search(agent_name, lock):
    '''
    INPUT : agent_name
    OUTPUT : the name of the agent that has seen given agent_name
    '''
    lock.acquire()
    try:
        with open('back_end/memory/agent_detected.json', 'r') as file:
            info = json.load(file)
            file.close()
    finally:
        lock.release()
    for name in info:
        if agent_name in info[name]:
            return name
    return None


def perceive(agent, map):
    '''
    INPUT : agent, map
    OUTPUT : add events to the sensory memory when discovering the environment or when some agent
    activated the perceive function and return the agents nearby
    '''

    # Get the events nearby the agent and eventually the discussion
    events_nearby = map.get_events_nearby(agent.name, agent.position)
    events_nearby = [
        f'{event.split(",")[0]} is {event.split(",")[1]}' for event in events_nearby]

    for event in events_nearby:
        agent.sensory_memory.add(event)

    agents_nearby = map.get_agents_nearby(agent.name, agent.position)

    return agents_nearby


def interact(agent, other_agents, lock):
    '''
    INTPUT: agent, other_agents
    OUTPUT: No or name of the orther agent that the agent should interact with 
    '''

    other_agents_info = [[other_agent.name, agent.get_relationship(other_agent.name), get_current_event(
        other_agent.name, lock)] for other_agent in other_agents]

    file = open('back_end/prompts/interact.txt', 'r')
    prompt_interact = file.read().replace('#task_of_the_agent#', get_current_event(
        agent.name, lock).split(',')[1]).replace('#other_agents_info#', str(other_agents_info))
    file.close()

    prompt_interact = prompt_interact.split("###")

    message = [
        {'role': 'system',
         'content': prompt_interact[0]},
        {'role': 'user',
         'content': prompt_interact[1]},
    ]

    answer = get_completion(message)

    return answer
