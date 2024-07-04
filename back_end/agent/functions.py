import json
from back_end.useful_functions import get_completion
from back_end.agent.get import get_plan_status


def calculate_direction(position1, position2):
    '''
    INPUT: starting position, ending position
    OUTPUT: direction: "DOWN" / "UP" / "RIGHT" / "LEFT"
    '''
    if position1[0] == position2[0]:
        if position1[1] == position2[1] + 1:
            return "LEFT"
        else:
            return "RIGHT"
    elif position1[1] == position2[1]:
        if position1[0] == position2[0]+1:
            return "UP"
        else:
            return "DOWN"
    else:
        return None


def filter_sensory_memory(agent, events, env, discussions, lock, threshold=4, threshlod_thinking=8):
    '''
    INTPUT: agent, events, env, discussions, lock, threshold, threshlod_thinking
    OUTPUT: add the events that have an importance greater than the threshold to the long term memory 
            and think and update the emotion of the agent if the importance is greater than threshlod_thinking
    '''
    print(agent.name + str(events))
    if discussions != None:
        pass

    sub_tasks_already_done, rest_of_plan = get_plan_status(
        agent.name, agent.file_path, lock)
    with lock:
        # Get the importance of each event in the sensory memory
        file = open('back_end/prompts/sensory_memory.txt', 'r')
        prompt_filter = file.read().replace('#identity#', str(agent.get_info())).replace('#sub_tasks#', str(
            sub_tasks_already_done)).replace('#events#', str(events)).replace('#rest_of_plan#', str(rest_of_plan))
        file.close()

    prompt_filter = prompt_filter.split("###")

    message = [
        {'role': 'system',
         'content': prompt_filter[0]},
        {'role': 'user',
         'content': prompt_filter[1]},
    ]

    events_importance = get_completion(message, max_tokens=500, temperature=0)

    if not events_importance.endswith(']'):
        events_importance += ']'

    events_importance = eval(events_importance)

    # add the events that have an importance greater than the threshold to the long term memory

    for i in range(min(len(events), len(events_importance))):
        if events_importance[i] > threshold:
            if events_importance[i] >= threshlod_thinking:
                agent.think(events[i])
                agent.update_emotion(lock)
            node = events[i]
            # agent.long_term_memory.add_connected_node(node)
            agent.add_episodic(node, env.get_time_back_end(),
                               events_importance[i])


def delete(agent_name, episodic=True):
    '''
    INPUT: agent_name
    OUTPUT: clean discussion.json, agent_detected.json, current_event.json, discussion_state.json, current_emotion.json
    '''

    # Discussion
    with open('back_end/memory/discussion.json', 'r') as file:
        data = json.load(file)

    data[agent_name]["discussion_history"] = []
    data[agent_name]["current_discussion"] = ""
    data[agent_name]["summary"] = ""

    with open('back_end/memory/discussion.json', 'w') as file:
        json.dump(data, file, indent=4)

    # Agent detected
    data = {}
    with open('back_end/memory/agent_detected.json', 'w') as file:
        json.dump(data, file, indent=4)

    # Current event
    with open('back_end/memory/current_event.json', 'r') as file:
        data = json.load(file)
    data[agent_name] = f"{agent_name},None"

    with open('back_end/memory/current_event.json', 'w') as file:
        json.dump(data, file, indent=4)

    # Discussion state
    data = {}
    with open('back_end/memory/discussion_state.json', 'w') as file:
        json.dump(data, file, indent=4)

    # Current emotion
    with open('back_end/memory/current_emotion.json', 'r') as file:
        data = json.load(file)

    data[agent_name]["current_state"] = []

    with open('back_end/memory/current_emotion.json', 'w') as file:
        json.dump(data, file, indent=4)

    # episodic
    if (episodic):
        episodic = {"embeddings": {}, "node": []}

        with open(f'back_end/memory/{agent_name}/episodic.json', 'w') as file:
            json.dump(episodic, file, indent=4)


def summary_of_the_day(agent_name, file_path, lock):
    a, b = get_plan_status(agent_name, file_path, lock)
    plan = a + b
    with lock:
        file = open('back_end/prompts/day_summary.txt', 'r')
        prompt_filter = file.read().replace('#plan#', str(plan))
        file.close()

    prompt_sum = prompt_filter.split("###")

    message = [
        {'role': 'system',
         'content': prompt_sum[0]},
        {'role': 'user',
         'content': prompt_sum[1]},
    ]

    day_summary = get_completion(message, max_tokens=500, temperature=0)

    return day_summary


def end_of_the_day(agent, nb_day, env, lock):
    '''
    INPUT: None
    OUTPUT: None
    '''
    # Summary of the day
    summary = summary_of_the_day(agent.name, agent.file_path, lock)
    agent.add_episodic(f"Summary of day {nb_day} :" + summary, env.get_time_back_end(),
                       9)
    # Personnality
    agent.update_personality(summary)
    # Delete except episodic memory
    delete(agent.name, episodic=False)

    return summary
