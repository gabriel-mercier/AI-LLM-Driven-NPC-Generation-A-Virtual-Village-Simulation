import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from front_end.settings import *
from front_end.pygame_functions import decompose_text
from front_end.effects import *
import json

class Button(pygame.sprite.Sprite):
    def __init__(self,id, x, y, width, height, image):
        super().__init__()
        self.image = pygame.transform.scale(image, (width,height))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.id = id

class Agent_Button(Button):
    def __init__(self, number, person):
        x = screen_width - 24
        y = 48 * number
        self.id = person.name
        super().__init__(id,x, y, 24, 48, person.image)
        self.person = person

    def update(self, camera):
        if camera.target == None:
            pos = pygame.mouse.get_pos()
            # get the button that is clicked on
            if self.rect.collidepoint(pos):
                if pygame.mouse.get_pressed()[0]:
                    camera.target = self.person
 
class Close_Button(Button):
    def __init__(self):
        x = screen_width - 24
        y = 0
        image = pygame.image.load("front_end/png/close.png").convert_alpha()
        id = "close"
        super().__init__(id, x, y, 24, 24, image)

    def update(self, camera):
        if camera.target != None:
            pos = pygame.mouse.get_pos()
            # get the button that is clicked on
            if self.rect.collidepoint(pos):
                if pygame.mouse.get_pressed()[0]:
                    camera.target = None        

class Effect_Button(Button):
    def __init__(self, screen):
        self.screen = screen
        id = "rain"
        x = 0
        y = 0
        image = pygame.image.load("front_end/png/rain.png").convert_alpha()
        super().__init__(id, x, y, 48, 24, image)

        self.image = pygame.transform.scale(image, (12,24))
        self.rect = pygame.Rect(0, screen_height // 2, 24, 48)
        self.rect.x = 0
        self.rect.y = screen_height // 2
        
        
        self.objects = pygame.sprite.Group()
        for _ in range(1000):
            rain = Rain(screen_width, screen_height, self.image, 6, 12)
            self.objects.add(rain)

        self.status = False

    def update(self):
        pos = pygame.mouse.get_pos()
        # get the button that is clicked on
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0]:
                self.status = not self.status

    def draw(self, screen):
        # botton_text = pygame.font.SysFont(None, 24).render(self.id, True, black)
        # botton_rect = pygame.Rect(self.rect.x, self.rect.y, 24, 48)
        pygame.draw.rect(screen, white, self.rect, 0, 5)
        pygame.draw.rect(screen, black, self.rect, 2, 5)

        screen.blit(self.image, (self.rect.x + 6, self.rect.y + 12))
        if self.status:
            self.objects.update()
            self.objects.draw(screen)

class Person_menu(pygame.sprite.Sprite):
    """

    A menu that displays the person's name and image at the right of the screen when the person is selected
    it shows also 3 onglets: info, memory, and chat
    
    """
    def __init__(self,camera,screen):
        super().__init__()
        self.camera = camera
        self.screen = screen
        self.image = pygame.Surface((5* 48, screen_height))
        self.image.fill(white)
        self.rect = self.image.get_rect()
        self.rect.x = screen_width - self.rect.width
        self.rect.y = 24
        self.font = pygame.font.SysFont(None, 32)
        self.text_color = black
        self.text_color_selected = red
        self.onglets = ["identity", "memory", "chat"]
        self.selected = "identity"
        self.scroll = 0

    def update(self,events):
        pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and self.camera.target != None and pos[0] > screen_width - 48*5:
                if event.button == 4:
                    self.scroll -= 1
                if event.button == 5:
                    self.scroll += 1
            self.scroll = max(0, self.scroll)


        if self.camera.target != None:
            # get the onglet that is clicked on
            for onglet in self.onglets:
                if self.get_onglet(onglet)[1].collidepoint(pos):
                    if pygame.mouse.get_pressed()[0]:
                        self.selected = onglet
                        self.scroll = 0
                        break

    def get_text(self, onglet):
        # get the text of the onglet from json and put it in a rect
        font = pygame.font.SysFont(None, 18)
        texts = []
        rects = []
        if onglet == "identity":
            file_location = "back_end/memory/identity.json"
            with open(file_location) as json_file:
                data = {"current task": self.camera.target.current_task}
                data.update(json.load(json_file)[self.camera.target.name])

            for key in data:
                if not key in ["personnality", "personnality explanation", "initial_position"]:
                    texts += decompose_text(key.upper() + ": " + str(data[key]),40)
        elif onglet == "memory":
            file_location = f"back_end/memory/{self.camera.target.name}/episodic.json"
            with open(file_location) as json_file:
                data = json.load(json_file)
                json_file
            data = data["node"]
            for i in range(len(data)):
                texts += decompose_text(f'{data[i][0]}: {data[i][1]}',40)
        elif onglet == "chat":
            file_location = f"back_end/memory/discussion.json"
            with open(file_location) as json_file:
                data = json.load(json_file)[self.camera.target.name]["current_discussion"]
                data = data.split("\n")
            for i in range(1,len(data)):
                texts += decompose_text(data[i],40)
        
        
        for i in range(len(texts)):
            text = font.render(texts[i], True, self.text_color)
            rect = text.get_rect()
            rect.x = self.rect.x + 10
            rect.y = self.rect.y + 150 + 20 * i
            texts[i] = text
            rects.append(rect)
        return texts, rects

    def get_onglet(self, onglet):
        font = pygame.font.SysFont(None, 24)
        if self.selected == onglet:
            text = font.render(onglet, True, self.text_color_selected)
        else:
            text = font.render(onglet, True, self.text_color)

        n = (5 * 48) // len(self.onglets)
        rect = text.get_rect()
        rect.x = self.rect.x + self.onglets.index(onglet) * n + n//2 - rect.width//2
        rect.y = self.rect.y + 100

        return text, rect 

    
    
    def draw(self):
        # draw the menu with the onglets and the text of the selected onglet and with the scroll
        if self.camera.target != None:
            self.screen.blit(self.image, self.rect)
            image = self.camera.target.image
            self.screen.blit(image, (self.rect.x +24, self.rect.y -24 ))
            text = self.font.render(self.camera.target.name, True, self.text_color)
            self.screen.blit(text, (self.rect.x + 100, self.rect.y + 30))
            count = 0
            for i in range(len(self.onglets)):
                text , rect = self.get_onglet(self.onglets[i])
                self.screen.blit(text, rect)
                if self.selected == self.onglets[i]:
                    for text, rect in zip(self.get_text(self.onglets[i])[0], self.get_text(self.onglets[i])[1]):
                        if count >= self.scroll:
                            self.screen.blit(text, rect.move(0, -20 * self.scroll))
                        count += 1
                    
                        