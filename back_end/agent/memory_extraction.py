import json
from back_end.agent.get import get_identity
from back_end.useful_functions import get_completion, retrieve_episodic, get_duration


def think(agent, event):
    '''
    INPUT: agent, event
    OUTPUT: the agent generate a thought about the event
    '''
    identity = get_identity()[agent.name]
    identity.pop('initial_position', None)

    neighbors = retrieve_episodic(agent, event)
    contexts_of_neighbors = [neighbor[0] for neighbor in neighbors]
    with open('back_end/memory/identity.json', 'r') as file:
        data = json.load(file)
    names = list(data.keys())

    event_words = event.split()
    names_here = [word for word in event_words if word in names]

    file = open('back_end/prompts/think.txt', 'r')
    prompt_thought = file.read().replace(
        '#agent_name#', agent.name).replace(
        '#info#', str(identity)).replace(
        '#event#', event).replace(
        '#related_events#', str(contexts_of_neighbors)).replace(
        '#personality#', agent.print_personality()).replace(
        '#emotions#', agent.print_emotions())

    file.close()

    if len(names_here) == 0:
        prompt_thought = prompt_thought.replace(
            "They have a complex relationship with #other_agent_name#, marked by #relationship#.", " ")
    else:
        prompt_thought = prompt_thought.replace(
            '#other_agent_name#', str([name for name in names_here])).replace(
            '#relationship#', str([agent.get_relationship(name) for name in names_here]))  # relationship#.","They have a complex relationship with #other_agent_name#, marked by #relationship#.")

    prompt_thought = prompt_thought.replace("{", "").replace(
        "}", "").replace("'", "").replace("[", "").replace("]", "").replace('"', "")

    prompt_thought = prompt_thought.split("###")

    message = [
        {'role': 'system',
         'content': prompt_thought[0]},
        {'role': 'user',
         'content': prompt_thought[1]},
    ]

    thought = get_completion(message)

    agent.sensory_memory.add("Thought :" + thought)

    print(f"{agent.name} thought: {thought}")

    return thought


def reflection_daily(agent, time, n_base = 5, n_output = 3, parameters = [0.7,0.3]):
    '''
    INPUT: agent, time, n_base, n_output, parameters
    OUTPUT: the agent generate high-level insights after a day
    '''
    retrieval = []
    prompt_base = []
    memory_numbers = 0

    # sub_tasks_already_done, rest_of_plan = get_plan_status(agent)
    info_agent = agent.get_info()
    

    with open(f'back_end/memory/{agent.name}/episodic.json','r') as file:
        data = json.load(file)
    for list in data['node']:
        list.append(get_duration(list[0],time)/(60*24))
        memory_numbers += 1

    retrieval = sorted(data['node'],key = lambda x:x[3]*parameters[0]+x[2]*parameters[1],reverse = True)
    
    for i in range(n_base):
        prompt_base.append(retrieval[i][1])

    with open('back_end/prompts/thinking.txt','r') as file:
        prompt = file.read().replace("#info_agent#",info_agent).replace("#number1#",str(n_base)).replace("#number2#",str(n_output))
    
    prompt= prompt.split("###")

    message = [
        {'role': 'system',
         'content': prompt[0]},
        {'role': 'user',
         'content': prompt[1]},
    ]
    response = get_completion(message)
    return response
