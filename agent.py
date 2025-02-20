from game import get_valid_moves, get_sub_game_winner, check_end
import game as game

def generate_next_game_states(game_state, valid_moves):
    new_game_states = []

    for move in valid_moves:
        row, col = move
        new_state = [row[:] for row in game_state]  # Create a copy of the game state
        new_state[row][col] = '0'  # Place an 'O' at the valid move position
        new_game_states.append(new_state)

    return new_game_states

def print_state(game_state):
    for row in game_state:
        print(' '.join(row))
    print("\n")

class Node:
    def __init__(self, game_state, last_move, parent=None):
        self.game_state = game_state
        self.last_move = last_move
        self.children = []
        self.parent = parent

def expand_node(node, depth, max_depth, current_player):
    if depth >= max_depth:
        return

    valid_moves = get_valid_moves(node.game_state, node.last_move)
    for move in valid_moves:
        new_state = [row[:] for row in node.game_state]
        row, col = move
        new_state[row][col] = current_player  # Place 'X' or 'O' based on the current player
        child_node = Node(new_state, move, node)
        node.children.append(child_node)
        # Alternate player for the next level
        next_player = 'O' if current_player == 'X' else 'X'
        expand_node(child_node, depth + 1, max_depth, next_player)

def print_tree(node, depth):
    # Print the current node's game state
    print(f"Depth {depth} Node:")
    print_state(node.game_state)

    # Recursively print each child
    for child in node.children:
        print_tree(child, depth + 1)

def print_single_branch(node, depth=0):
    # Print the current node's game state
    print(f"Depth {depth} Node:")
    print_state(node.game_state)

    # If this node has children, continue with the first child
    if node.children:
        print_single_branch(node.children[0], depth + 1)

def count_nodes(node):
    if node is None:
        return 0

    count = 1  # Count the current node
    for child in node.children:
        count += count_nodes(child)  # Count all nodes in the subtree

    return count

def count_winning_opportunities(boards_won, boards_lost):
    winning_combinations = [
        [1, 2, 3], [4, 5, 6], [7, 8, 9],  # Rows
        [1, 4, 7], [2, 5, 8], [3, 6, 9],  # Columns
        [1, 5, 9], [3, 5, 7]              # Diagonals
    ]
    
    count = 0
    for combo in winning_combinations:
        player_wins = [board for board in combo if board in boards_won]
        opponent_wins = [board for board in combo if board in boards_lost]

        # Check if the player has exactly 2 wins and the opponent has none in the combination
        if len(player_wins) == 2 and not any(board in combo for board in boards_lost):
            # Check if the remaining board is not already won
            remaining_board = [board for board in combo if board not in player_wins][0]
            if remaining_board not in boards_won + boards_lost:
                count += 1
    return count

def calculate_blocking_score(boards_won, opponent_boards_potential_win):
    winning_combinations = [
        [1, 2, 3], [4, 5, 6], [7, 8, 9],  # Rows
        [1, 4, 7], [2, 5, 8], [3, 6, 9],  # Columns
        [1, 5, 9], [3, 5, 7]              # Diagonals
    ]

    count = 0
    for combo in winning_combinations:
        if any(board in boards_won for board in combo) and \
           sum(board in opponent_boards_potential_win for board in combo) == 2:
            count += 1
    
    return count

