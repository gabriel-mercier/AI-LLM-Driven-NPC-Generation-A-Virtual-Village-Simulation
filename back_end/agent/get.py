import json


def get_current_event(agent_name, lock):
    '''
    INTPUT: agent_name
    OUTPUT: the current event of the agent
    '''
    lock.acquire()
    try:
        with open('back_end/memory/current_event.json', 'r') as file:
            data = json.load(file)
            file.close()
            current_event = data[agent_name]
    finally:
        lock.release()
    return current_event


def change_current_event(agent_name, event, lock):
    '''
    INPUT: agent_name, event
    OUTPUT: change the current event of the agent in the memory
    '''

    lock.acquire()
    try:
        with open('back_end/memory/current_event.json', 'r') as file:
            data = json.load(file)
            file.close()
        data[agent_name] = event
        with open('back_end/memory/current_event.json', 'w') as file:
            json.dump(data, file, indent=4)
            file.close()
    finally:
        lock.release()
    return event


def get_identity():
    '''
    INTPUT: agent
    OUTPUT: a dictionnary containing identity info i.e name, age, personality, life style, profile ...
    '''
    try:
        with open('back_end/memory/identity.json', 'r') as file:
            existing_data = json.load(file)
            file.close()
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}
    return existing_data


def get_relationship(agent_file_path, agent_name, other_agent_name):
    '''
    INTPUT: agent_file_path, agent_name, other_agent_name
    OUTPUT: the relationship between the agent and the other_agent
    '''

    relationship_explanation = f"What is following is an array of size 4, describing the relationship from the point of view of {agent_name} where each element corresponds, in order, to the following characteristics: dominance, appreciation, solidarity, familiarity with values ranging from 0 to 10 : "

    try:
        with open(agent_file_path + 'relationship.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        return 'Error: relationship.json file not found.'
    except json.JSONDecodeError:
        return 'Error: Failed to decode relationship.json.'

    if other_agent_name in data:
        relationship = data[other_agent_name].get(
            "relationship", "Unknown relationship")
        description = data[other_agent_name].get(
            "description", "No description available")
        return relationship_explanation + str(relationship) + ". " + str(description)
    else:
        return f"No relationship information found for {other_agent_name}."


def get_plan_status(agent_name, file_path, lock):
    '''
    INPUT: agent
    OUTPUT: a list of all tasks already performed and a list of tasks to be done in the future.
    '''
    sub_tasks_already_done = []
    rest_of_plan = []
    with open(file_path + 'plan.json', 'r') as file:
        plan = json.load(file)

    current_event_found = False

    for task in plan:
        if len(task) >= 4:
            sub_tasks = task[3]
            for sub_task_value in sub_tasks:
                sub_task_description = sub_task_value[3]

                if f"{agent_name},{sub_task_description}" == get_current_event(agent_name, lock):
                    current_event_found = True
                    sub_tasks_already_done.append(sub_task_description)
                elif current_event_found:
                    rest_of_plan.append(sub_task_description)
                else:
                    sub_tasks_already_done.append(sub_task_description)
        else:
            if len(task) > 2:
                rest_of_plan.append(task[2])

    return sub_tasks_already_done, rest_of_plan


def get_info_agent(agent_name):
    '''
    INPUT: agent_name
    OUTPUT: the info of the agent
    '''
    try:
        with open('back_end/memory/identity.json', 'r') as file:
            data = json.load(file)
            info = data[agent_name]
    except FileNotFoundError:
        print(f"file identity cannot be found")
        info = None
    return info
