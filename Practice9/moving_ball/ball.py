import pygame
class Ball:
    def __init__(self, screen_width, screen_height):
        self.radius=25
        self.color=(255,0,0)
        self.x=screen_width // 2 # start at center
        self.y=screen_height // 2
        self.speed=20
        self.screen_width=screen_width
        self.screen_height=screen_height

    def move(self, direction):
        if direction=="UP":
            if self.y-self.radius-self.speed>=0:
                self.y-=self.speed

        elif direction=="DOWN":
            if self.y+self.radius+self.speed<=self.screen_height:
                self.y+=self.speed

        elif direction=="LEFT":
            if self.x - self.radius - self.speed >=0:
                self.x-=self.speed

        elif direction=="RIGHT":
            if self.x+self.radius+self.speed <=self.screen_width:
                self.x+=self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)