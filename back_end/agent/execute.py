import time
import json
from back_end.agent.functions import calculate_direction
from back_end.agent.discussion import launch_discussion, hear_discussion
from back_end.agent.detect import search


def move(agent, direction, environment):
    '''
    INPUT: agent, direction : "UP" / "DOWN" / "RIGHT" / "LEFT", environment
    OUTPUT: in class environment, the agent moves by one step in the direction
    '''

    map = environment.map
    cases_matrix = map.case_details.get()
    case = cases_matrix[agent.position[0]][agent.position[1]]
    if agent.name in case["agents"]:
        case["agents"].remove(agent.name)
    cases_matrix[agent.position[0]][agent.position[1]] = case
    map.case_details.put(cases_matrix)

    if direction == "UP":
        agent.position = (agent.position[0]-1, agent.position[1])
    elif direction == "DOWN":
        agent.position = (agent.position[0]+1, agent.position[1])
    elif direction == "RIGHT":
        agent.position = (agent.position[0], agent.position[1]+1)
    else:
        agent.position = (agent.position[0], agent.position[1]-1)

    cases_matrix = map.case_details.get()
    case = cases_matrix[agent.position[0]][agent.position[1]]
    case["agents"].append(agent.name)
    cases_matrix[agent.position[0]][agent.position[1]] = case
    map.case_details.put(cases_matrix)


def move_agent_to(agent, path, environment, step_time, lock):
    '''
    INPUT: agent, path, environment, step_time
    OUTPUT: in class environment, the agent moves from its current position to the destination
    '''
    # Create a reference time for the whole path
    time_0 = time.time()
    # Move the agent to the destination localisation in the environment
    agents_seen = []

    while len(path) != 0:
        # Define a reference time to be used to wait for the duration of the step
        current_time = time.time()

        # Move a step
        direction = calculate_direction(agent.position, path.pop(0))
        move(agent, direction, environment)
        environment.add_configuration_to_the_queue(agent.name, [
                                                   f'{agent.name} is walking', step_time * environment.front_back_ratio, direction])

        # Wait for the duration of the task, i.e wait till the end of the task is reached and stay active
        while time.time() < current_time + step_time:
            # Perceive the environment by adding the new information to the sensory memory and get the agents nearby
            agents = agent.perceive(environment.map)

            agents = list(agents)

            # Agents that have not been seen yet during the round path
            other_agents = [a for a in agents if a.name not in agents_seen]

            if len(other_agents) != 0:
                # Check if I was already seen by an agent
                agent_asking_me = search(agent.name, lock)

                # If I was seen by an agent
                if agent_asking_me != None:

                    hear_discussion(agent, agent_asking_me, environment, lock)

                # If I was not seen by any agent
                else:

                    launch_discussion(agent, other_agents, environment, lock)

                agents_seen += [a.name for a in other_agents]

    time_spent = time.time() - time_0
    return time_spent


def execute_sub_task(agent, sub_task, environment, index_of_task, index_of_sub_task, lock):
    '''
    INTPUT: agent, sub_task, environment, index_of_task, index_of_sub_task
    OUTPUT:
    if the agent is already at the destination localisation:
        the agent performs the task
        the task is added to the queue of configuration
    else:
        the agent moves to the destination localisation
        the task is added to the queue of configuration
    '''
    # A reference to count how many time is spent in the task
    counter = time.time()

    # Get the task information
    start, end, localisation, task = sub_task[0], sub_task[1], sub_task[2], sub_task[3]

    # Get the the whole localisation
    if len(localisation.split(':')) == 2:
        # Get the object to add to the localisation if it does not exist
        objects = environment.map.localisations[localisation]
        object_requested = agent.get_object_for(
            task, localisation, list(objects))
        if (object_requested):
            destination_localisation = localisation + ':' + object_requested
        else:  # object = None
            destination_localisation = localisation

        # Add it to the plan file
        with open(agent.file_path + 'plan.json', 'r') as file:
            previous_plan = json.load(file)
            file.close()
        sub_task[2] = destination_localisation
        previous_plan[index_of_task][3][index_of_sub_task] = sub_task
        with open(agent.file_path + 'plan.json', 'w') as file:
            json.dump(previous_plan, file, indent=4)
            file.close()
    else:
        destination_localisation = localisation

    try:
        object = destination_localisation.split(':')[2]
    except IndexError:
        object = None

    map = environment.map

    # Clear the sensory memory
    agent.clear_sensory_memory()

    # remove the previous event from the map (from case_details) because it is not relevant anymore
    cur_event = agent.get_current_event(lock)
    if cur_event != f'{agent.name},None':
        environment.map.remove_event(cur_event, agent)

    # Update current event
    agent.change_current_event(f'{agent.name},{task}', lock)

    # Get the coordinates (x, y) of the destination localisation
    destinations = map.get_coordinates(destination_localisation)

    # Pick the first destination that is a road
    for x, y in destinations:
        if map.grid_roads[x, y] != 0:
            x_road = x
            y_road = y
            break
    try:
        # Get the path from the current position to the destination
        path = environment.map.find_path(agent.position, (x_road, y_road))
        length_path = len(path)
    except:
        print(
            f'!!!!! No path found for {agent.name} to {destination_localisation}, You have to check the map again !!!!!')

    # Define the step velocity
    step_time = 0.25

    # Move the agent to the destination localisation in the environment
    time_spent_in_path = move_agent_to(
        agent, path, environment, step_time, lock)

    # add the new event to the map (to case_details)
    cur_event = agent.get_current_event(lock)
    environment.map.add_event(cur_event, agent)

    # Perceive the environment by adding the new information to the sensory memory
    agent.perceive(map)

    # The events already treated by the filter
    seen = list(agent.sensory_memory)

    # filter the sensory memory of the agent by adding the relevant information to the long term memory
    if len(seen) > 0:
        agent.filter_sensory_memory(seen, environment, lock)

    # Wait for the duration of the task, i.e wait till the end of the task is reached and stay active
    current_time = time.time()

    task_duration = environment.get_duration(start, end)*environment.velocity
    task_duration_left = task_duration - (current_time - counter)

    while time.time() < current_time + task_duration_left:
        # Perceive the environment by adding the new information to the sensory memory
        agents = agent.perceive(map)

        not_seen = list(set(agent.sensory_memory) - set(seen))

        agents = list(agents)

        if len(not_seen) > 0:

            # filter the sensory memory of the agent by adding the relevant information to the long term memory
            agent.filter_sensory_memory(not_seen, environment, lock)

            # Add the seen events to the seen list
            for ev in not_seen:
                seen.append(ev)

    # Add the new event to the list of configurations to be displayed
    task_time = (task_duration - step_time*length_path) * \
        environment.front_back_ratio
    if object in {"Chair left side", 'Table left side', "Bed James side", 'Console'}:
        command = 'SIT RIGHT'
    elif object in {"Chair right side", 'Table right side', "Bed John side", "Bed Elsa side", "Bed Tom side", "Bed Alice side", "Bed Sara side"}:
        command = 'SIT LEFT'
    else:
        command = 'STAY'

    environment.add_configuration_to_the_queue(
        agent.name, [task, task_time, command])