def calculate_score(game_state, player, last_move):
    score = 0
    opponent = 'O' if player == 'X' else 'X'
    boards_won, boards_lost = [], []
    # check if game is over
    if check_end(game_state) == (True, player):
        return 10000
    elif check_end(game_state) == (True, opponent):
        return -10000
    
    # score for individual boards
    #print(get_sub_game_winner(5, game_state))
    for i in range(1,10):
        if get_sub_game_winner(i, game_state) == player:
            if i == 5: 
                score += 100 # winning center board
                boards_won.append(i)
            elif i == 1 or i == 3 or i == 7 or i == 9: 
                score += 80 # 10 points for winning corner board
                boards_won.append(i)
            else: 
                boards_won.append(i)
                score += 70 # winning edge board
        if get_sub_game_winner(i, game_state) == opponent:
            if i == 5: 
                boards_lost.append(i)
                score -= 100 # if enemy has middle board
            elif i == 1 or i == 3 or i == 7 or i == 9: 
                boards_lost.append(i)
                score -= 80 # if enemy has corner board
            else: 
                boards_lost.append(i)
                score -= 70 # if enemy has edge
    
    # check for consecutive boards won
    score += 100 * count_winning_opportunities(boards_won, boards_lost) # add 100 points for each board lined up for a game win
    score -= 100 * count_winning_opportunities(boards_lost, boards_won) # subtract 100 points for each board opponent has lined up for a win

    # add points if blocking opponent from winning
    score += 150 * calculate_blocking_score(boards_won, boards_lost) # add 150 points if blocking opponent from winning
    score -= 150 * calculate_blocking_score(boards_lost, boards_won) # subtract 150 points if won a board that opponent has blocked

    # check for small boards 1 away from winning
    for i in range(1,10): # iterate through all boards
        if i in boards_won or i in boards_lost:
            continue # if board is won or lost, skip
        sub_board = game.get_sub_board(game_state, i)
        squares_won = []
        squares_lost = []
        i=1   
        for row in sub_board:
            for ele in row:
                if ele == player:
                    squares_won.append(i)
                elif ele == opponent:
                    squares_lost.append(i)
                i+=1

        
        score += 10 * count_winning_opportunities(squares_won, squares_lost) # add 10 points for each board lined up for a sub-board win
        score -= 10 * count_winning_opportunities(squares_lost, squares_won) # subtract for opponent



    return score

def is_terminal(node):
    if check_end(node.game_state)[0] == True:
        return True
    possible_moves = game.get_valid_moves(node.game_state, node.last_move)
    if len(possible_moves) == 0:
        return True
    
    return False

def minimax(node, depth, is_maximizing_player, player):
    if depth == 0 or is_terminal(node):
        return calculate_score(node.game_state, 'O', node.last_move), node  # Return score and node

    if is_maximizing_player:
        max_eval = float('-inf')
        best_node = None
        for child in node.children:
            eval, _ = minimax(child, depth - 1, False, player)
            #print(f'max: {eval}')
            if eval > max_eval:
                max_eval = eval
                best_node = child
        return max_eval, best_node
    else:
        min_eval = float('inf')
        worst_node = None
        for child in node.children:
            eval, _ = minimax(child, depth - 1, True, player)
            #print(f'min: {eval}')
            if eval < min_eval:
                min_eval = eval
                worst_node = child
        return min_eval, worst_node

def print_minimax(root_node):

    for child in root_node.children:
        state = child.game_state
        score= minimax(child, 4, False, player='O')  # Adjust depth and player accordingly
        print("Game State:")
        print_state(state)
        print("Score:", score)
        print("\n")

