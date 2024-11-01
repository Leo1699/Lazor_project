import re

def read_bff(filepath):
    grid = []
    blocks = {}
    lazors = []
    points = []

    with open(filepath, 'r') as file:
        lines = file.readlines()

        parsing_grid = False
        for line in lines:
            line = line.strip()
            if line.startswith('#') or line == '':
                continue

            if line == "GRID START":
                parsing_grid = True
                continue
            elif line == "GRID STOP":
                parsing_grid = False
                continue

            if parsing_grid:
                grid.append(line.split())
            elif line.startswith(("A", "B", "C")):
                block_type, count = line.split()
                blocks[block_type] = int(count)
            elif line.startswith("L"):
                _, x, y, vx, vy = line.split()
                lazors.append((int(x), int(y), int(vx), int(vy)))
            elif line.startswith("P"):
                _, x, y = line.split()
                points.append((int(x), int(y)))

    return grid, blocks, lazors, points

class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class ReflectBlock(Block):
    def interact(self, lazor):
        # Reflect the lazor based on its incoming direction
        lazor.vx, lazor.vy = -lazor.vx, -lazor.vy

class OpaqueBlock(Block):
    def interact(self, lazor):
        # Stop the lazor by setting its velocity to zero
        lazor.vx, lazor.vy = 0, 0

class RefractBlock(Block):
    def interact(self, lazor):
        # Allow lazor to pass through with a copy of the lazor being refracted
        new_lazor = Lazor(lazor.x, lazor.y, -lazor.vx, -lazor.vy)
        return new_lazor

class Lazor:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def move(self):
        # Move lazor to next position
        self.x += self.vx
        self.y += self.vy

class Board:
    def __init__(self, grid, blocks, lazors, points):
        self.grid = grid
        self.blocks = blocks  # Dictionary of block types and their counts
        self.lazors = [Lazor(*lazor) for lazor in lazors]
        self.points = set(points)
        self.hit_points = set()

    def place_block(self, block_type, x, y):
        # Place a block of given type on the board
        if block_type == 'A':
            self.grid[x][y] = ReflectBlock(x, y)
        elif block_type == 'B':
            self.grid[x][y] = OpaqueBlock(x, y)
        elif block_type == 'C':
            self.grid[x][y] = RefractBlock(x, y)

    def simulate_lazor(self):
        for lazor in self.lazors:
            while True:
                lazor.move()
                if (lazor.x, lazor.y) in self.points:
                    self.hit_points.add((lazor.x, lazor.y))
                # Get the current block at lazor's position
                current_block = self.grid[lazor.x][lazor.y]
                if isinstance(current_block, Block):
                    # Interact with block and determine new lazor position/direction
                    new_lazor = current_block.interact(lazor)
                    if new_lazor:
                        self.lazors.append(new_lazor)
                if lazor.vx == 0 and lazor.vy == 0:
                    break  # Lazor stopped by opaque block

    def is_solution(self):
        # Check if all points have been hit
        return self.points == self.hit_points

    def solve(self):
        # Try different block configurations here (use backtracking or other logic)
        pass

def output_solution(board):
    print("Solution Board:")
    for y in range(len(board.grid)):
        for x in range(len(board.grid[0])):
            if (x, y) in board.hit_points:
                print("P", end=" ")  # Mark points that have been hit
            else:
                print(board.grid[x][y] or ".", end=" ")  # "." for empty spaces
        print()


if __name__ == "__main__":
    filepath = 'dark_1.bff'
    grid, blocks, lazors, points = read_bff(filepath)
    board = Board(grid, blocks, lazors, points)

    # Solve the puzzle
    if board.solve():
        output_solution(board)
    else:
        print("No solution found.")
