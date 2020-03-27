"""
An AI player for Othello. 
"""

# gotta make moves within 10 seconds

import random
import sys
import time
import math
import heapq

# need a dctionary that maps a board state to its minimax value
# the key is the board and the value is the 

cache = {}

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    score = get_score(board) # (# of dark disks, # of light disks), color 1 for dark and 2 for light
    final = (score[0] - score[1]) if color == 1 else (score[1] - score[0])    
    return final

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    return 0 #change this!

############ MINIMAX ###############################
# returns lowest possible utility 
# TODO: add cache to minimax 
# TODO: should compute utility be for the opponent or for the color
def minimax_min_node(board, color, limit, caching = 0):
    opponent = 1 if color == 2 else 2
    moves = get_possible_moves(board, opponent) # get moves the opponent can make
    min_util = math.inf
    best_move = None
    sorted_moves = []

    if caching and board in cache:
        return cache[board]
    
    if not moves or limit == 0:
        return (None, compute_utility(board, color)) # score of current player
    
    if not moves or limit == 0:
        return (None, compute_utility(board,color))
        
    for move in moves:
        board_after_play = play_move(board, opponent, move[0], move[1])
        util = compute_utility(board_after_play, color)
        sorted_moves.append((board_after_play, move, util))
    
    for item in sorted_moves:
        board_after_play = item[0]
        result = minimax_max_node(board_after_play, color, limit - 1, caching)
        utility = result[1]
        
        if utility < min_util:
            best_move = item[1]
            min_util = utility
    
    return (best_move, min_util)

# returns highest possible utility
def minimax_max_node(board, color, limit, caching = 0): 
    opponent = 1 if color == 2 else 2
    moves = get_possible_moves(board, color)
    max_util = -math.inf
    best_move = None
    sorted_moves = []
    
    if caching and board in cache:
        return cache[board]
    
    if not moves or limit == 0:
        return (None, compute_utility(board, color))
    
    for move in moves:
        board_after_play = play_move(board, color, move[0], move[1])
        util = compute_utility(board_after_play, color)
        sorted_moves.append((board_after_play, move, util))
    
    for item in sorted_moves:
        board_after_play = item[0]
        # board_after_play = play_move(board, color, move[0], move[1])
        result = minimax_min_node(board_after_play, color, limit - 1, caching)
        utility = result[1]
        
        if utility > max_util:
            best_move = item[1]
            max_util = utility
    
    return (best_move, max_util)

def select_move_minimax(board, color, limit, caching = 0):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  
    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    """
    result = minimax_max_node(board, color, limit, caching)
    return result[0]
    
############ ALPHA-BETA PRUNING #####################
# should my cache keep track of who the player is
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    opponent = 1 if color == 2 else 2
    best_move = None
    min_util = math.inf
    moves = get_possible_moves(board, opponent) 
    sorted_moves = []
    unsorted_moves = []
    select_list = []
    
    if caching and board in cache:
        return cache[board]
    
    if not moves or limit == 0:
        return (None, compute_utility(board,color))
        
    # SORT
    for move in moves:
        board_after_play = play_move(board, opponent, move[0], move[1])
        util = compute_utility(board_after_play, color)
        unsorted_moves.append((util, board_after_play, move))
        heapq.heappush(sorted_moves, (util, board_after_play, move))

    if ordering:
        select_list = sorted_moves
    else:
        select_list = unsorted_moves
        # sorted_moves.sort(key = lambda x: x[2]) # sort by utility value
    
    # CACHE
    for item in select_list:
        board_after_play = item[1]
        result = alphabeta_max_node(board_after_play, color, alpha, beta, limit - 1, caching, ordering)
        
        if result[1] < min_util:
            best_move = item[2]
            min_util = result[1]
            
        if min_util <= alpha: 
            if caching: cache[board] = (best_move, min_util)
            return (best_move, min_util)
        
        beta = min(beta, min_util)
    
    if caching: cache[board] = (best_move, min_util)
    return (best_move, min_util)

# maximizer
# TODO: maybe change caching so that it stores the max min shit
def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):        
    opponent = 1 if color == 2 else 2
    best_move = None
    max_util = -math.inf
    moves = get_possible_moves(board, color)
    sorted_moves = []
    unsorted_moves = []
    select_list = []
    
    if caching and board in cache:
        return cache[board]
    
    if not moves or limit == 0:
        return (None, compute_utility(board, color))
    
    for move in moves: 
        board_after_play = play_move(board, color, move[0], move[1])
        util = compute_utility(board_after_play, color)
        # seperate into sorted and unsorted
        unsorted_moves.append((util, board_after_play, move))
        heapq.heappush(sorted_moves, (-util, board_after_play, move))

    if ordering:
        select_list = sorted_moves
    else:
        select_list = unsorted_moves
            
    # if ordering:            
    #     sorted_moves.sort(reverse = True, key = lambda x: x[2]) # sort by utility value

    for item in select_list:
        board_after_play = item[1]
        result = alphabeta_min_node(board_after_play, color, alpha, beta, limit - 1, caching, ordering)            
        if result[1] > max_util:
            best_move = item[2]
            max_util = result[1]
            
        if max_util >= beta: 
            if caching: cache[board] = (best_move, max_util)
            return (best_move, max_util)
        
        alpha = max(alpha, max_util)
    
    if caching: cache[board] = (best_move, max_util)
    return (best_move, max_util)

def select_move_alphabeta(board, color, limit, caching = 0, ordering = 0):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations. 
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations. 
    """
    alpha = -math.inf
    beta = math.inf
    
    result = alphabeta_max_node(board, color, alpha, beta, limit, caching, ordering)
    cache.clear()
    return result[0] 

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Othello AI") # First line is the name of this AI
    arguments = input().split(",")
    
    color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light. 
    limit = int(arguments[1]) #Depth limit
    minimax = int(arguments[2]) #Minimax or alpha beta
    caching = int(arguments[3]) #Caching 
    ordering = int(arguments[4]) #Node-ordering (for alpha-beta only)

    if (minimax == 1): eprint("Running MINIMAX")
    else: eprint("Running ALPHA-BETA")

    if (caching == 1): eprint("State Caching is ON")
    else: eprint("State Caching is OFF")

    if (ordering == 1): eprint("Node Ordering is ON")
    else: eprint("Node Ordering is OFF")

    if (limit == -1): eprint("Depth Limit is OFF")
    else: eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True: # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL": # Game is over.
            print
        else:
            board = eval(input()) # Read in the input and turn it into a Python
                                  # object. The format is a list of rows. The
                                  # squares in each row are represented by
                                  # 0 : empty square
                                  # 1 : dark disk (player 1)
                                  # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1): #run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else: #else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)
            
            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_ai()


# def alphabeta_max_node_OG(board, color, alpha, beta, limit, caching = 0, ordering = 0):        
#     opponent = 1 if color == 2 else 2
#     best_move = None
#     max_util = -math.inf
#     moves = get_possible_moves(board, color)
    
#     if not moves or limit == 0:
#         return (None, compute_utility(board,color))

#     for move in moves:
#         board_after_play = play_move(board, color, move[0], move[1])
        
#         if caching and board_after_play in cache:
#             result = cache[board_after_play]
#         else:
#             result = alphabeta_min_node(board_after_play, color, alpha, beta, limit - 1, caching, ordering)
#             if caching: cache[board_after_play] = result
        
#         if result[1] > max_util:
#             best_move = move
#             max_util = result[1]
            
#         if max_util >= beta: 
#             return (best_move, max_util)
        
#         alpha = max(alpha, max_util)
        
#     return (best_move, max_util)