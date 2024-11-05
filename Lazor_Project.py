from PIL import Image, ImageDraw
from sympy.utilities.iterables import multiset_permutations
import copy
import time


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
            L_temp = []
            P_temp = []
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
    # Here are some troubleshooting for '.bff' files
    # Unreasonable block number
    if (A_num + B_num + C_num) == 0:
        raise Exception('There are no available block ABC')
    if (A_num + B_num + C_num) >= row * column:
        raise Exception('There are more blocks than available spaces')
    # No lasers
    if len(L_list) == 0:
        raise Exception('There are no lasors')
    for i in range(len(L_list)):
        # The format of the lasor is incorrect
        if len(L_list[i]) != 4:
            raise Exception('The format of the lasor is incorrect')
    # The start points of lasers are unreasonable
        if L_list[i][0] < 0 or L_list[i][0] > column * 2 or L_list[i][1] < 0 or L_list[i][1] > row * 2:
            raise Exception('The start point of lasors are out of the grid')
    # The directions of the lasors are unreasonable
        if (L_list[i][2] != -1 and L_list[i][2] != 1) or (L_list[i][3] != -1 and L_list[i][3] != 1):
            raise Exception('The directions of lasors are unreasonable')
    for i in range(len(P_list)):
        # The end points are unreasonable
        if P_list[i][0] < 0 or P_list[i][0] > column * 2 or P_list[i][1] < 0 or P_list[i][1] > row * 2:
            raise Exception('The end point of lasors are out of the grid')
    # No end points
    if len(P_list) == 0:
        raise Exception('There are no end points')

    # Any element other than 'ABCxo' in grid
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] not in ['x', 'o', 'A', 'B', 'C']:
                raise Exception('There are undefined characters in the grid')

    return gridfull, A_num, B_num, C_num, L_list, P_list, grid_origin


def get_colors():
    '''
    The idea of the code comes from the maze lab of the software carpentry class.
    Colors map that the lazor board will use:
        0 - BlackGray - The background
        A - White - A reflect block
        B - Black - A black block
        C - transparent - A transparent block
        o - Gray - A possible space for putting block
        x - BlackGray - A place that could not have block

    **Returns**

        color_map: *dict, int, tuple*
            A dictionary that will correlate the integer key to a color.
    '''
    return {
        0: (20, 20, 20),
        'A': (255, 255, 255),
        'B': (0, 0, 0),
        'C': (255, 0, 0),
        'o': (100, 100, 100),
        'x': (50, 50, 50),
    }


