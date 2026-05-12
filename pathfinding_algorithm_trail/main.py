import pygame
import csv
import heapq

WIDTH, HEIGHT = 600, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)
GRAY = (200, 200, 200)

class Node:
    def __init__(self, x, y, type):
        self.x, self.y = x, y
        self.type = type
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f

def load_map(filename):
    grid = []
    start = None
    end = None
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for y, row in enumerate(reader):
            grid_row = []
            for x, val in enumerate(row):
                node = Node(x, y, val)
                grid_row.append(node)
                if val == '2':
                    start = node
                elif val == '3':
                    end = node
            grid.append(grid_row)
    return grid, start, end

def heuristic(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    grid, start_node, end_node = load_map('map.csv')
    rows, cols = len(grid), len(grid[0])
    cell_w, cell_h = WIDTH // cols, HEIGHT // rows

    if start_node:
        start_node.g = 0
        start_node.f = heuristic(start_node, end_node)
    
    open_set = []
    if start_node:
        heapq.heappush(open_set, (start_node.f, start_node))
    
    closed_set = set()
    path = []
    found = False
    searching = True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if searching and open_set:
            current = heapq.heappop(open_set)[1]

            if current == end_node:
                searching = False
                found = True
                temp = current
                while temp:
                    path.append(temp)
                    temp = temp.parent
            
            closed_set.add(current)

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = current.x + dx, current.y + dy
                if 0 <= ny < rows and 0 <= nx < cols:
                    neighbor = grid[ny][nx]
                    if neighbor.type == '1' or neighbor in closed_set:
                        continue

                    temp_g = current.g + 1
                    if temp_g < neighbor.g:
                        neighbor.parent = current
                        neighbor.g = temp_g
                        neighbor.h = heuristic(neighbor, end_node)
                        neighbor.f = neighbor.g + neighbor.h
                        if neighbor not in [n[1] for n in open_set]:
                            heapq.heappush(open_set, (neighbor.f, neighbor))
        elif not open_set:
            searching = False

        screen.fill(WHITE)
        for row in grid:
            for node in row:
                rect = (node.x * cell_w, node.y * cell_h, cell_w, cell_h)
                if node.type == '1':
                    pygame.draw.rect(screen, BLACK, rect)
                elif node == start_node:
                    pygame.draw.rect(screen, GREEN, rect)
                elif node == end_node:
                    pygame.draw.rect(screen, RED, rect)
                elif node in path:
                    pygame.draw.rect(screen, BLUE, rect)
                elif node in closed_set:
                    pygame.draw.rect(screen, PURPLE, rect)
                elif node in [n[1] for n in open_set]:
                    pygame.draw.rect(screen, CYAN, rect)
                
                pygame.draw.rect(screen, GRAY, rect, 1)

        pygame.display.flip()
        pygame.time.delay(30)

    pygame.quit()

if __name__ == "__main__":
    main()