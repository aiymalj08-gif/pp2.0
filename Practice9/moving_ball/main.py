import pygame
from ball import Ball

pygame.init() # initialize pygame

SCREEN_WIDTH=800
SCREEN_HEIGHT=600
screen=pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Moving BALL Game!")

white=(255, 255, 255)

clock=pygame.time.Clock()

ball=Ball(SCREEN_WIDTH, SCREEN_HEIGHT)

running=True

while running:
    screen.fill(white)

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_q:
                running = False


    keys=pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        ball.move("UP")

    if keys[pygame.K_DOWN]:
        ball.move("DOWN")

    if keys[pygame.K_RIGHT]:
        ball.move("RIGHT")

    if keys[pygame.K_LEFT]:
        ball.move("LEFT")

    ball.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()