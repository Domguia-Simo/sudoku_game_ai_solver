import pygame
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 540, 600
ROWS, COLS = 9, 9
CELL_SIZE = WIDTH // 9
FONT = pygame.font.SysFont("comicsans", 40)
DELAY = 50  # milliseconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (255, 0, 0)

# Sample puzzle (0 = empty)
board = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

# Create window
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Solver AI (Backtracking)")


# Drawing Functions
def draw_grid():
    for i in range(ROWS + 1):
        line_width = 4 if i % 3 == 0 else 1
        pygame.draw.line(win, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), line_width)
        pygame.draw.line(win, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, WIDTH), line_width)

def draw_numbers(board):
    for i in range(ROWS):
        for j in range(COLS):
            if board[i][j] != 0:
                text = FONT.render(str(board[i][j]), True, BLACK)
                win.blit(text, (j * CELL_SIZE + 20, i * CELL_SIZE + 10))

def draw_board(board):
    win.fill(WHITE)
    draw_grid()
    draw_numbers(board)
    pygame.display.update()


# Sudoku Logic Functions
def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    box_x, box_y = col // 3, row // 3
    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if board[i][j] == num:
                return False
    return True

def find_empty(board):
    for i in range(ROWS):
        for j in range(COLS):
            if board[i][j] == 0:
                return i, j
    return None

def visualize_solver(board):
    empty = find_empty(board)
    if not empty:
        return True

    row, col = empty
    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num

            # Visualization
            draw_board(board)
            pygame.draw.rect(win, GREEN, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
            pygame.display.update()
            pygame.time.delay(DELAY)

            if visualize_solver(board):
                return True

            # Backtrack
            board[row][col] = 0
            draw_board(board)
            pygame.draw.rect(win, RED, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
            pygame.display.update()
            pygame.time.delay(DELAY)

    return False


# Main Game Loop
def main():
    running = True
    solved = False

    while running:
        draw_board(board)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not solved:
                    visualize_solver(board)
                    solved = True

    pygame.quit()

main()
