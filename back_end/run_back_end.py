def run_back_end(env, agent, initial_plan, barrier, lock):
    '''
    This function is used to run the back-end of the simulation.
    It loops through the initial plan of the day and create sub plans for each task. and then it
    loops through the sub plans and execute them.
    '''

    index_of_task = 0
    number_of_tasks = len(initial_plan)-1
    index_of_day = 1

    while True:
        if index_of_task == 0 and index_of_day == 1:
            '''Here we create the first sub plan and then wait for the other agents to create their own sub plan .'''

            # Create sub tasks for task_i and return them
            sub_plan_i = agent.create_sub_plan(
                index_of_task, env.map.get_localisations().keys(), lock)

            # wait for all the processes to be ready
            barrier.wait()
            print(f'Process is ready for {agent.name}')

        else:
            # Create sub tasks for task_i and return them
            sub_plan_i = agent.create_sub_plan(
                index_of_task, env.map.get_localisations().keys(), lock)

        # Execute sub tasks for task_i
        executing_sub_plan = True
        number_of_sub_tasks = len(sub_plan_i)-1
        index_of_sub_task = 0

        while executing_sub_plan:
            # Execute the sub task
            sub_task = sub_plan_i[index_of_sub_task]
            agent.execute_sub_task(
                sub_task, env, index_of_task, index_of_sub_task, lock)

            if index_of_sub_task == number_of_sub_tasks:
                executing_sub_plan = False

            index_of_sub_task += 1

        # Here the first day is over
        if index_of_task == number_of_tasks:
            index_of_day += 1
            index_of_task = 0
            day_summary = agent.end_of_the_day(env, lock)
            initial_plan = agent.create_initial_plan()
            number_of_tasks = len(initial_plan)-1

        else:
            index_of_task += 1
