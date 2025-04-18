
import pygame
import time
import random
import copy
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Initialize Pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 540, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku with AI Solver")
FONT = pygame.font.SysFont("comicsans", 40)
SMALL_FONT = pygame.font.SysFont("comicsans", 20)

# Database setup using SQLAlchemy
Base = declarative_base()

class SudokuPuzzle(Base):
    __tablename__ = 'sudoku_puzzles'

    id = Column(Integer, primary_key=True)
    difficulty = Column(String)
    puzzle_data = Column(String)
    solution_data = Column(String)

engine = create_engine('sqlite:///sudoku_games.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

class BoardGenerator:
    def __init__(self):
        pass

    def generate_board(self, difficulty="medium"):
        """Generates a Sudoku board of a given difficulty."""
        board = [[0] * 9 for _ in range(9)]
        self._fill_board(board)
        level = {"easy": 35, "medium": 45, "hard": 55}
        remove_count = level.get(difficulty, 45)
        solution = [row[:] for row in board] # Store the solution before making it a puzzle
        self._make_puzzle(board, remove_count)
        return board, solution

    def _make_puzzle(self, board, remove_count):
        """Removes elements from a solved board to create a puzzle."""
        cells = list((i, j) for i in range(9) for j in range(9))
        random.shuffle(cells)
        removed = 0
        while removed < remove_count:
            row, col = cells.pop()
            if board[row][col] != 0:
                board[row][col] = 0
                removed += 1

    def _fill_board(self, board):
        """Fills the board using backtracking to create a solved Sudoku."""
        nums = list(range(1, 10))
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    random.shuffle(nums)
                    for num in nums:
                        if self._valid(board, num, (i, j)):
                            board[i][j] = num
                            if self._fill_board(board):
                                return True
                            board[i][j] = 0
                    return False
        return True

    def _valid(self, board, num, pos):
        """Checks if a number is valid at a given position."""
        row, col = pos
        # Check row
        if any(board[row][i] == num for i in range(9)):
            return False
        # Check column
        if any(board[i][col] == num for i in range(9)):
            return False
        # Check box
        box_x, box_y = col // 3, row // 3
        for i in range(box_y * 3, box_y * 3 + 3):
            for j in range(box_x * 3, box_x * 3 + 3):
                if board[i][j] == num:
                    return False
        return True

class Solver:
    def solve(self, board, visualizer=None):
        """Solves the Sudoku board using backtracking."""
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    for num in range(1, 10):
                        if self._valid(board, num, (i, j)):
                            board[i][j] = num
                            if visualizer:
                                visualizer.update(board, i, j, num, "Trying")
                            if self.solve(board, visualizer):
                                return True
                            board[i][j] = 0
                            if visualizer:
                                visualizer.update(board, i, j, num, "Backtracking")
                    return False
        return True

    def _valid(self, board, num, pos):
        """Checks if a number is valid at a given position."""
        row, col = pos
        # Check row
        if any(board[row][i] == num for i in range(9)):
            return False
        # Check column
        if any(board[i][col] == num for i in range(9)):
            return False
        # Check box
        box_x, box_y = col // 3, row // 3
        for i in range(box_y * 3, box_y * 3 + 3):
            for j in range(box_x * 3, box_x * 3 + 3):
                if board[i][j] == num:
                    return False
        return True

class Visualizer:
    def __init__(self, board):
        self.board = board
        self.original = copy.deepcopy(board)

    def draw(self):
        """Draws the Sudoku board on the Pygame window."""
        WIN.fill((255, 255, 255))
        # Draw grid
        for i in range(10):
            thickness = 4 if i % 3 == 0 else 1
            pygame.draw.line(WIN, (0, 0, 0), (0, i * 60), (540, i * 60), thickness)
            pygame.draw.line(WIN, (0, 0, 0), (i * 60, 0), (i * 60, 540), thickness)

        # Draw numbers
        for i in range(9):
            for j in range(9):
                num = self.board[i][j]
                if num != 0:
                    color = (0, 0, 0) if self.original[i][j] != 0 else (0, 0, 255)
                    text = FONT.render(str(num), True, color)
                    WIN.blit(text, (j * 60 + 20, i * 60 + 15))

    def update(self, board, row, col, num, action):
        """Updates the visualizer with the current board state."""
        self.board = copy.deepcopy(board)
        self.draw()
        pygame.display.update()
        print(f"{action} number {num} at ({row}, {col})")
        time.sleep(0.05)

class Game:
    def __init__(self, difficulty="medium"):
        self.generator = BoardGenerator()
        self.solver = Solver()
        self.difficulty = difficulty
        self.puzzle, self.solution = self.generator.generate_board(self.difficulty)
        self.visualizer = Visualizer(self.puzzle)
        self.running = True
        self.solved = False
        self.db_session = session

    def store_game(self):
        """Stores the current game (puzzle and solution) in the database."""
        puzzle_str = ','.join(str(num) for row in self.puzzle for num in row)
        solution_str = ','.join(str(num) for row in self.solution for num in row)
        new_game = SudokuPuzzle(difficulty=self.difficulty, puzzle_data=puzzle_str, solution_data=solution_str)
        self.db_session.add(new_game)
        self.db_session.commit()
        print("Game stored in the database.")

    def load_game(self, game_id):
        """Loads a game from the database based on its ID."""
        stored_game = self.db_session.query(SudokuPuzzle).filter_by(id=game_id).first()
        if stored_game:
            puzzle_data = list(map(int, stored_game.puzzle_data.split(',')))
            solution_data = list(map(int, stored_game.solution_data.split(',')))
            self.puzzle = [puzzle_data[i*9:(i+1)*9] for i in range(9)]
            self.solution = [solution_data[i*9:(i+1)*9] for i in range(9)]
            self.visualizer = Visualizer(self.puzzle)
            self.solved = False
            print(f"Game ID {game_id} loaded.")
            return True
        else:
            print(f"Game ID {game_id} not found.")
            return False

    def run(self):
        """Main game loop."""
        print("Initial puzzle:")
        for row in self.puzzle:
            print(row)
        print("Initial solution:")
        for row in self.solution:
            print(row)
        print("Visualizer board (initial):")
        for row in self.visualizer.board:
            print(row)

        self.visualizer.draw()
        pygame.display.update()

        while self.running:
            WIN.fill((255, 255, 255))
            self.visualizer.draw()
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s and not self.solved:
                        self.store_game()
                    elif event.key == pygame.K_l:
                        game_id_to_load = int(input("Enter Game ID to load: "))
                        self.load_game(game_id_to_load)
                    elif event.key == pygame.K_SPACE and not self.solved:
                        time.sleep(1)
                        print("Solving started...\n")
                        if self.solver.solve(self.puzzle, self.visualizer):
                            print("\nSolved successfully!")
                        else:
                            print("\nNo solution found!")
                        self.solved = True
                        self.visualizer.board = self.puzzle # Update visualizer to show solved board

        pygame.quit()
        self.db_session.close()

if __name__ == "__main__":
    game = Game("medium")
    game.run()