def save_solution_bff(solved_board, answer_lazor, lazors_info, holes, filename):
    '''
    This function saves the solution as a .bff file with clear laser path branching.

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

        # Write laser path solution with branching details
        f.write("LASER PATH\n")
        for path in answer_lazor:
            main_path_points = set()  # Track points on the main path
            f.write("Main Path:\n  ")

            split_detected = False  # Track whether a split was detected

            for i, point in enumerate(path):
                point_tuple = tuple(point[:2])  # Convert list to tuple for hashability, using only coordinates

                if point_tuple in main_path_points and i > 0 and not split_detected:
                    # Detect split point and branch
                    f.write(f"\n  Split at {point[:2]}:\n")
                    split_detected = True

                    # Write the reflection path
                    f.write("    Reflection Path: ")
                    for j in range(i, len(path)):
                        if j < len(path) - 1:
                            f.write(f"({path[j][0]}, {path[j][1]}) -> ")
                        else:
                            f.write(f"({path[j][0]}, {path[j][1]})\n")

                    # Write the transmission path
                    f.write("    Transmission Path: ")
                    continue  # Skip to transmission path section
                elif split_detected:
                    # Continue with transmission path after split
                    if i < len(path) - 1:
                        f.write(f"({point[0]}, {point[1]}) -> ")
                    else:
                        f.write(f"({point[0]}, {point[1]})\n")
                else:
                    # Continue main path
                    if i < len(path) - 1:
                        f.write(f"({point[0]}, {point[1]}) -> ")
                    else:
                        f.write(f"({point[0]}, {point[1]})\n")
                    main_path_points.add(point_tuple)
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
    This Function class is a wrapper for identifying right grid and return a lazor path

    **Parameters**

        grid : *list*
            A list of list stand for a possible grid of the solution
        lazorlist : *list*
            A list of list stand for start point and direction of lazor
        holelist : *list*
            A list of list stand for the position of the end point or the hole
    '''

    def __init__(self, grid, lazorlist, holelist):
        self.grid = grid
        self.lazorlist = lazorlist
        self.holelist = holelist

    def block(self, block_type):
        '''
        This function is to identify the function of different blocks

        **Parameters**

            block_type: *str*
                This represents different blocks
                'A': Reflect block
                'B': Opaque block
                'C': Refract block
                'D': Crstal block
                'o': Blank space
                'x': unavailable space

        **Return**

            new_direction: *list*
                The new direction of lasors
        '''
        self.type = block_type
        new_direction = []
        # When lasors touch the reflect block
        if self.type == 'A':
            if self.point[0] & 1 == 0:
                new_direction = [self.direction[0] * (-1), self.direction[1]]
            else:
                new_direction = [self.direction[0], self.direction[1] * (-1)]
        # When lasors touch the opaque block
        elif self.type == 'B':
            new_direction = []
        # When lasors touch the refract block
        elif self.type == 'C':
            if self.point[0] & 1 == 0:
                new_direction = [self.direction[0], self.direction[1],
                                 self.direction[0] * (-1), self.direction[1]]
            else:
                new_direction = [self.direction[0], self.direction[1],
                                 self.direction[0], self.direction[1] * (-1)]
        # When lasors touch the crystal block
        elif self.type == 'D':
            if self.point[0] & 1 == 0:
                new_direction = [2, 0,
                                 self.direction[0], self.direction[1]]
            else:
                new_direction = [0, 2,
                                 self.direction[0], self.direction[1]]
        # When lasors touch the blank space
        elif self.type == 'o' or self.type == 'x' :
            new_direction = self.direction

        return new_direction

    def meet_block(self, point, direction):
        '''
        This function will check whether the lasor encounter a functional block
        and returns the new direction of the lasor

        **Parameters**

            point: *list*
                The current lazor position
            direction: *list*
                The current direction of lazor

        **Return**

            new_direction: *list*
                A list that includes new directions of lazor after meeting functional block
        '''
        self.point = point
        self.direction = direction
        # Calculate the next position of the laser
        x1, y1 = point[0], point[1] + direction[1]
        x2, y2 = point[0] + direction[0], point[1]
        # Obtain the block laser touches
        if point[0] & 1 == 1:
            block_type = self.grid[y1][x1]
            new_direction = self.block(block_type)
        if point[0] & 1 == 0:
            block_type = self.grid[y2][x2]
            new_direction = self.block(block_type)

        return new_direction

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
        This function can return a list of the lasors path

        **Parameters**

            None

        **Return**

            lazorlist: *list*
                A list contains lasors path
        '''
        result = []
        lazorlist = []
        # Get the lasers' list from input and store them into lazorlist
        for p in range(len(self.lazorlist)):
            lazorlist.append([self.lazorlist[p]])
        # IMPORTANT!!!
        # 'n' here is to avoid infinite loop of laser in a circle
        # The range can be bigger, but the bigger it is, the slower the script runs
        # It cannot be too small because of the limitations of some levels
        for n in range(30):
            # The original lazor is added to the lazor list
            for k in range(len(lazorlist)):
                coordination_x = lazorlist[k][-1][0]
                coordination_y = lazorlist[k][-1][1]
                direction_x = lazorlist[k][-1][2]
                direction_y = lazorlist[k][-1][3]
                coordination = [coordination_x, coordination_y]
                direction = [direction_x, direction_y]
                # Checking if the lazor and its next step is inside the boundary
                if self.check(coordination, direction):
                    continue
                else:
                    # Receiving the coordination & direction of lazor after a step
                    next_step = self.meet_block(coordination, direction)
                    # If there are no elements in the list, it indicates it is block B
                    if len(next_step) == 0:
                        lazorlist[k].append([
                            coordination[0], coordination[1], 0, 0])
                        if (coordination in self.holelist) and (coordination not in result):
                            result.append(coordination)
                    # If there are 2 elements, it is "o" or A block
                    elif len(next_step) == 2:
                        direction = next_step
                        coordination = [
                            coordination[0] + direction[0], coordination[1] + direction[1]]
                        lazorlist[k].append(
                            [coordination[0], coordination[1], direction[0], direction[1]])
                        if (coordination in self.holelist) and (coordination not in result):
                            result.append(coordination)
                    # If there are 4 elements, it is C block or D block, we seperate them and add the straight line to a new list in lazor list,
                    # and the other to the list under the original lazor
                    elif len(next_step) == 4:
                        if next_step[0] == 0 or next_step[0] == 2:
                            direction = next_step
                            coordination = [
                            coordination[0] + direction[0], coordination[1] + direction[1]]
                            lazorlist[k].append(
                                [coordination[0], coordination[1], direction[2], direction[3]])
                            if (coordination in self.holelist) and (coordination not in result):
                                result.append(coordination)
                        else:
                            direction = next_step
                            coordination_newlaz1 = [
                                coordination[0] + direction[0], coordination[1] + direction[1]]
                            coordination_newlaz2 = [
                                coordination[0], coordination[1]]
                            lazorlist.append(
                                [[coordination_newlaz1[0], coordination_newlaz1[1], direction[0], direction[1]]])
                            lazorlist[k].append(
                                [coordination_newlaz2[0], coordination_newlaz2[1], direction[2], direction[3]])
                            coordination = coordination_newlaz2
                            if (coordination in self.holelist) and (coordination not in result):
                                result.append(coordination)
                    else:
                        print('Wrong')
        if len(result) == len(self.holelist):
            return lazorlist
        else:
            return 0


def obvs_judge(gridfull_temp, possible_list, list_temp, holelist):
    '''
    This function can skip some obveriously wrong solution

    **Parameters**

        gridfull_temp: *list*
            The grid about to be solved

        possible_list: *list
            All possible permutations of 'ABCo'.

        list_temp: *list*
            The permutation currently being used.

        holelist: *list*
            The positions of the end points

    **Return**

        None
    '''
    for jj in range(len(holelist)):  # Ruling out grids that have blocks blocking a hole
        x_hole = holelist[jj][1]
        y_hole = holelist[jj][0]
        if ((gridfull_temp[x_hole][y_hole + 1] in ['A', 'B']) and (gridfull_temp[x_hole][y_hole - 1] in ['A', 'B'])) or \
                ((gridfull_temp[x_hole + 1][y_hole] in ['A', 'B']) and (gridfull_temp[x_hole - 1][y_hole] in ['A', 'B'])):
            return False
        else:
            return True


def find_path(grid, A_num, B_num, C_num, lazorlist, holelist, position):
    '''
    Generate a possible grid with blocks filled in and solves it, if it is the right grid, we return all the necessary parameters of the grid

    **Parameters**

        grid: *list*
            The full grid in the form of a coordinate system
        A_num: *int*
            The number of A-block available
        B_num: *int*
            The number of B-block available
        C_num: *int*
            The number of C-block available
        lazorlist: *list*
            The first two elements is the positon of the start point, the last two elements are the direction.
        holelist: *list*
            The positions of the end points
        position: *list*
            A list store the pre-placed blocks

    **Return**

        solution: *list*
            The positions and directions laser passed
        list_temp_save: *list*
            One possible permutation of blocks
        test_board: *list*
            The full grid in coordination
    '''
    Blocks = []
    # Wxtract the blank positions and replace them with blocks
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
    # Generate a list of permutations of blocks and blank postion
    list_Blocks = list(multiset_permutations(Blocks))

    while len(list_Blocks) != 0:
        list_temp = list_Blocks[-1]
        list_temp_save = copy.deepcopy(list_temp)
        list_Blocks.pop()
        # Generate a board from grid function
        ori_grid = Grid(grid)
        test_board = ori_grid.gen_grid(list_temp, position)
        # Test the board with obvs_judge and run it through Lazor to see if it is the right board
        if obvs_judge(test_board, list_Blocks, list_temp, holelist):
            lazor = Lazor(test_board, lazorlist, holelist)
            solution = lazor.lazor_path()
            # We retunr 0 if the board is wrong and return a list with the path of lazors if its right.
            if solution != 0:
                return solution, list_temp_save, test_board
            else:
                continue


def find_fixed_block(smallgrid):
    '''
    This function looks for blocks that were in the original board
    so that we wouldn't replace it when generating grids

    **Parameters**

        smallgrid: *list*
            This is the orignial grid provided by the .bff file

    **Return**

        position: *list*
            The coordination of the fixed blocks provided by the game
    '''
    position = []
    for i in range(len(smallgrid)):
        for j in range(len(smallgrid[0])):
            block = smallgrid[i][j]
            if block == 'A' or block == 'B' or block == 'C':
                position.append([i*2+1, j*2+1])
    return position


def solver(fptr):
    '''
    This function provides all the necessary parameters of the correct grid
    and generates a .bff file of the result

    **Parameters**

        fptr: *str*
            This is the .bff file name you want to run.

    **Return**

        good_grid: *list*
            A list representing the correct grid
        answer: *list*
            A list containing all laser paths
        lazor: *list*
            The correct grid but every element in one list
    '''
    # Read the .bff file and extract the grid, block numbers, lasers, holes, etc.
    read = read_bff(fptr)
    grid = read[0]
    a = read[1]
    b = read[2]
    c = read[3]
    lazorlist = read[4]
    holelist = read[5]
    smallgrid = read[6]

    # Find the positions of fixed blocks
    position = find_fixed_block(smallgrid)

    # Find the solution grid, laser paths, and correct configuration
    answer, lazor = find_path(grid, a, b, c, lazorlist, holelist, position)[:2]

    # Generate the original board with the correct laser path
    good_list = copy.deepcopy(lazor)
    good_grid = copy.deepcopy(smallgrid)
    for row in range(len(good_grid)):
        for column in range(len(good_grid[0])):
            if good_grid[row][column] == 'o':
                good_grid[row][column] = good_list.pop(0)

    # Save the solution as a .bff file instead of an image
    save_solution_bff(solved_board=good_grid, answer_lazor=answer,
                      lazors_info=lazorlist, holes=holelist, filename=fptr)

    return good_grid, answer, lazor


if __name__ == "__main__":
    t0 = time.time()
    solver('dark_1.bff')
    solver('mad_1.bff')
    solver('mad_4.bff')
    #solver('numbered_6.bff')
    #solver('showstopper_4.bff')
    #solver('tiny_5.bff')
    #solver('mad_7.bff')
    t1 = time.time()
    print(t1 - t0)