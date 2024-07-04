import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from front_end.settings import *
from front_end.map import *
from front_end.pygame_functions import *

def run_front_end(env, barrier=None):
    # Wait for the other processes to finish setting up
    if barrier != None:
        barrier.wait()

    # initialize pygame and create window
    pygame.init()

    clock = pygame.time.Clock()
    
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Village Map')

    # set up map, person, buttons and camera
    map = Pygame_Map()
    agents, buttons = map.get_persons()
    camera = Camera(map)
    menu = Person_menu(camera,screen)

    effects = Effect_Button(screen)

    debut = False
    start_status = False
    # game loop
    running = True

    while running:

        
        clock.tick(FPS)
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # get the commands from the back-end
        
        commands = env.queue_of_configurations
        # loading screen while the execution has not begun (len(commands) < 1)
        if debut == False:
            loading_screen(screen,debut)
            debut = True
            for person in agents:
                if len(commands[person.name]) < 10:
                    debut = False
                    break
        elif start_status == False:
            loading_screen(screen,debut)
            start_status = start_screen()

        else:   


            # calculate the min number of commands for all the persons
            #n = min([len(commands[person.name]) for person in agents])
            # Check if there are commands to execute
            #if n > 0:
                # Update the agents, the time
            agents.update(commands, env.front_end_time)
            env.front_end_time += 1/FPS

            menu.update(events) # Update the menu 

            buttons.update(camera) # Update the buttons (follow the agents)
            
            
            camera.update(events)# Update the camera (follow the agents or move with the arrow keys and zoom with the mouse wheel)

            effects.update()

            # Draw everything
            
            camera.draw(agents, buttons, screen) # Draw the map, the agents (Tasks) and the buttons

            menu.draw() # Draw the menu
            
            # Draw the time
            Draw_time(env.front_end_time, env.front_end_time_velocity, screen, clock.get_fps())

            effects.draw(screen)
        
        # *after* drawing everything, update the display
        pygame.display.update()

    pygame.quit()