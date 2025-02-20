import pygame
import sys
import time
from agent import get_next_move

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 2
BOARD_ROWS, BOARD_COLS = 9, 9
SQUARE_SIZE = WIDTH // BOARD_COLS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
first_move = True

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Tic Tac Toe")

# Game state
game_state = [[' ' for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
current_player = 'X'


def draw_board():
    # Draw all gray sub-lines
    for row in range(1, BOARD_ROWS):
        if row % 3 != 0:  # Draw gray lines for sub-grids
            pygame.draw.line(screen, GRAY, (0, row * SQUARE_SIZE), (WIDTH, row * SQUARE_SIZE), LINE_WIDTH)
    for col in range(1, BOARD_COLS):
        if col % 3 != 0:  # Draw gray lines for sub-grids
            pygame.draw.line(screen, GRAY, (col * SQUARE_SIZE, 0), (col * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

    # Draw the black lines for the main 3x3 grid
    for row in range(0, BOARD_ROWS, 3):
        pygame.draw.line(screen, BLACK, (0, row * SQUARE_SIZE), (WIDTH, row * SQUARE_SIZE), LINE_WIDTH * 3)
    for col in range(0, BOARD_COLS, 3):
        pygame.draw.line(screen, BLACK, (col * SQUARE_SIZE, 0), (col * SQUARE_SIZE, HEIGHT), LINE_WIDTH * 3)

def mark_square(row, col, player):
    game_state[row][col] = player

def check_click_position(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
            radius = SQUARE_SIZE // 3  # Smaller radius for 'O'
            offset = SQUARE_SIZE // 4  # Offset for 'X' start and end points

            if game_state[row][col] == 'X':
                pygame.draw.line(screen, RED, (center_x - offset, center_y - offset), (center_x + offset, center_y + offset), LINE_WIDTH * 2)
                pygame.draw.line(screen, RED, (center_x + offset, center_y - offset), (center_x - offset, center_y + offset), LINE_WIDTH * 2)
            elif game_state[row][col] == 'O':
                pygame.draw.circle(screen, BLUE, (center_x, center_y), radius, LINE_WIDTH * 2)

def switch_player(player):
    return 'X' if player == 'O' else 'O'

def find_section(x, y):
    if 0 <= x < 3:
        if 0 <= y < 3:
            return 1
        elif 3 <= y < 6:
            return 4
        elif 6 <= y <= 9:
            return 7
    elif 3 <= x < 6:
        if 0 <= y < 3:
            return 2
        elif 3 <= y < 6:
            return 5
        elif 6 <= y <= 9:
            return 8
    elif 6 <= x <= 9:
        if 0 <= y < 3:
            return 3
        elif 3 <= y < 6:
            return 6
        elif 6 <= y <= 9:
            return 9

def subsection(x,y):
    x+=1
    y+=1

    if x % 3 == 1:
        row = 1
    if x % 3 == 2:
        row = 2
    if x % 3 == 0:
        row = 3

    if y % 3 == 1:
        col = 1
    if y % 3 == 2:
        col = 2
    if y % 3 == 0:
        col = 3
    
    
    if (row,col) == (1,1):
        return 1
    if (row,col) == (2,1):
        return 2
    if (row,col) == (3,1):
        return 3
    if (row,col) == (1,2):
        return 4
    if (row,col) == (2,2):
        return 5
    if (row,col) == (3,2):
        return 6
    if (row,col) == (1,3):
        return 7
    if (row,col) == (2,3):
        return 8
    if (row,col) == (3,3):
        return 9

def get_sub_board(game_state, sub_board_number):
    if sub_board_number < 1 or sub_board_number > 9:
        raise ValueError("Sub-board number must be between 1 and 9.")

    # Calculate the starting row and column indices for the sub-board
    start_row = ((sub_board_number - 1) // 3) * 3
    start_col = ((sub_board_number - 1) % 3) * 3

    # Extract the 3x3 sub-board
    sub_board = [row[start_col:start_col + 3] for row in game_state[start_row:start_row + 3]]
    return sub_board    

def check_win(board, player):
    # Check rows
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] == player:
            return True

    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] == player:
            return True

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] == player:
        return True
    if board[0][2] == board[1][1] == board[2][0] == player:
        return True

    return False
    
def input_is_valid(x,y, board_num):
    board_num = board_num - 1
    target_board = get_sub_board(game_state, board_num+1)

    #print(target_board)
    if check_win(target_board, 'X'):
        print('board is won by X')
        if find_section(x,y) != board_num + 1:
            return True
        return False
    if check_win(target_board, 'O'):
        print('board is won by O')
        if find_section(x,y) != board_num + 1:
            return True
        first_move = True
        return False

    if find_section(x,y) == board_num + 1:
        return True

    print(target_board)

def check_end(game_state):
    # Create a new board representing the status of each 3x3 sub-board
    sub_board_status = [[' ' for _ in range(3)] for _ in range(3)]

    # Check each sub-board and update the status
    for sub_board_num in range(1, 10):
        sub_board = get_sub_board(game_state, sub_board_num)
        if check_win(sub_board, 'X'):
            sub_board_status[(sub_board_num - 1) // 3][(sub_board_num - 1) % 3] = 'X'
        elif check_win(sub_board, 'O'):
            sub_board_status[(sub_board_num - 1) // 3][(sub_board_num - 1) % 3] = 'O'

    # Check if either player has won the overall game
    if check_win(sub_board_status, 'X'):
        return True, 'X'
    elif check_win(sub_board_status, 'O'):
        return True, 'O'
    
    return False, None        

def get_sub_game_winner(sub_board_number, game_state):
    sub_board = get_sub_board(game_state, sub_board_number)
    if check_win(sub_board, 'X'):
        return 'X'
    elif check_win(sub_board, 'O'):
        return 'O'
    return None

def draw_sub_game_backgrounds():
    border_reduction = LINE_WIDTH * 3 // 2  # Adjust this as needed
    for sub_board_num in range(1, 10):
        winner = get_sub_game_winner(sub_board_num, game_state)
        if winner:
            top_left_x = ((sub_board_num - 1) % 3) * 3 * SQUARE_SIZE + border_reduction
            top_left_y = ((sub_board_num - 1) // 3) * 3 * SQUARE_SIZE + border_reduction
            width = SQUARE_SIZE * 3 - 2 * border_reduction
            height = SQUARE_SIZE * 3 - 2 * border_reduction

            # Lighter shades with low opacity for both red and blue
            if winner == 'X':
                color = (255, 192, 203, 20)  # Lighter red (pinkish) with low opacity
            else:
                color = (173, 216, 230, 20)  # Lighter blue with low opacity

            pygame.draw.rect(screen, color, (top_left_x, top_left_y, width, height))

def draw_lines():
    # Draw all gray sub-lines
    for row in range(1, BOARD_ROWS):
        if row % 3 != 0:  # Draw gray lines for sub-grids
            pygame.draw.line(screen, GRAY, (0, row * SQUARE_SIZE), (WIDTH, row * SQUARE_SIZE), LINE_WIDTH)
    for col in range(1, BOARD_COLS):
        if col % 3 != 0:  # Draw gray lines for sub-grids
            pygame.draw.line(screen, GRAY, (col * SQUARE_SIZE, 0), (col * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

    # Draw the black lines for the main 3x3 grid
    for row in range(0, BOARD_ROWS, 3):
        pygame.draw.line(screen, BLACK, (0, row * SQUARE_SIZE), (WIDTH, row * SQUARE_SIZE), LINE_WIDTH * 3)
    for col in range(0, BOARD_COLS, 3):
        pygame.draw.line(screen, BLACK, (col * SQUARE_SIZE, 0), (col * SQUARE_SIZE, HEIGHT), LINE_WIDTH * 3)

def get_valid_moves(game_state, last_move):
    valid_moves = []

    # Find the sub-board the player must play in
    target_sub_board = subsection(last_move[1], last_move[0])

    # Check if the target sub-board is full or already won
    if check_win(get_sub_board(game_state, target_sub_board), 'X') or \
       check_win(get_sub_board(game_state, target_sub_board), 'O') or \
       all(cell != ' ' for row in get_sub_board(game_state, target_sub_board) for cell in row):
        # If full or won, the player can play anywhere
        for row in range(9):
            for col in range(9):
                if game_state[row][col] != 'X' and game_state[row][col] != 'O':
                    valid_moves.append((row, col))
    else:
        # Calculate the starting indices of the target sub-board
        start_row = ((target_sub_board - 1) // 3) * 3
        start_col = ((target_sub_board - 1) % 3) * 3

        # Add valid moves within the target sub-board
        for row in range(start_row, start_row + 3):
            for col in range(start_col, start_col + 3):
                if game_state[row][col] != 'X' and game_state[row][col] != 'O':
                    valid_moves.append((row, col))

    return valid_moves


def main():
    screen.fill(WHITE)
    draw_lines() 
    pygame.display.update()
    global first_move
    global current_player
    global last_move
    global target_subsection

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if current_player == 'X':
            # Wait for mouse click event
            event = pygame.event.wait()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                clicked_row, clicked_col = check_click_position((mouseX, mouseY))
                process_move(clicked_row, clicked_col)
                screen.fill(WHITE)
                draw_sub_game_backgrounds()  # Draw the backgrounds first
                draw_lines()                 # Then draw all the lines
                draw_figures()               # Finally, draw the figures
                pygame.display.update()
        else:
            # AI's turn to calculate its move
            start_time = time.time()
            clicked_row, clicked_col = get_next_move(game_state, last_move, 'O')
            process_move(clicked_row, clicked_col)
            draw_sub_game_backgrounds()
            draw_lines()
            draw_figures()
            pygame.display.update()
            end_time = time.time()
            print(f"AI processing time: {end_time - start_time} seconds")

def process_move(row, col):
    global first_move
    global current_player
    global last_move
    global target_subsection

    if game_state[row][col] == ' ':
        if first_move or input_is_valid(col, row, target_subsection):
            mark_square(row, col, current_player)
            draw_figures()  # Draw the move on the board
            current_player = switch_player(current_player)
            last_move = (row, col)
            target_subsection = subsection(col, row)
            valid_moves = get_valid_moves(game_state, last_move)
            first_move = False
            over_bool, winner = check_end(game_state)
            if over_bool:
                print(f"the game has been won by {winner}")
        else:
            print(f'Please choose in the proper section ({target_subsection})')

# Run the main game loop
main()
