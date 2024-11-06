from sympy.utilities.iterables import multiset_permutations
import copy
import time

class A_Block:
    '''
    A-type block that reflects the laser upon interaction.

    **Methods**

        interact(direction, point):
            Reflects the laser based on position and direction.

    **Parameters**

        direction: *list*
            The laser's current direction as [dx, dy].
        point: *list*
            Current position of the laser as [x, y].

    **Returns**

        list:
            Reflected laser direction as [dx, dy].
    '''
    @staticmethod
    def interact(direction, point):
        # Reflects based on position: horizontal or vertical flip
        return [-direction[0], direction[1]] if point[0] % 2 == 0 else [direction[0], -direction[1]]


class B_Block:
    '''
    B-type block that absorbs the laser, ending its path.

    **Methods**

        interact(direction, point):
            Absorbs the laser.

    **Parameters**

        direction: *list*
            The laser's current direction as [dx, dy].
        point: *list*
            Current position of the laser as [x, y].

    **Returns**

        list:
            Empty list indicating the laser is absorbed.
    '''
    @staticmethod
    def interact(direction, point):
        # Laser absorbed, no further direction
        return []


class C_Block:
    '''
    C-type block that splits the laser into two paths.

    **Methods**

        interact(direction, point):
            Splits the laser based on position and direction.

    **Parameters**

        direction: *list*
            Laser's current direction as [dx, dy].
        point: *list*
            Current position of the laser as [x, y].

    **Returns**

        list:
            Two new directions after splitting, as [dx1, dy1, dx2, dy2].
    '''
    @staticmethod
    def interact(direction, point):
        # Split laser: generates two paths based on position
        if point[0] % 2 == 0:
            return [direction[0], direction[1], -direction[0], direction[1]]
        else:
            return [direction[0], direction[1], direction[0], -direction[1]]


def read_bff(file_name):
    '''
    Reads a .bff file and parses block counts, laser setup, target points, and grid layout.

    **Parameters**

        file_name: *str*
            Filename of the .bff file.

    **Returns**

        tuple:
            Parsed data including grid layout, block counts, laser info, targets, and original grid.
    '''
    # Initialize counts and lists for blocks, lasers, targets, and grid structure
    A_num = B_num = C_num = 0
    L_list = []
    P_list = []
    grid_temp = []
    reading_grid = False

    # Open and process each line in the file
    with open(file_name, 'r') as f:
        for line in f:
            line = line.strip()

            # Ignore comments and blank lines
            if line.startswith('#') or not line:
                continue

            # Count blocks A, B, C based on file format
            if line.startswith('A ') and line[2:].isdigit():
                A_num = int(line.split()[1])
            elif line.startswith('B ') and line[2:].isdigit():
                B_num = int(line.split()[1])
            elif line.startswith('C ') and line[2:].isdigit():
                C_num = int(line.split()[1])

            # Collect laser start points and directions
            elif line.startswith('L '):
                parts = line.split()
                L_list.append([int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])])

            # Collect target points for lasers
            elif line.startswith('P '):
                parts = line.split()
                P_list.append([int(parts[1]), int(parts[2])])

            # Identify grid content between 'GRID START' and 'GRID STOP'
            elif line == 'GRID START':
                reading_grid = True
            elif line == 'GRID STOP':
                reading_grid = False
            elif reading_grid:
                grid_temp.append(line.split())

    # Expand grid layout for border calculations
    grid_full = [[x for x in row] for row in grid_temp]
    grid_origin = [row.copy() for row in grid_full]
    row = len(grid_full)
    column = len(grid_full[0])
    insert = ['x'] * (2 * column + 1)

    # Insert 'x' borders to create a complete grid structure with boundary
    for i in range(row):
        for j in range(column + 1):
            grid_full[i].insert(2 * j, 'x')
    for i in range(row + 1):
        grid_full.insert(2 * i, insert)

    return grid_full, A_num, B_num, C_num, L_list, P_list, grid_origin


def save_solution_bff(solved_board, answer_lazor, lazors_info, holes, filename):
    '''
    Saves the solution to a .bff file with all laser paths.

    **Parameters**

        solved_board: *list*
            Solved grid layout with block placements.
        answer_lazor: *list*
            Paths of the lasers as lists of coordinates.
        lazors_info: *list*
            Original positions and directions of lasers as [x, y, dx, dy].
        holes: *list*
            Target points for the lasers as lists of [x, y].
        filename: *str*
            Original .bff file name.
    '''
    # Define solution file name based on original
    solution_filename = f"{filename.split('.')[0]}_solved.bff"

    # Open the new file to write the solution details
    with open(solution_filename, 'w') as f:
        # Write grid configuration
        f.write("GRID START\n")
        for row in solved_board:
            line = ' '.join(row)
            f.write(line + '\n')
        f.write("GRID STOP\n\n")

        # Write laser setup details
        f.write("L LASER_START\n")
        for lazor in lazors_info:
            f.write(f"L {lazor[0]} {lazor[1]} {lazor[2]} {lazor[3]}\n")
        f.write("L LASER_END\n\n")

        # Write hole (target) locations
        f.write("P HOLES_START\n")
        for hole in holes:
            f.write(f"P {hole[0]} {hole[1]}\n")
        f.write("P HOLES_END\n\n")

        # Write unique laser paths
        f.write("LASER PATH\n")
        for path in answer_lazor:
            unique_path = []
            for point in path:
                if not unique_path or unique_path[-1] != point[:2]:
                    unique_path.append(point[:2])

            # Write the path in specified format
            f.write("Path:\n  ")
            for i, point in enumerate(unique_path):
                if i < len(unique_path) - 1:
                    f.write(f"({point[0]}, {point[1]}) -> ")
                else:
                    f.write(f"({point[0]}, {point[1]}) -> END\n")
            f.write("\n")
        f.write("LASER PATH END\n")

    print(f'Solution successfully saved in {solution_filename}')


