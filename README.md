# Lazor Project for EN.540.635

## This is LazorProject for Group QQalways_Win
The Lazor Project is a Python-based program that automatically solves the "Lazors" game. This project simulates the game's grid, tracks laser paths, and strategically places blocks to meet game objectives. The solution is generated through algorithmic computations and saved as a .bff file.

## Team Member:
Haoran Liu: hliu169@jh.edu  
Congqi Lin: clin145@jh.edu  

## How It Works

### Key Classes

- **A_Block, B_Block, C_Block**: These classes define the interaction behavior for each block type:
  - **A_Block**: Reflects the laser upon contact, changing its direction.
  - **B_Block**: Absorbs the laser, ending its path at that block.
  - **C_Block**: Splits the laser into two separate paths, creating a fork in the path.

- **Grid**: Manages the grid structure and allows for block placement. The Grid class handles:
  - **locate_static_blocks**: Identifies fixed blocks on the board to prevent overwriting them during grid updates.
  - **gen_grid**: Places blocks on the grid based on specific configurations.

- **Lazor**: Manages laser movements and interactions with blocks on the grid, including:
  - **block**: Determines the block type at a position and updates the laser's path accordingly.
  - **meet_block**: Checks for block encounters and calculates the new laser direction.
  - **check**: Verifies if the laser path is still within grid boundaries.
  - **lazor_path**: Tracks each laser's path, ensuring that it reaches all target points.

### Key Functions

- **read_bff**: Reads and parses the `.bff` file to extract initial game configuration, such as block counts, laser positions, target points, and grid layout.

- **save_solution_bff**: Saves the solved grid layout, including laser paths, to a `.bff` file. This function generates the solution output format, including:
  - Final grid layout with placed blocks
  - Laser start points
  - Target points
  - Laser path steps

- **find_path**: Generates potential block configurations and tests each to find a solution that meets the target requirements. It returns the solution if one is found.

- **solve_lazor_game**: The main function that orchestrates the entire process, combining the above classes and functions to read input, compute solutions, and save the output.

### Workflow

1. **Parse Input**: The `.bff` file is read to obtain game configuration details.
2. **Generate Grid**: A grid is generated with the available blocks placed in specified positions.
3. **Simulate Laser Paths**: The laser paths are calculated based on the blocks' interactions.
4. **Find Solution**: Multiple grid configurations are tested to find one where all target points are hit by the lasers.
5. **Save Solution**: The solved grid layout and laser paths are saved to a `.bff` file.

## Example Usage:  
The Input .bff docs like (showstopper_4.bff)  
```plaintext

GRID START
B o o
o o o
o o o
GRID STOP

A 3
B 3

L 3 6 -1 -1

P 2 3
```

The result will display like (showstopper_4_solved.bff)
```plaintext 
GRID START
B A B
B o A
A o B
GRID STOP

L LASER_START
L 3 6 -1 -1
L LASER_END

P HOLES_START
P 2 3
P HOLES_END

LASER PATH
Path:
  (3, 6) -> (2, 5) -> (3, 4) -> (4, 3) -> (3, 2) -> (2, 3) -> END

LASER PATH END
```
