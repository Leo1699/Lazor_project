from sympy.utilities.iterables import multiset_permutations
import copy
import time

class A_Block:
    '''
    This class defines the behavior of an A-type block,
    which reflects the laser in a new direction upon interaction.

    **Methods**

        interact(direction, point):
            Returns the reflected direction of the laser based on the
            position of the block and the incoming laser direction.

    **Parameters**

        direction: *list*
            A list representing the laser's current direction.
        point: *list*
            The current position of the laser.

    **Returns**

        list:
            A new direction after reflection based on the block's position.
    '''
    @staticmethod
    def interact(direction, point):
        # Reflect based on direction and position
        return [-direction[0], direction[1]] if point[0] % 2 == 0 else [direction[0], -direction[1]]


class B_Block:
    '''
    This class defines the behavior of a B-type block,
    which absorbs the laser, effectively ending its path.

    **Methods**

        interact(direction, point):
            Returns an empty list to indicate the laser is absorbed.

    **Parameters**

        direction: *list*
            A list representing the laser's current direction.
        point: *list*
            The current position of the laser.

    **Returns**

        list:
            An empty list to indicate the laser is absorbed.
    '''
    @staticmethod
    def interact(direction, point):
        # Absorb the laser
        return []


class C_Block:
    '''
    This class defines the behavior of a C-type block,
    which splits the laser into two paths upon interaction.

    **Methods**

        interact(direction, point):
            Returns two new directions for the laser, effectively
            splitting it based on the block's position and incoming direction.

    **Parameters**

        direction: *list*
            A list representing the laser's current direction.
        point: *list*
            The current position of the laser.

    **Returns**

        list:
            A list containing two sets of directions, representing
            the split paths of the laser.
    '''
    @staticmethod
    def interact(direction, point):
        # Split the laser into two directions
        if point[0] % 2 == 0:
            return [direction[0], direction[1], -direction[0], direction[1]]
        else:
            return [direction[0], direction[1], direction[0], -direction[1]]



def read_bff(file_name):
    '''
    Extract imformation from '.bff' file

    **Parameters**

        file_name: *str*
            The full name of the file which has information to be extracted

    **Return**

        tuple: *list, int, int, int, list, list，list*
            Elements in the tuple are as follow:
                grid_full: *list*
                    The full grid in the form of a coordinate system
                A_num: *int*
                    The number of A-block available
                B_num: *int*
                    The number of B-block available
                C_num: *int*
                    The number of C-block available
                L_list: *list*
                    The first two elements is the positon of the start point of the
                    lazor, the last two elements are the direction of the lazor
                P_list: *list*
                    The positions of the end points
                grid_origin: *list*
                    The grid directly obtained from the '.bff' file
    '''
    # Initialize the parameters
    content = []  # Store the content
    grid = []
    grid_origin = []
    grid_temp = []
    A_num = 0  # Initialize A, B, C, L, P
    B_num = 0
    C_num = 0
    L_list = []
    P_list = []
    # Open and read the file
    with open(file_name, 'r') as f:
        # Get all the lines in the file
        lines = list(f)
        for i in range(len(lines)):
            lines[i] = lines[i].strip()
            content.append(list(lines[i]))
    # Extract useful information
    for i in range(len(content)):
        for j in range(len(content[i])):
            # Set up some temporary lists
            A_temp = []
            B_temp = []
            C_temp = []
            # L_temp = []
            # P_temp = []
            # Get the number of available A-block
            if content[i][j] == 'A' and (str.isalpha(content[i][j + 1]) is False):
                for k in range(len(content[i])):
                    if str.isdigit(content[i][k]):
                        A_temp.append(content[i][k])
                        A_num = int(''.join(A_temp))
            # Get the number of available B-block
            if content[i][j] == 'B' and (str.isalpha(content[i][j + 1]) is False):
                for k in range(len(content[i])):
                    if str.isdigit(content[i][k]):
                        B_temp.append(content[i][k])
                        B_num = int(''.join(B_temp))
            # Get the number of available C-block
            if content[i][j] == 'C' and (str.isalpha(content[i][j + 1]) is False):
                for k in range(len(content[i])):
                    if str.isdigit(content[i][k]):
                        C_temp.append(content[i][k])
                        C_num = int(''.join(C_temp))
            # Get the positions of the start point and direction of lasors
            if content[i][j] == 'L' and (str.isalpha(content[i][j + 1]) is False):
                L_temp = lines[i].strip().split(' ')
                L_temp.remove('L')
                L_list.append([int(L_temp[0]), int(L_temp[1]),
                               int(L_temp[2]), int(L_temp[3])])
            # Get the positions of the end points
            if content[i][j] == 'P' and (str.isalpha(content[i][j - 1]) is False):
                P_temp = lines[i].strip().split(' ')
                P_temp.remove('P')
                P_list.append([int(P_temp[0]), int(P_temp[1])])

        # Get the raw grid from the file
        if lines[i] == 'GRID START':
            grid_start = i + 1
            while lines[grid_start] != 'GRID STOP':
                grid_temp.append(content[grid_start])
                grid_start += 1

    # Remove the spaces of the raw grid
    for i in range(len(grid_temp)):
        gridline = [x for x in grid_temp[i] if x != ' ']
        grid.append(gridline)
    # Get the original grid which will be used to draw a picture
    for i in range(len(grid_temp)):
        gridline = [x for x in grid_temp[i] if x != ' ']
        grid_origin.append(gridline)
    # Fulfill the grid with 'x' to get the full grid
    gridfull = grid.copy()
    row = len(gridfull)
    column = len(gridfull[0])
    insert = ['x'] * (2 * column + 1)
    for i in range(0, row):
        for j in range(0, column + 1):
            gridfull[i].insert(2 * j, 'x')
    for i in range(0, row + 1):
        gridfull.insert(2 * i, insert)


    return gridfull, A_num, B_num, C_num, L_list, P_list, grid_origin


