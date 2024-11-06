# Lazor Project for EN.540.635

## This is LazorProject for Group QQalways_Win
The Lazor Project is a Python-based program that automatically solves the "Lazors" game. This project simulates the game's grid, tracks laser paths, and strategically places blocks to meet game objectives. The solution is generated through algorithmic computations and saved as a .bff file.

## Team Member:
Haoran Liu: hliu169@jh.edu  
Congqi Lin: clin145@jh.edu  

## How It Works

### Key Classes and Functions

- **A_Block, B_Block, C_Block**: Classes defining the interaction behavior of different types of blocks:
  - **A_Block**: Reflects the laser upon contact.
  - **B_Block**: Absorbs the laser, ending its path.
  - **C_Block**: Splits the laser into two separate paths.

- **read_bff**: Reads and parses the `.bff` file to obtain the initial game configuration, including:
  - Block counts (A, B, and C types)
  - Laser start positions and directions
  - Target points for lasers
  - Initial grid layout

- **Grid**: Manages the grid structure and allows for block placement. It handles:
  - Generating the grid with added blocks
  - Locating static blocks that should not be overwritten

- **Lazor**: Manages the lasers and their interactions with blocks in the grid, including:
  - Tracking the laser paths through the grid
  - Checking for boundaries and target holes
  - Updating laser directions based on block interactions

- **find_path**: Generates possible grid configurations with different block placements, then tests each configuration to find a solution that hits all target points.

- **save_solution_bff**: Saves the solution (final grid layout and laser paths) back into a `.bff` file.

- **solve_lazor_game**: The main function that combines all the steps, from reading the `.bff` file, finding the solution, to saving the solution.

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


The result will display like (showstopper_4_solved.bff)  
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