class Grid:
    '''
    Class to generate and manage grid configurations.

    **Parameters**

        origrid: *list*
            The original grid layout without added blocks.
    '''

    def __init__(self, origrid):
        # Initialize grid and dimensions
        self.origrid = origrid
        self.length = len(origrid)
        self.width = len(origrid[0])

    def gen_grid(self, listgrid, position):
        '''
        Inserts blocks into the grid according to the specified positions.

        **Parameters**

            listgrid: *list*
                List of block types to insert (e.g., 'A', 'B', 'C').
            position: *list*
                Coordinates of empty cells where blocks can be placed.

        **Returns**

            list:
                Updated grid with blocks inserted.
        '''
        self.listgrid = listgrid
        for row in range(len(self.origrid)):
            for column in range(len(self.origrid[0])):
                # Place blocks in empty spots except for fixed/static positions
                if [row, column] not in position:
                    if self.origrid[row][column] != 'x':
                        self.origrid[row][column] = listgrid.pop(0)
        return self.origrid


class Lazor:
    '''
    Class for managing laser paths through the grid and tracking laser interactions.

    **Parameters**

        grid: *list*
            Grid layout containing block placements.
        lazorlist: *list*
            Laser start points and directions as lists of [x, y, dx, dy].
        holelist: *list*
            Target hole positions as lists of [x, y].
    '''

    def __init__(self, grid, lazorlist, holelist):
        # Initialize the grid, lasers, and targets
        self.grid = grid
        self.lazorlist = lazorlist
        self.holelist = holelist

    def block(self, block_type, direction, point):
        '''
        Determines the block type and handles laser interaction.

        **Parameters**

            block_type: *str*
                Type of block ('A', 'B', or 'C').
            direction: *list*
                Current laser direction as [dx, dy].
            point: *list*
                Current laser position as [x, y].

        **Returns**

            list:
                Updated direction(s) after interaction.
        '''
        block_classes = {
            'A': A_Block,
            'B': B_Block,
            'C': C_Block
        }
        block_class = block_classes.get(block_type)
        if block_class:
            return block_class.interact(direction, point)
        return direction

    def meet_block(self, point, direction):
        '''
        Checks for a block encounter and updates laser direction accordingly.

        **Parameters**

            point: *list*
                Current laser position [x, y].
            direction: *list*
                Current direction of laser [dx, dy].

        **Returns**

            list:
                New direction of the laser after encountering a block.
        '''
        # Calculate possible next positions
        x1, y1 = point[0], point[1] + direction[1]
        x2, y2 = point[0] + direction[0], point[1]

        # Determine block type based on laser position
        block_type = self.grid[y1][x1] if point[0] & 1 == 1 else self.grid[y2][x2]
        return self.block(block_type, direction, point)

    def check(self, laz_co, direction):
        '''
        Verifies if the laser is still within grid boundaries.

        **Parameters**

            laz_co: *list*
                Current laser coordinates as [x, y].
            direction: *list*
                Current laser direction as [dx, dy].

        **Returns**

            bool:
                True if within bounds, False if out of bounds.
        '''
        width = len(self.grid[0])
        length = len(self.grid)
        x, y = laz_co[0], laz_co[1]

        # Check if next position is within the grid
        return x < 0 or x >= width or y < 0 or y >= length or \
            x + direction[0] < 0 or x + direction[0] >= width or \
            y + direction[1] < 0 or y + direction[1] >= length

    def lazor_path(self):
        '''
        Calculates and tracks paths for all lasers in the grid.

        **Returns**

            list:
                Laser paths with coordinates for each step, or 0 if targets are missed.
        '''
        # Initialize laser paths and completed targets
        laser_paths = []
        completed_paths = []

        for laser in self.lazorlist:
            laser_paths.append([laser])

        for step in range(30):
            for i in range(len(laser_paths)):
                x, y, dx, dy = laser_paths[i][-1]
                current_pos = [x, y]
                direction = [dx, dy]

                # Skip if laser moves out of bounds
                if self.check(current_pos, direction):
                    continue

                # Calculate next step and interactions with blocks
                next_step = self.meet_block(current_pos, direction)

                # If block is of type B, laser stops here
                if len(next_step) == 0:
                    laser_paths[i].append([x, y, 0, 0])
                    if current_pos in self.holelist and current_pos not in completed_paths:
                        completed_paths.append(current_pos)

                # For type A blocks or empty cells, update direction
                elif len(next_step) == 2:
                    direction = next_step
                    x += direction[0]
                    y += direction[1]
                    laser_paths[i].append([x, y, direction[0], direction[1]])
                    if [x, y] in self.holelist and [x, y] not in completed_paths:
                        completed_paths.append([x, y])

                # For type C, laser may split into two paths
                elif len(next_step) == 4:
                    x1, y1 = x + next_step[0], y + next_step[1]
                    x2, y2 = x, y
                    laser_paths.append([[x1, y1, next_step[0], next_step[1]]])
                    laser_paths[i].append([x2, y2, next_step[2], next_step[3]])
                    if [x2, y2] in self.holelist and [x2, y2] not in completed_paths:
                        completed_paths.append([x2, y2])
                else:
                    print('Unexpected block type encountered')

        # Return paths if all target holes are reached
        return laser_paths if len(completed_paths) == len(self.holelist) else 0