def save_solution_bff(solved_board, answer_lazor, lazors_info, holes, filename):
    '''
    This function saves the solution as a .bff file with all paths output correctly.

    **Parameters**

        solved_board: *list*
            The solved grid with the block placements

        answer_lazor: *list*
            The paths that lasers passed

        lazors_info: *list*
            The original positions and directions of the lasers

        holes: *list*
            The positions of the hole points

        filename: *str*
            The name of the original .bff file

    **Return**

        None
    '''
    solution_filename = f"{filename.split('.')[0]}_solved.bff"

    with open(solution_filename, 'w') as f:
        # Write grid solution
        f.write("GRID START\n")
        for row in solved_board:
            line = ' '.join(row)  # Convert list to a string with space-separated values
            f.write(line + '\n')
        f.write("GRID STOP\n\n")

        # Write laser information
        f.write("L LASER_START\n")
        for lazor in lazors_info:
            f.write(f"L {lazor[0]} {lazor[1]} {lazor[2]} {lazor[3]}\n")
        f.write("L LASER_END\n\n")

        # Write hole information
        f.write("P HOLES_START\n")
        for hole in holes:
            f.write(f"P {hole[0]} {hole[1]}\n")
        f.write("P HOLES_END\n\n")

        # Write each laser path
        f.write("LASER PATH\n")
        for path in answer_lazor:
            # Avoid writing paths with repeated coordinates
            unique_path = []
            for point in path:
                if not unique_path or unique_path[-1] != point[:2]:
                    unique_path.append(point[:2])

            # Format the path output as requested
            f.write("Path:\n  ")
            for i, point in enumerate(unique_path):
                if i < len(unique_path) - 1:
                    f.write(f"({point[0]}, {point[1]}) -> ")
                else:
                    f.write(f"({point[0]}, {point[1]}) -> END\n")
            f.write("\n")
        f.write("LASER PATH END\n")

    print(f'Solution successfully saved in {solution_filename}')



