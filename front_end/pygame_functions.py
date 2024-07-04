import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import pytmx
from front_end.person import Person
from datetime import datetime, timedelta
from front_end.settings import *

def decompose_text(text, max_length):
    text = text.split()
    lines = []
    line = ""
    for word in text:
        if len(line) + len(word) < max_length:
            line += word + " "
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)
    return lines

def get_time(start_time, duration_minutes):
    # Convert the start time to a datetime object
    start_time_obj = datetime.strptime(start_time, "%H:%M")

    # Calculate the end time by adding the duration in milliseconds
    end_time_obj = start_time_obj + timedelta(minutes=duration_minutes)

    # Format the end time as a string in the HH:MM format
    end_time = end_time_obj.strftime("%H:%M")

    return end_time

def Draw_time(time, velosity, screen, FPS):
 
    # loading in the middle of the screen
    font = pygame.font.SysFont(None, 24 )
    
    real_time = time / velosity
    text = get_time("07:00",real_time)
    
    # Get text surface and rectangle
    text_surface = font.render(text, True, black)
    text_rect = text_surface.get_rect()

    # Set the position of the rectangle (top-left corner)
    text_rect.topleft = (10, 10)
     
    # Draw
    pygame.draw.rect(screen, white, text_rect)  # Draw the rectangle
    screen.blit(text_surface, text_rect.topleft)  # Draw the text on the rectangle

    # Draw the FPS
    text = f"FPS: {int(FPS)}"
    text_surface = font.render(text, True, black)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (10, 40)
    pygame.draw.rect(screen, white, text_rect)
    screen.blit(text_surface, text_rect.topleft)


def loading_screen(screen,debut):
    # loading in the middle of the screen
    if debut == False:
        welcome_img = pygame.image.load("front_end/png/THE VILLAGE loading.png")
        welcome_img = pygame.transform.scale(welcome_img, (screen_width, screen_height)).convert_alpha()
        screen.blit(welcome_img, (0, 0))
    else:
        welcome_img = pygame.image.load("front_end/png/THE VILLAGE.png")
        welcome_img = pygame.transform.scale(welcome_img, (screen_width, screen_height)).convert_alpha()
        screen.blit(welcome_img, (0, 0))


def start_screen():
    x, y = pygame.mouse.get_pos()
    width_scale = screen_width / 1280
    height_scale = screen_height / 720
    if 464 * width_scale < x < 761 * width_scale and 503 * height_scale < y < 657 * height_scale:
        if pygame.mouse.get_pressed()[0]:
            return True 
    return False



    

    

