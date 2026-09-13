import matplotlib.pyplot as plt
import pygame, sys, math

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Direction Finder")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((255, 255, 255))

    pygame.display.flip()