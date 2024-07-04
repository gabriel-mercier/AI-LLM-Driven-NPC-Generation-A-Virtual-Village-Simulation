import json
import time
from back_end.useful_functions import get_completion
from back_end.agent.detect import interact
from back_end.agent.get import get_plan_status, get_current_event, get_relationship
from back_end.agent.plan import insert_discussion


def hear_discussion(agent, agent_asking_me, environment, lock):
    '''
    INPUT : agent, agent_asking_me, environment
    OUTPUT : outperform the process that the agent listen to the discussion between the agent and the agent_asking_me
    '''
    lock.acquire()
    try:
        with open('back_end/memory/discussion_state.json', 'r') as file:
            info = json.load(file)
            file.close()
    finally:
        lock.release()

    state = info[agent_asking_me]

    # Time to wait
    ref_time_to_wait = time.time()
    if state[0] == "WAITING":
        while True:
            lock.acquire()
            try:
                with open('back_end/memory/discussion_state.json', 'r') as file:
                    info = json.load(file)
                    file.close()
            finally:
                lock.release()

            state = info[agent_asking_me]
            if state[0] != "WAITING" or state[0] == "Ignore":
                break
            time.sleep(0.3)

        time_to_wait = time.time() - ref_time_to_wait
        environment.add_configuration_to_the_queue(agent.name, [
            f'{agent.name} is talking with {agent_asking_me}', time_to_wait*environment.front_back_ratio, 'STAY'])

    if state[0] == "TALKING":
        time_of_discussion = state[1]

        # modify plan
        insert_discussion(agent, time_of_discussion)
        environment.add_configuration_to_the_queue(agent.name, [
            f'{agent.name} is talking with {agent_asking_me}', time_of_discussion*environment.front_back_ratio, 'STAY'])
        time.sleep(time_of_discussion)


def launch_discussion(agent, other_agents, environment, lock):
    '''
    INTPUT:  agent, orther_agents, environment
    OUTPUT: outperform the process that the agent discuss with the other agents
    '''
    # Add the agents that I have seen
    lock.acquire()
    try:
        with open('back_end/memory/agent_detected.json', 'r') as file:
            info = json.load(file)
            file.close()
    finally:
        lock.release()
    info[agent.name] = [a.name for a in other_agents]

    lock.acquire()
    try:
        with open('back_end/memory/agent_detected.json', 'w') as file:
            json.dump(info, file, indent=4)
            file.close()
    finally:
        lock.release()

    # Update the state of the discussion
    lock.acquire()
    try:
        with open('back_end/memory/discussion_state.json', 'r') as file:
            info = json.load(file)
            file.close()
        info[agent.name] = ["WAITING", 0]
        with open('back_end/memory/discussion_state.json', 'w') as file:
            json.dump(info, file, indent=4)
            file.close()
    finally:
        lock.release()

    # Reference time to wait
    ref_time_to_wait = time.time()

    interact_answer = interact(agent, [other_agents[0]], lock)
    print(f'interact_answer: {interact_answer}')

    if interact_answer != 'NO':

        other_agent = environment.map.agents[interact_answer]
        disc_time = agent.get_discussion(other_agent, lock)

        # Add the waiting time to the configuration queue
        time_to_wait = time.time() - ref_time_to_wait
        environment.add_configuration_to_the_queue(agent.name, [
                                                   f'{agent.name} is talking with {interact_answer}', time_to_wait*environment.front_back_ratio, 'STAY'])

        # Update the current event of the agent
        cur_event = agent.change_current_event(
            f'{agent.name},talking with {interact_answer}', lock)
        environment.map.add_event(cur_event, agent)

        lock.acquire()
        try:
            # Update the state of the discussion
            with open('back_end/memory/discussion_state.json', 'r') as file:
                info = json.load(file)
                file.close()
            info[agent.name] = ["TALKING", disc_time]
            with open('back_end/memory/discussion_state.json', 'w') as file:
                json.dump(info, file, indent=4)
                file.close()
        finally:
            lock.release()

        # Add the discussion to the configuration queue
        insert_discussion(agent, disc_time)
        environment.add_configuration_to_the_queue(agent.name, [
                                                   f'{agent.name} is talking with {interact_answer}', disc_time*environment.front_back_ratio, 'STAY'])

        # Wait for the duration of the discussion
        time.sleep(disc_time)

        lock.acquire()
        try:
            # discussion is over
            with open('back_end/memory/agent_detected.json', 'r') as file:
                info = json.load(file)
                file.close()
            del info[agent.name]
            with open('back_end/memory/agent_detected.json', 'w') as file:
                json.dump(info, file, indent=4)
                file.close()

            with open('back_end/memory/discussion_state.json', 'r') as file:
                info = json.load(file)
                file.close()
            del info[agent.name]
            with open('back_end/memory/discussion_state.json', 'w') as file:
                json.dump(info, file, indent=4)
                file.close()
        finally:
            lock.release()

        '''# Add the discussion to the sensory memory of the agent
        summarize_discussion = summarize_discussion(
            discussion, agent.name, other_agent.name)
        agent.sensory_memory.add(summarize_discussion)'''

    else:
        lock.acquire()
        try:
            with open('back_end/memory/discussion_state.json', 'r') as file:
                info = json.load(file)
                file.close()
            info[agent.name] = ["Ignore", 0]
            with open('back_end/memory/discussion_state.json', 'w') as file:
                json.dump(info, file, indent=4)
                file.close()

            # discussion is over
            with open('back_end/memory/agent_detected.json', 'r') as file:
                info = json.load(file)
                file.close()
            del info[agent.name]
            with open('back_end/memory/agent_detected.json', 'w') as file:
                json.dump(info, file, indent=4)
                file.close()

            with open('back_end/memory/discussion_state.json', 'r') as file:
                info = json.load(file)
                file.close()
            del info[agent.name]
            with open('back_end/memory/discussion_state.json', 'w') as file:
                json.dump(info, file, indent=4)
                file.close()
        finally:
            lock.release()

        # Add the waiting time to the configuration queue
        time_to_wait = time.time() - ref_time_to_wait
        environment.add_configuration_to_the_queue(agent.name, [
                                                   f'{agent.name} is talking with {other_agents[0]}', time_to_wait*environment.front_back_ratio, 'STAY'])