teststate = [[' ', ' ', ' ', ' ', ' ', ' ', 'X', ' ', 'O'], ['O', ' ', 'X', ' ', ' ', 'X', ' ', 'X', ' '], [' ', ' ', 'X', ' ', ' ', ' ', ' ', ' ', 'X'], [' ', ' ', ' ', ' ', ' ', 'O', 'O', 'O', 'O'], [' ', ' ', 'X', ' ', 'X', 'O', ' ', 'X', ' '], [' ', ' ', ' ', ' ', ' ', 'O', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ''], [' ', ' ', ' ', ' ', ' ', ' ', ' ', '', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']]
teststate2 = [['X', ' ', 'X', ' ', ' ', ' ', ' ', ' ', 'O'], [' ', 'O', ' ', ' ', ' ', ' ', ' ', 'O', 'X'], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', 'O', ' ', 'X', ' ', ' ', ' '], [' ', ' ', ' ', ' ', 'X', ' ', 'O', ' ', ' '], ['X', ' ', 'O', ' ', ' ', ' ', ' ', ' ', 'O'], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', 'X', ' ', 'X'], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']]

#print(calculate_score(teststate2, 'O'))
#print(time.time() - start_time)

test3 = [['O', ' ', 'O', ' ', ' ', 'O', 'X', 'X', ' '], ['X', 'X', ' ', ' ', ' ', ' ', ' ', ' ', 'X'], ['O', ' ', ' ', ' ', ' ', 'X', ' ', ' ', 'X'], [' ', ' ', ' ', ' ', ' ', 'O', ' ', ' ', ' '], [' ', ' ', ' ', ' ', 'X', 'O', ' ', 'X', ' '], [' ', 'O', ' ', ' ', ' ', 'O', 'O', ' ', ' '], ['X', ' ', ' ', 'X', ' ', ' ', 'O', 'O', 'O'], [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'X', ' '], [' ', ' ', 'X', ' ', ' ', ' ', ' ', ' ', ' ']]
# recent move = (6,0)

test4 = [[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', 'X', ' ', ' ', ' ', 'X', ' ', ' '], [' ', ' ', ' ', ' ', ' ', 'O', ' ', ' ', ' '], [' ', ' ', ' ', ' ', 'X', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], ['O', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], ['X', ' ', ' ', ' ', ' ', ' ', 'O', ' ', ' ']]
# recent move = (8,0)

gstate = [['O', ' ', ' ', ' ', ' ', ' ', 'X', ' ', ' '], [' ', 'O', ' ', ' ', ' ', ' ', ' ', ' ', 'X'], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'X'], [' ', ' ', ' ', ' ', ' ', 'O', ' ', ' ', 'O'], [' ', ' ', ' ', ' ', 'X', 'O', ' ', 'X', ' '], [' ', ' ', ' ', ' ', ' ', 'O', ' ', ' ', 'X'], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'O'], [' ', ' ', 'O', ' ', ' ', ' ', ' ', 'X', ' '], [' ', ' ', ' ', ' ', ' ', 'X', 'X', ' ', 'O']]
gstate2 = [['O', 'O', 'O', ' ', ' ', ' ', '', ' ', ' '], [' ', '', ' ', ' ', ' ', ' ', ' ', ' ', 'X'], [' ', ' ', ' ', 'O', 'O', 'O', ' ', ' ', 'X'], [' ', ' ', ' ', ' ', ' ', '', ' ', ' ', 'O'], ['X', 'X', 'X', ' ', '', '', ' ', '', ' '], [' ', ' ', ' ', ' ', ' ', 'O', ' ', ' ', 'X'], [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'O'], [' ', ' ', 'O', ' ', ' ', ' ', ' ', 'X', ' '], [' ', ' ', ' ', ' ', ' ', '', 'X', ' ', '']]

#print(calculate_score(gstate, 'O'))
#print_state(gstate)

def get_next_move(game_state, last_move, player):
    valid_moves = get_valid_moves(game_state, last_move)
    if len(valid_moves) == 1:
        return valid_moves[0]

    root_state = game_state  # Initial game state
    root_node = Node(game_state=root_state, last_move=last_move)
    expand_node(root_node, 0, max_depth=4, current_player=player)

    best_score = float('-inf')
    best_move = None

    scores = []
    for child in root_node.children:
        score, _ = minimax(child, depth=3, is_maximizing_player=True, player=player)  # Adjust the depth and player as needed
        scores.append(score)
        if score > best_score:
            best_score = score
            best_move = child

    # best_move now holds the child node with the highest score
    #print(best_move.last_move)
    #print_state(best_move.game_state)  # Assuming print_state is your function to print a game state
    grandchildren_scores = []
    for grandchild in best_move.children:
        grandchildren_scores.append(calculate_score(grandchild.game_state, grandchild.last_move, player))
    #print(best_score, scores, grandchildren_scores)

    return best_move.last_move

