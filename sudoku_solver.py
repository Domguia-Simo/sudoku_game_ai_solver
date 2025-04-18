import pygame 
import time 
import random 
import copy 
pygame.init() 
WIDTH, HEIGHT = 540, 600 
WIN = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption("Sudoku with AI Solver") 
FONT = pygame.font.SysFont("comicsans", 40) 
SMALL_FONT = pygame.font.SysFont("comicsans", 20) 
# -------------------- Board Generator -------------------- 
def generate_board(difficulty="medium"): 
    # Start with a full board using backtracking 
    board = [[0] * 9 for _ in range(9)] 
    fill_board(board) 
    # Remove elements based on difficulty 
    level = {"easy": 35, "medium": 45, "hard": 55} 
    remove = level.get(difficulty, 45) 
    while remove > 0: 
            row, col = random.randint(0, 8), random.randint(0, 8) 
            if board[row][col] != 0: 
                board[row][col] = 0 
                remove -= 1 
    return board 
 
def fill_board(board): 
    nums = list(range(1, 10)) 
    for i in range(9): 
        for j in range(9): 
            if board[i][j] == 0: 
                random.shuffle(nums) 
                for num in nums: 
                    if valid(board, num, (i, j)): 
                        board[i][j] = num 
                        if fill_board(board): 
                            return True 
                        board[i][j] = 0 
                return False 
    return True 
 
# -------------------- Backtracking Solver -------------------- 
def valid(board, num, pos): 
    row, col = pos 
    # Check row 
    if any(board[row][i] == num for i in range(9)): 
        return False 
    # Check column 
    if any(board[i][col] == num for i in range(9)): 
        return False 
    # Check box 
    box_x, box_y = col // 3, row // 3 
    for i in range(box_y*3, box_y*3 + 3): 
        for j in range(box_x*3, box_x*3 + 3): 
            if board[i][j] == num: 
                return False 
    return True 
 
def solve(board, visualizer=None): 
    for i in range(9): 
        for j in range(9): 
            if board[i][j] == 0: 
                for num in range(1, 10): 
                    if valid(board, num, (i, j)): 
                        board[i][j] = num 
                        if visualizer: 
                            visualizer.update(board, i, j, num, "Trying") 
                        if solve(board, visualizer): 
                            return True 
                        board[i][j] = 0 
                        if visualizer: 
                            visualizer.update(board, i, j, num, 
"Backtracking") 
                return False 
    return True 
 
# -------------------- Visualization -------------------- 
class Visualizer: 
    def __init__(self, board): 
        self.board = board 
        self.original = copy.deepcopy(board) 
 
    def draw(self): 
        WIN.fill((255, 255, 255)) 
        # Draw grid 
        for i in range(10): 
            thickness = 4 if i % 3 == 0 else 1 
            pygame.draw.line(WIN, (0, 0, 0), (0, i*60), (540, i*60), 
thickness) 
            pygame.draw.line(WIN, (0, 0, 0), (i*60, 0), (i*60, 540), 
thickness) 
 
        # Draw numbers 
        for i in range(9): 
            for j in range(9): 
                num = self.board[i][j] 
                if num != 0: 
                    color = (0, 0, 0) if self.original[i][j] != 0 else (0, 
0, 255) 
                    text = FONT.render(str(num), True, color) 
                    WIN.blit(text, (j*60 + 20, i*60 + 15)) 
 
    def update(self, board, row, col, num, action): 
        self.board = copy.deepcopy(board) 
        self.draw() 
        pygame.display.update() 
        print(f"{action} number {num} at ({row}, {col})") 
        time.sleep(0.05) 
 
# -------------------- Main Game Loop -------------------- 
def main(): 
    difficulty = "medium"  # Change to "easy", "hard" if needed 
    board = generate_board(difficulty) 
    visualizer = Visualizer(board) 
    running = True 
    solved = False 
 
    while running: 
        WIN.fill((255, 255, 255)) 
        visualizer.draw() 
        pygame.display.update() 
 
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                running = False 
 
        if not solved: 
            time.sleep(1) 
            print("Solving started...\n") 
            solve(board, visualizer) 
            print("\nSolved successfully!") 
            solved = True 
 
    pygame.quit() 
 
if __name__ == "__main__": 
    main()