def find_path(grid, A_num, B_num, C_num, lazorlist, holelist, position):
    '''
    Generates possible grids with block placements and finds the solution.

    **Parameters**

        grid: *list*
            Initial grid layout with empty cells marked.
        A_num: *int*
            Number of A blocks available.
        B_num: *int*
            Number of B blocks available.
        C_num: *int*
            Number of C blocks available.
        lazorlist: *list*
            Laser start positions and directions.
        holelist: *list*
            Target hole positions.
        position: *list*
            Positions of static blocks.

    **Returns**

        tuple:
            Solution with laser paths, block arrangement, and updated grid.
    '''
    # Collect all possible block configurations
    Blocks = []
    for a in grid:
        for b in a:
            if b == 'o':
                Blocks.append(b)
    for i in range(A_num):
        Blocks[i] = 'A'
    for i in range(A_num, A_num + B_num):
        Blocks[i] = 'B'
    for i in range(A_num + B_num, A_num + B_num + C_num):
        Blocks[i] = 'C'

    # Generate block placements and test configurations
    list_Blocks = list(multiset_permutations(Blocks))

    while list_Blocks:
        list_temp = list_Blocks.pop()
        list_temp_save = copy.deepcopy(list_temp)

        ori_grid = Grid(grid)
        test_board = ori_grid.gen_grid(list_temp, position)

        lazor = Lazor(test_board, lazorlist, holelist)
        solution = lazor.lazor_path()

        if solution != 0:
            return solution, list_temp_save, test_board


def locate_static_blocks(grid):
    '''
    Identifies fixed (static) blocks in the grid.

    **Parameters**

        grid: *list*
            Original grid layout from the .bff file.

    **Returns**

        list:
            Coordinates of fixed blocks as lists of [x, y].
    '''
    static_positions = []
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            cell = grid[i][j]
            if cell in ('A', 'B', 'C'):
                static_positions.append([i * 2 + 1, j * 2 + 1])
    return static_positions


def solve_lazor_game(file_path):
    '''
    Extracts data from a .bff file, computes solution, and saves result.

    **Parameters**

        file_path: *str*
            Name of the .bff file.

    **Returns**

        tuple:
            Solved grid layout, paths of all lasers, and final grid layout.
    '''
    # Parse grid and laser setup
    parsed_data = read_bff(file_path)
    main_grid, num_a, num_b, num_c, lasers, targets, base_grid = parsed_data

    # Identify static block positions
    fixed_positions = locate_static_blocks(base_grid)

    # Find paths, grid layout, and laser configurations
    laser_paths, flattened_grid = find_path(
        main_grid, num_a, num_b, num_c, lasers, targets, fixed_positions
    )[:2]

    # Apply correct block placements to the grid
    temp_grid_list = copy.deepcopy(flattened_grid)
    solution_grid = copy.deepcopy(base_grid)
    for i in range(len(solution_grid)):
        for j in range(len(solution_grid[0])):
            if solution_grid[i][j] == 'o':
                solution_grid[i][j] = temp_grid_list.pop(0)

    # Save solution back to a .bff file
    save_solution_bff(solved_board=solution_grid, answer_lazor=laser_paths,
                      lazors_info=lasers, holes=targets, filename=file_path)

    return solution_grid, laser_paths, flattened_grid


if __name__ == "__main__":
    t0 = time.time()
    solve_lazor_game('dark_1.bff')
    solve_lazor_game('mad_1.bff')
    solve_lazor_game('mad_4.bff')
    solve_lazor_game('mad_7.bff')
    solve_lazor_game('numbered_6.bff')
    solve_lazor_game('showstopper_4.bff')
    solve_lazor_game('tiny_5.bff')
    solve_lazor_game('yarn_5.bff')
    t1 = time.time()
    print(t1 - t0)