class Grid(object):
    '''
    This Function class is a wrapper for generating various grids

    **Parameters**

        grid : *list*
            A list of list stand for a possible grid of the solution
    '''

    def __init__(self, origrid):
        self.origrid = origrid
        self.length = len(origrid)
        self.width = len(origrid[0])

    def gen_grid(self, listgrid, position):
        '''
        This function aim to put 'A', 'B' or 'C' block into the grid

        **Parameters**

            listgrid: *list*
                The grid that have the same length and width with the original grid
            position: *list*
                One possible arrangement for putting the blocks

        **Return**

            self.origrid: *list*
                The grid with blocks filled in
        '''
        self.listgrid = listgrid
        for row in range(len(self.origrid)):
            for column in range(len(self.origrid[0])):
                if [row, column] not in position:
                    if self.origrid[row][column] != 'x':
                        self.origrid[row][column] = listgrid.pop(0)
        return self.origrid


class Lazor(object):
    '''
    This Function class is a wrapper for identifying right grid and return a laser path

    **Parameters**

        grid : *list*
            A list of list stand for a possible grid of the solution
        lazorlist : *list*
            A list of list stand for start point and direction of laser
        holelist : *list*
            A list of list stand for the position of the end point or the hole
    '''

    def __init__(self, grid, lazorlist, holelist):
        self.grid = grid
        self.lazorlist = lazorlist
        self.holelist = holelist

    def block(self, block_type, direction, point):
        '''
        This function identifies the function of different blocks
        and interacts with the laser based on block type.
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
        This function checks whether the laser encounters a functional block
        and returns the new direction of the laser.

        **Parameters**

            point: *list*
                The current laser position
            direction: *list*
                The current direction of laser

        **Return**

            new_direction: *list*
                A list that includes new directions of laser after meeting functional block
        '''
        # Calculate the next position of the laser
        x1, y1 = point[0], point[1] + direction[1]
        x2, y2 = point[0] + direction[0], point[1]

        # Obtain the block type the laser touches
        if point[0] & 1 == 1:
            block_type = self.grid[y1][x1]
        else:
            block_type = self.grid[y2][x2]

        # Call the block method to handle interaction with the block
        return self.block(block_type, direction, point)



    def check(self, laz_co, direction):
        '''
        This function is used to check if the laser and its next step
        is inside the grid, if not, return to the last step.

        **Parameters:**

            laz_co:*list*
                The current coordination of the lazor point
            direction:*list*
                The direction of the newest lazor

        **Returns**
            *bool*
                True if the lazor is still in the grid
        '''
        width = len(self.grid[0])
        length = len(self.grid)
        x = laz_co[0]
        y = laz_co[1]
        # Determine whether the position is in the grid
        if x < 0 or x > (width - 1) or y < 0 or y > (length - 1) or \
            (x + direction[0]) < 0 or \
            (x + direction[0]) > (width - 1) or \
            (y + direction[1]) < 0 or \
                (y + direction[1]) > (length - 1):
            return True
        else:
            return False


    def lazor_path(self):
        '''
        This function calculates and returns the paths of all lasers.

        **Parameters**

            None

        **Return**

            laser_paths: *list*
                A list containing the paths of all lasers.
        '''
        laser_paths = []
        completed_paths = []

        # Initialize each laser's starting path
        for laser in self.lazorlist:
            laser_paths.append([laser])

        # Limit iterations to prevent infinite loops in cases of circular paths
        for step in range(30):
            for i in range(len(laser_paths)):
                x, y = laser_paths[i][-1][0], laser_paths[i][-1][1]
                dx, dy = laser_paths[i][-1][2], laser_paths[i][-1][3]
                current_pos = [x, y]
                direction = [dx, dy]

                # Continue to next step if laser is outside grid boundary
                if self.check(current_pos, direction):
                    continue

                # Determine the laser’s behavior upon encountering a block
                next_step = self.meet_block(current_pos, direction)

                # Case for B block: laser stops
                if len(next_step) == 0:
                    laser_paths[i].append([x, y, 0, 0])
                    if current_pos in self.holelist and current_pos not in completed_paths:
                        completed_paths.append(current_pos)

                # Case for A block or empty space: laser changes direction
                elif len(next_step) == 2:
                    direction = next_step
                    x += direction[0]
                    y += direction[1]
                    laser_paths[i].append([x, y, direction[0], direction[1]])
                    if [x, y] in self.holelist and [x, y] not in completed_paths:
                        completed_paths.append([x, y])

                # Case for C or D block: laser may split into two paths
                elif len(next_step) == 4:
                    if next_step[0] == 0 or next_step[0] == 2:
                        direction = next_step
                        x += direction[0]
                        y += direction[1]
                        laser_paths[i].append([x, y, direction[2], direction[3]])
                        if [x, y] in self.holelist and [x, y] not in completed_paths:
                            completed_paths.append([x, y])
                    else:
                        # Split laser into two paths at this position
                        x1, y1 = x + next_step[0], y + next_step[1]
                        x2, y2 = x, y
                        laser_paths.append([[x1, y1, next_step[0], next_step[1]]])
                        laser_paths[i].append([x2, y2, next_step[2], next_step[3]])
                        if [x2, y2] in self.holelist and [x2, y2] not in completed_paths:
                            completed_paths.append([x2, y2])
                else:
                    print('Unexpected block type encountered')

        # Check if all target holes are reached
        if len(completed_paths) == len(self.holelist):
            return laser_paths
        else:
            return 0


