import pygame, sys
from checker import *

# Initialize
pygame.init()

screen = pygame.display.set_mode((640,640))
pygame.display.set_caption("Checkers")
clock = pygame.time.Clock()
running = True

# Draw Checkerboard, H and W of each square is 80
def drawBoard():
    for x in range(8):
        for y in range(8):
            rect = [x*80, y*80, 80, 80]
            pygame.draw.rect(screen, "red" if (x + y) % 2 == 0 else "black", rect)

# Draw the given graph for either color
def drawGraph(graph:dict, positions:dict):
    for vert, edge in graph.items():
        pygame.draw.circle(screen, "green", positions[vert], 5)
        for e in edge:
            pygame.draw.line(screen, "blue", positions[vert], positions[e])

game = Game(sys.argv[0].strip("/main.py"))

while running:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            game.clicked(event.pos)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                game = Game(sys.argv[0].strip("/main.py"))
    
    drawBoard()
    game.draw(screen)
    game.checkWinner(screen)
    pygame.display.flip()