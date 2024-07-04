import pygame
import random

class Rain(pygame.sprite.Sprite):
    def __init__(self, window_width, window_height, image, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(image, (width,height))
        self.rect = self.image.get_rect()
        self.speedx = 3
        self.speedy = random.randint(5,25)
        self.rect.x = random.randint(-10, window_width)
        self.rect.y = random.randint(-5, window_height)
        self.window_width = window_width
        self.window_height = window_height
        self.status = False

    def update(self):
        self.status = not self.status

        if self.status: 
            if self.rect.bottom > self.window_height:
                self.speedx = 3
                self.speedy = random.randint(5,25)
                self.rect.x = random.randint(-self.window_width, self.window_width)
                self.rect.y = random.randint(-self.window_height,-5)
                
            self.rect.x = self.rect.x + self.speedx
            self.rect.y = self.rect.y + self.speedy            