def find_path(grid, A_num, B_num, C_num, lazorlist, holelist, position):
    '''
    Generate a possible grid with blocks filled in and solves it. If it is the correct grid, we return all the necessary parameters of the grid.

    Parameters remain the same.
    '''
    Blocks = []
    # Extract the blank positions and replace them with blocks
    for a in grid:
        for b in a:
            if b == 'o':
                Blocks.append(b)
    for i in range(A_num):
        Blocks[i] = 'A'
    for i in range(A_num, (A_num + B_num)):
        Blocks[i] = 'B'
    for i in range((A_num + B_num), (A_num + B_num + C_num)):
        Blocks[i] = 'C'

    # Generate a list of permutations of blocks and blank position
    list_Blocks = list(multiset_permutations(Blocks))

    while len(list_Blocks) != 0:
        list_temp = list_Blocks.pop()
        list_temp_save = copy.deepcopy(list_temp)

        # Generate a board from grid function
        ori_grid = Grid(grid)
        test_board = ori_grid.gen_grid(list_temp, position)

        # Test the board with Lazor to see if it is the correct board
        lazor = Lazor(test_board, lazorlist, holelist)
        solution = lazor.lazor_path()

        # We return 0 if the board is incorrect and a list with the path of lasers if it's correct.
        if solution != 0:
            return solution, list_temp_save, test_board
        else:
            continue


def locate_static_blocks(grid):
    '''
    This function identifies static blocks in the initial board layout
    to prevent overwriting them when generating new grids.

    **Parameters**

        grid: *list*
            The original grid layout from the .bff file.

    **Return**

        static_positions: *list*
            A list of coordinates for blocks fixed by the game.
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
    This function extracts the necessary components from a .bff file,
    computes the solution grid, and saves the result as a .bff file.

    **Parameters**

        file_path: *str*
            The filename of the .bff file to be processed.

    **Return**

        solution_grid: *list*
            A list representing the solved grid configuration.
        laser_paths: *list*
            A list containing the paths of all lasers.
        flattened_grid: *list*
            The grid with all elements in a single list.
    '''
    # Parse the .bff file to retrieve grid setup and laser configurations
    parsed_data = read_bff(file_path)
    main_grid = parsed_data[0]
    num_a = parsed_data[1]
    num_b = parsed_data[2]
    num_c = parsed_data[3]
    lasers = parsed_data[4]
    targets = parsed_data[5]
    base_grid = parsed_data[6]

    # Identify the fixed block locations
    fixed_positions = locate_static_blocks(base_grid)

    # Calculate the solution paths, laser tracks, and grid layout
    laser_paths, flattened_grid = find_path(
        main_grid, num_a, num_b, num_c, lasers, targets, fixed_positions
    )[:2]

    # Copy the correct path configuration into the final grid layout
    temp_grid_list = copy.deepcopy(flattened_grid)
    solution_grid = copy.deepcopy(base_grid)
    for i in range(len(solution_grid)):
        for j in range(len(solution_grid[0])):
            if solution_grid[i][j] == 'o':
                solution_grid[i][j] = temp_grid_list.pop(0)

    # Save the solution details back into a new .bff file
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