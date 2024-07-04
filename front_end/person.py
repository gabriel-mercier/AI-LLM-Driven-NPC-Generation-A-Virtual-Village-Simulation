import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from front_end.settings import *

class Person(pygame.sprite.Sprite):
    def __init__(self,name, x, y, image, map):
        super().__init__()
        self.name = name
        self.x = x
        self.y = y
        self.image = image
        self.map = map
        self.current_task = "Idle" # current task of the agent
        self.begin_execution = 0  # time when the execution begins
        self.execute_duration = 0  # duration of execution
        self.walk_duration = 0  # duration of walking
        self.moving = False  # whether the sprite is moving
        self.steps = 0  # number of steps taken

        # animation details
        self.sprite_sheet_path = f"front_end/png/{name}"
        self.sprite_sheet_images = {
            "Idle": pygame.image.load(f"{self.sprite_sheet_path}/Idle.png").convert_alpha(),
            "Walk": pygame.image.load(f"{self.sprite_sheet_path}/Walk.png").convert_alpha(),
            "Sit": pygame.image.load(f"{self.sprite_sheet_path}/Sit.png").convert_alpha(),
        }
        tile_width, tile_height = self.map.get_tile_size()  
        self.sprite_sheet_images_scaled = {
            "Idle": pygame.transform.scale(self.sprite_sheet_images["Idle"], (24*tile_width, 2*tile_height)).convert_alpha(),
            "Walk": pygame.transform.scale(self.sprite_sheet_images["Walk"], (24*tile_width, 2*tile_height)).convert_alpha(),
            "Sit": pygame.transform.scale(self.sprite_sheet_images["Sit"], (12*tile_width, 2*tile_height)).convert_alpha(),
        }
        self.current_sprite = 0
        self.current_status = "Idle"
        self.direction = "DOWN"

    def get_offset(self):
        if self.current_status == "Sit" and self.direction == "LEFT":
            return 6
        if self.direction == "UP":
            return 6
        elif self.direction == "DOWN":
            return 18
        elif self.direction == "LEFT":
            return 12
        elif self.direction == "RIGHT":
            return 0

    # get agent position
    def get_position(self):
        return self.x * self.map.scale_factor, self.y * self.map.scale_factor
    
    # get agent image scaled 
    def get_image(self):
        image = self.sprite_sheet_images_scaled[self.current_status]
        return image
    
    # get agent image rect (position where the image is drawn)
    def get_rect(self):
        image_rect = self.get_image().get_rect()
        image_rect.x = self.x * self.map.scale_factor
        image_rect.y = self.y * self.map.scale_factor
        return image_rect

    # Draw agent task if current_task is not None
    def execute(self , screen, camera):

        tile_width, tile_height = self.map.get_tile_size()

        font = pygame.font.SysFont(None, int(tile_height))

        if self.current_task != None:
            task = self.current_task
            if len(task) > 20:
                task = task[:20] + "..."   

            # Get agent position
            agent_x, agent_y = self.get_position()

            # Render the task text
            text_surface = font.render(task, True, black)
            
            # Get text size
            text_width, text_height = font.size(task)

            # Calculate text box position 
            padding = tile_height/4
            text_box_rect = pygame.Rect(agent_x + tile_width//2 - text_width//2 - padding, agent_y - text_height - padding , text_width + padding * 2, text_height + padding * 2)
            text_surface_rect = pygame.Rect(agent_x + tile_width//2 - text_width//2, agent_y - text_height, text_width, text_height)
            
            # Draw text box
            pygame.draw.rect(screen, white, camera.apply(text_box_rect))
            # Draw text box border
            pygame.draw.rect(screen, black, camera.apply(text_box_rect), 2)
            # Draw text
            screen.blit(text_surface, camera.apply(text_surface_rect))

    # Update agent position
    def move(self,command = None):
        self.direction = command
        x_move = 0
        y_move = 0
        # Check if there is a command to move (4 * tile_height pixels per second <=> in 1/4 second move 1 tile <=> in 1 second move 4 tiles)
        if command:
            if command == 'UP':
                y_move -= 4*self.map.tile_height//FPS
            elif command == 'DOWN':
                y_move += 4*self.map.tile_height//FPS
            elif command == 'LEFT':
                x_move -= 4*self.map.tile_height//FPS
            elif command == 'RIGHT':
                x_move += 4*self.map.tile_height//FPS
            else:
                pass
        else:
            pass
        self.x += x_move
        self.y += y_move
    
    def update(self,commands = None, time = None):
        
        # Check if there is a current task
        if self.current_task != None:
             # Check if execution duration is completed
            if time - self.begin_execution >= self.execute_duration:
                self.current_task = None
            else :            
                return
            
        # Check if the person is moving
        if self.moving != False:
            # Check if the person has completed its movement
            if self.steps > FPS//4:
                self.moving = False
                self.steps = 0
            # If not, continue moving and update the number of steps taken
            else:
                self.move(self.moving)
                self.steps += 1
                return
            
        # if there is no current task, or the execution duration is completed
        # Get the next command from the list
        if len(commands[self.name]) == 0:
            self.current_status = "Idle" if self.current_status != "Sit" else "Sit"
            return
        else:
            command = commands[self.name].pop(0)
            # Check if the command indicates staying in place
            if command[-1] == "STAY":
                self.current_status = "Idle"
                # Update execution details
                self.begin_execution = time
                self.execute_duration = (command[1])
                # Execute the task
                self.current_task = command[0]
                self.walk_duration = 0
            elif command[-1] == "SIT LEFT":
                self.current_status = "Sit"
                self.direction = "LEFT"
                # Update execution details
                self.begin_execution = time
                self.execute_duration = (command[1])
                # Execute the task
                self.current_task = command[0]
                self.walk_duration = 0
            elif command[-1] == "SIT RIGHT":
                self.current_status = "Sit"
                self.direction = "RIGHT"
                # Update execution details
                self.begin_execution = time
                self.execute_duration = (command[1])
                # Execute the task
                self.current_task = command[0]
                self.walk_duration = 0
            else:
                self.current_status = "Walk"
                # Move the sprite
                self.moving = command[-1]
                # Update walking duration
                self.walk_duration += 1/4


        
        

    
            

           


