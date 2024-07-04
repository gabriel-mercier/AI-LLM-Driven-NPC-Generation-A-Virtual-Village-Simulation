import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import pytmx
from front_end.person import Person
from front_end.settings import *
from front_end.game import *


class Pygame_Map():
    def __init__(self, map_folder = 'front_end/map assets', file_name = 'map'):


        self.map_tmx = pytmx.load_pygame(f'{map_folder}/{file_name}.tmx')
        self.map_img = pygame.image.load(f'{map_folder}/{file_name}.png').convert_alpha()
        self.scale_factor = 0.5 # scale factor of the map
        self.tile_width = self.map_tmx.tilewidth
        self.tile_height = self.map_tmx.tileheight
        self.width = self.map_tmx.width * self.tile_width
        self.height = self.map_tmx.height * self.tile_height
        self.map_img_scaled = pygame.transform.scale(self.map_img, self.get_map_size()).convert_alpha()
        self.persons = pygame.sprite.Group()

    # get map size scaled
    def get_map_size(self):
        return ( self.width * self.scale_factor, self.height * self.scale_factor)
    
    # get tile size scaled
    def get_tile_size(self):
        return (self.tile_width * self.scale_factor, self.tile_height * self.scale_factor)
    
    # get map image scaled
    def get_map_img(self):
        return self.map_img_scaled
    
    # load persons from map file
    def get_persons(self):
        """
        Initialize persons and buttons from map file

        OUTPUT: return a pygame.sprite.Group of persons and the buttons associated to them for the camera

        """
        persons = pygame.sprite.Group()
        buttons = pygame.sprite.Group()
        for obj,i in zip(self.map_tmx.get_layer_by_name("agents"), range(len(self.map_tmx.get_layer_by_name("agents")))):
            person_image = self.map_tmx.get_tile_image_by_gid(obj.gid)
            if person_image : 
                person = Person(obj.name,obj.x,obj.y ,person_image, self)
                button = Agent_Button(i, person)
                persons.add(person)
                buttons.add(button)
        buttons.add(Close_Button())
        self.persons = persons
        return persons, buttons
    
    def scale_img(self):
        self.map_img_scaled = pygame.transform.scale(self.map_img, self.get_map_size()).convert_alpha()
        for person in self.persons:
            width , height = self.get_tile_size()
            person.sprite_sheet_images_scaled = {
                "Idle": pygame.transform.scale(person.sprite_sheet_images["Idle"], (24*width, 2*height)).convert_alpha(),
                "Walk": pygame.transform.scale(person.sprite_sheet_images["Walk"], (24*width, 2*height)).convert_alpha(),
                "Sit": pygame.transform.scale(person.sprite_sheet_images["Sit"], (12*width, 2*height)).convert_alpha()
            }

        
class Camera:
    def __init__(self, map):

        width, height = map.get_map_size()
        # camera position in the middle of the map
        self.camera = pygame.Rect(-(width - screen_width),0, width, height)
        self.map = map
        self.target = None
    
    def apply(self, rect):
        return rect.move(self.camera.topleft)
    
    def zoom(self,events):

        """ 
        Zoom in and zoom out with mouse wheel

        """
        pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and (self.target == None or pos[0] < screen_width - 48*5):
                if event.button == 4:
                    self.map.scale_factor = min(1, self.map.scale_factor + 0.05)
                if event.button == 5:
                    self.map.scale_factor = max(self.map.scale_factor - 0.05 , screen_height / self.map.height, screen_width / self.map.width)
                self.map.scale_img()
                break
        # change camera position to fit the map size
        if self.camera.x < -(self.camera.width - screen_width):
            self.camera.x = -(self.camera.width - screen_width)
        if self.camera.y < -(self.camera.height - screen_height):
            self.camera.y = -(self.camera.height - screen_height)
        
    def update(self,events):
        
        self.zoom(events)
        
        width, height = self.map.get_map_size()
        self.camera.width = width
        self.camera.height = height
        
        
        if self.target != None:
            x, y = self.target.get_position()
            x = -x + int(0.5 * screen_width)
            y = -y + int(0.5 * screen_height)
            # limit scrolling to map size
            x = min(0, x)  # left
            y = min(0, y)  # top
            x = max(-(width - screen_width), x)  # right
            y = max(-(height - screen_height), y)  # bottom
            self.camera.x , self.camera.y = x - 48* 5, y 
        else:
            # keyboard control without exciding the map 
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_q]:
                self.camera.x += 10
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.camera.x -= 10
            if keys[pygame.K_UP] or keys[pygame.K_z]:
                self.camera.y += 10
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.camera.y -= 10
            # limit scrolling to map size
            x, y = self.camera.x, self.camera.y
            x = min(0, x)  # left
            y = min(0, y)  # top
            x = max(-(width - screen_width), x)  # right
            y = max(-(height - screen_height), y)  # bottom
            self.camera.x , self.camera.y = x, y



    def draw(self, persons, buttons, screen):
        screen.blit(self.map.get_map_img(), self.camera)
        for person in persons:
            image = person.get_image()
            rect = person.get_rect()
            offset = person.get_offset()
            width = self.map.get_tile_size()[0]
            height = 2*self.map.get_tile_size()[1]
            screen.blit(image, self.apply(rect), (width*(offset + int(person.current_sprite)), 0, width, height))
            person.execute(screen, self)
            person.current_sprite = (person.current_sprite + 0.1) if person.current_sprite < 5.9 else 0
            
        for button in buttons:
            if self.target == None:
                if button.id != 'close':
                    screen.blit(button.image, button.rect)
            else:
                if button.id == 'close':
                    screen.blit(button.image, button.rect)
