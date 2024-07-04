import json, time

def run_front_end_test(env, barrier):
    # wait for all the processes to be ready
    barrier.wait()
    print(f'Process is ready for Front end')
    
    time.sleep(120)
    print('\n \n')
    print(env.queue_of_configurations['John'])
    print('\n \n')
    print(env.queue_of_configurations['James'])
    print('\n \n')
    print(env.queue_of_configurations['Elsa'])
    print('\n \n')
    
    with open('test.json', 'r') as file:
        test = json.load(file)
        file.close()
    
    test['John'] = list(env.queue_of_configurations['John'])
    test['James'] = list(env.queue_of_configurations['James'])
    test['Elsa'] = list(env.queue_of_configurations['Elsa'])
    
    with open('test.json', 'w') as file:
        json.dump(test, file, indent=4)
        file.close()

def read_initial_plan(path):
    with open(path, 'r') as file:
        initial_plan = json.load(file)
        file.close()
    return initial_plan

def print_agent(agent_name, txt):
    colors = ['\033[94m', '\033[92m', '\033[91m', '\033[0m']
    
    if agent_name == 'Elsa':
        print(f'{colors[0]} {txt} {colors[-1]}')
    elif agent_name == 'James':
        print(f'{colors[1]} {txt} {colors[-1]}')
    else:
        print(f'{colors[2]} {txt} {colors[-1]}')