def get_discussion(agent, other_agent, lock):
    '''
    INTPUT: agent, other_agent_name
    OUTPUT: the discussion between the agent and the other_agent
    '''
    sub_tasks_already_done_1, rest_of_plan_1 = get_plan_status(
        agent.name, agent.file_path, lock)
    sub_tasks_already_done_2, rest_of_plan_2 = get_plan_status(
        other_agent.name, other_agent.file_path, lock)

    file = open('back_end/prompts/discussion.txt', 'r')
    prompt_interact = file.read().replace(
        '#agent_name_1#', str(agent.name)).replace(
        '#agent_name_2#', str(other_agent.name)).replace(
        '#relationship_1_to_2#', str(agent.get_relationship(other_agent.name))).replace(
        '#relationship_2_to_1#', str(get_relationship(other_agent.file_path, other_agent.name, agent.name))).replace(
        '#important_1#', str(agent.retrieve_episodic(get_current_event(agent.name, lock).split(',')[1], 4)[0][0])).replace(
        '#important_2#', str(other_agent.retrieve_episodic(get_current_event(other_agent.name, lock).split(',')[1], 4)[0][0])).replace(
        '#sub_tasks_already_done_1#', str(sub_tasks_already_done_1)).replace(
        '#sub_tasks_already_done_2#', str(sub_tasks_already_done_2)).replace(
        '#rest_of_plan_1#', str(rest_of_plan_1)).replace(
        '#rest_of_plan_2#', str(rest_of_plan_2))
    file.close()

    prompt_interact = prompt_interact.split("###")

    message = [
        {'role': 'system',
         'content': prompt_interact[0]},
        {'role': 'user',
         'content': prompt_interact[1]},
    ]
    discussion = get_completion(message)

    lock.acquire()
    try:
        with open('back_end/memory/discussion.json', 'r') as file:
            data = json.load(file)
            file.close()

        data[agent.name]["current_discussion"] = discussion
        data[agent.name]["discussion_history"].append(discussion)
        data[other_agent.name]["current_discussion"] = discussion
        data[other_agent.name]["discussion_history"].append(discussion)

        with open('back_end/memory/discussion.json', 'w') as file:
            json.dump(data, file, indent=4)
            file.close()
    finally:
        lock.release()

    summary = summarize_discussion(discussion, agent.name, other_agent.name)

    agent.sensory_memory.add("Discussion : " + summary)

    disc_time = len(discussion)*0.01
    return disc_time


def summarize_discussion(discussion, agent_name, other_agent_name):
    '''
    INTPUT: discussion
    OUTPUT: the summary of the discussion
    '''
    file = open('back_end/prompts/summarize_discussion.txt', 'r')
    prompt_summarize = file.read().replace('#discussion#', str(discussion)).replace(
        '#agent_name#', str(agent_name)).replace('#other_agent_name#', str(other_agent_name))
    file.close()

    prompt_summarize = prompt_summarize.split("###")

    message = [
        {'role': 'system',
         'content': prompt_summarize[0]},
        {'role': 'user',
         'content': prompt_summarize[1]},
    ]

    summary = get_completion(message)

    try:
        with open('back_end/memory/discussion.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"file discussion cannot be found")
        return

    data[agent_name]["summary"] = summary
    data[other_agent_name]["summary"] = summary

    with open('back_end/memory/discussion.json', 'w') as file:
        json.dump(data, file, indent=4)

    return summary
