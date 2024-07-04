# For development purpose
from test_fcts import run_front_end_test, read_initial_plan

import multiprocessing
import concurrent.futures
from agent import Agent
from environment import Environment
from back_end.run_back_end import run_back_end
from front_end.run_front_end import run_front_end


def create_agent(agent_name, env):
    '''
    This function is used to create an agent and add it to the map.
    '''
    agent = Agent(name=agent_name)
    env.map.agents[agent_name] = agent

    # Update the case details of the map
    cases_matrix = env.map.case_details.get()
    case = cases_matrix[agent.position[0]][agent.position[1]]
    case["agents"].append(agent.name)
    cases_matrix[agent.position[0]][agent.position[1]] = case
    env.map.case_details.put(cases_matrix)

    # Create a queue of configurations for the agent
    env.queue_of_configurations[agent_name] = multiprocessing.Manager().list()

    # uplaod or create the initial plan of the day
    initial_plan = read_initial_plan(agent.file_path+'plan.json')
    # initial_plan = agent.create_initial_plan()
    return agent, initial_plan


if __name__ == "__main__":

    print('-----------------------Set up begins----------------------- \n')
    env = Environment()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks to create agents in parallel
        future1 = executor.submit(create_agent, "John", env)
        future2 = executor.submit(create_agent, 'James', env)
        future3 = executor.submit(create_agent, 'Elsa', env)
        future4 = executor.submit(create_agent, "Tom", env)
        future5 = executor.submit(create_agent, 'Alice', env)
        future6 = executor.submit(create_agent, 'Sara', env)

        # Retrieve results
        agent1, initial_plan1 = future1.result()
        agent2, initial_plan2 = future2.result()
        agent3, initial_plan3 = future3.result()
        agent4, initial_plan4 = future4.result()
        agent5, initial_plan5 = future5.result()
        agent6, initial_plan6 = future6.result()

    print(f'-----------------------Set up finished -----------------------\n')

    # Create a barrier for synchronizing the processes
    barrier = multiprocessing.Barrier(7)

    # Create a lock for the environment
    lock = multiprocessing.Lock()

    agents = [agent1, agent2, agent3, agent4, agent5, agent6]
    # Clean files
    agent1.delete()
    agent2.delete()
    agent3.delete()
    agent4.delete()
    agent5.delete()
    agent6.delete()

    initial_plans = [initial_plan1, initial_plan2,
                     initial_plan3, initial_plan4, initial_plan5, initial_plan6]
    processes = []

    for agent, initial_plan in zip(agents, initial_plans):
        process = multiprocessing.Process(
            target=run_back_end, args=(env, agent, initial_plan, barrier, lock))
        processes.append(process)
        process.start()

    # change the run_front_end_test to run_front_end to run the pygame front end
    front_end_process = multiprocessing.Process(
        target=run_front_end, args=(env, barrier))
    processes.append(front_end_process)
    front_end_process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()
