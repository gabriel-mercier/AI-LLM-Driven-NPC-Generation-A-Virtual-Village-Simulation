from back_end.useful_functions import get_completion, get_duration, add_minutes_to_time
from back_end.agent.get import get_plan_status,get_relationship
from back_end.agent.memory_extraction import reflection_daily
import json
import random


def extract_info_plan(file_path, treshold=6):
    '''
    INPUT: file path
    OUTPUT: extract information from the episodic memory and return it
    '''

    importants_events = []
    try:
        with open(file_path + 'episodic.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"file episodic cannot be found")
        return ""
    if 'node' in data and data['node']:
        for node in data['node']:
            _, event, importance = node
            if importance > treshold:
                importants_events.append(event)
        if importants_events:
            return " Here is important information/event(s) about the agent and his/her past: " + str(importants_events) + "."
        else:
            return ""
    return ""


def create_initial_plan(info, file_path):
    '''
    INTPUT: information from agent identity and the file path where the plan will be saved
    OUTPUT: initial plan in the form of json and return it
    '''

    info += extract_info_plan(file_path)
    with open('back_end/prompts/initial_plan.txt', 'r') as file:
        prompt_initial_plan = file.read().replace('#info#', str(info)).split("###")
        file.close()

    message = [
        {'role': 'system',
         'content': prompt_initial_plan[0]},
        {'role': 'user',
         'content': prompt_initial_plan[1]}
    ]

    plan = get_completion(message, max_tokens=500,
                          temperature=0, format={"type": "json_object"})

    plan = json.loads(plan)["plan_of_the_day"]
    with open(file_path + 'plan.json', 'w') as file:
        json.dump(plan, file, indent=4)
        file.close()

    return plan


def create_sub_plan(i, agent, localisations, lock):
    '''
    INTPUT: the task i for which the sub plan will be created, the file path where the plan will be saved, the localisations of the agent
    OUTPUT: create sub plan in the form of json and save it in memory and return it
    '''
    info = agent.get_info()
    file_path = agent.file_path

    task = i

    with open(file_path + 'plan.json', 'r') as file:
        plan = json.load(file)
        file.close()

    task_i = plan[task]

    # If sub plan already exists
    if len(task_i) == 4:
        return task_i[3]
    else:
        sub_tasks_already_done, rest_of_plan = get_plan_status(
            agent.name, agent.file_path, lock)

        with open('back_end/prompts/sub_plan.txt', 'r') as file:
            prompt_sub_plan = file.read().replace('#start_time#', task_i[0]).replace('#end_time#', task_i[1]).replace('#task#', task_i[2]).replace('#localisations#', str(
                localisations)).replace('#info#', str(info)).replace('#sub_tasks_already_done#', str(sub_tasks_already_done)).replace('#rest_of_plan#', str(rest_of_plan)).split("###")
            file.close()

        message = [
            {'role': 'system',
             'content': prompt_sub_plan[0]},
            {'role': 'user',
             'content': prompt_sub_plan[1]}
        ]
        sub_plan = get_completion(message, max_tokens=500, temperature=0, format={
                                  "type": "json_object"})
        sub_plan = json.loads(sub_plan)["sub_tasks"]

        # Verify if all the localisations are valid
        for sub_task in sub_plan:
            localisation = sub_task[2]
            if localisation not in localisations:
                print(f"Localisation :{localisation} is not valid")
                with open('back_end/prompts/sub_plan_error.txt', 'r') as file:
                    prompt_localisation = file.read().replace(
                        '#localisations#', str(localisations))
                    message_loc = [
                        {'role': 'system', 'content': prompt_localisation},]
                    localisation = get_completion(
                        message_loc, max_tokens=500, temperature=0)
                    if ('"' in localisation):
                        localisation = localisation.replace('"', '')
                    print(f"New localisation :{localisation}")
                    if localisation not in localisations:
                        print(f"New localisation :{localisation} is not valid")
                        localisation = random.choice(localisations.keys())
                        print(
                            f"New localisation :{localisation} is chosen randomly")
                    file.close()
                sub_task[2] = localisation

        plan[task].append(sub_plan)
        with open(file_path + 'plan.json', 'w') as file:
            json.dump(plan, file, indent=4)
            file.close()

        return sub_plan


def get_object_for(task, localisation, objects):
    '''
    INTPUT: agent, task, objects
    OUTPUT: object to add to the building:hall to have a complete localisation
    '''
    file = open('back_end/prompts/get_object.txt', 'r')
    prompt_object = file.read().replace('#task#', task).replace(
        '#objects#', str(objects)).replace('#localisation#', localisation).split("###")
    file.close()
    message = [
        {'role': 'system',
         'content': prompt_object[0]},
        {'role': 'user',
         'content': prompt_object[1]}
    ]
    object = get_completion(message, max_tokens=500, temperature=0)

    if object not in objects:
        new_prompt = f'Choose the most appropriate word from this list {objects} that is close to the task: {task}. Your answer must be only one word from the list provided.'
        message = [
            {'role': 'user',
             'content': new_prompt},
        ]
        object = get_completion(message, model="gpt-4",
                                max_tokens=500, temperature=0)

    if object not in objects:
        object = None

    return object


def insert_discussion(agent, disc_length, disc=""):
    '''
    INTPUT: disc, disc_length
    OUTPUT: insert the discussion in the plan
    '''
    with open("back_end/memory/current_event.json", 'r') as file:
        current_event = json.load(file)

    sub_task_discription = current_event[agent.name].split(",")[1]

    with open(agent.file_path + "plan.json", 'r') as file:
        plan = json.load(file)

    current_sub_task_index = -1
    i = 0
    while (len(plan[i]) == 4 and current_sub_task_index == -1):
        for j in range(len(plan[i][3])):
            if plan[i][3][j][3] == sub_task_discription:
                current_sub_task_index = j
                break
        i += 1

    current_task_index = i - 1

    # modify current task end time
    plan[current_task_index][1] = add_minutes_to_time(
        plan[current_task_index][1], disc_length)
    # modify the rest of the tasks
    # get the task with the maximum duration
    rest_of_tasks = plan[current_task_index + 1: len(plan)-1]

    max_task = max(rest_of_tasks, key=lambda task: get_duration(
        task[0], task[1]))

    max_task_index = rest_of_tasks.index(max_task)

    # modify the rest of the tasks
    for i in range(current_task_index + 1, len(plan)):
        if i < max_task_index:
            plan[i][0] = add_minutes_to_time(plan[i][0], disc_length)
            plan[i][1] = add_minutes_to_time(plan[i][1], disc_length)
        elif i == max_task_index:
            plan[i][0] = add_minutes_to_time(plan[i][0], disc_length)
        else:
            break

    # modify current sub_task end time
    plan[current_task_index][3][current_sub_task_index][1] = add_minutes_to_time(
        plan[current_task_index][3][current_sub_task_index][1], disc_length)
    # modify the rest of the sub tasks
    for j in range(current_sub_task_index + 1, len(plan[current_task_index][3])):
        plan[current_task_index][3][j][0] = add_minutes_to_time(
            plan[current_task_index][3][j][0], disc_length)
        plan[current_task_index][3][j][1] = add_minutes_to_time(
            plan[current_task_index][3][j][1], disc_length)

    with open(agent.file_path + 'plan.json', 'w') as file:
        json.dump(plan, file, indent=4)

def new_day(agent,time):

    ### conclusion of the day before
    info_episodic = extract_info_plan(agent.file_path)
    reflections = reflection_daily(agent,time)
    relationship = ""
    info_agent = agent.get_info()
    emotions = agent.print_emotions()

    with open('back_end/memory/identity.json', 'r') as file:
        data = json.load(file)
    names = list(data.keys())

    for name in names:
        if (name!=agent.name):
            relationship += get_relationship(agent.filepath,agent.name,name)
    
    with open("backend/prompts/new_day.txt",'r') as file:
        prompt = file.read()
    
    prompt = prompt.replace("#info_agent#",info_agent).replace("#relationship#",relationship).replace("#emotions#",emotions).replace("#info_episodic#",info_episodic).replace("#reflections#",reflections)
    prompt = prompt.split("###")
    message = [ {'role': 'system',
         'content': prompt[0]},
        {'role': 'user',
         'content': prompt[1]}]
    plan = get_completion(message,model="gpt-4",max_tokens=500, temperature=0,format={"type": "json_object"})
    plan = json.loads(plan)["plan_of_the_day"]
    with open(agent.file_path + 'plan.json', 'w') as file:
        json.dump(plan, file, indent=4)
        file.close()

    return plan


    
    

