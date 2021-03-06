"""Finish all TODO items in this file to complete the isolation project, then
test your agent's strength against a set of known agents using tournament.py
and include the results in your report.
"""
import random


class SearchTimeout(Exception):
    """Subclass base exception for code clarity. """
    pass


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    This should be the best heuristic function for your project submission.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    # Calculate the number of moves we can make that can't be reflected by the opposing player
    our_moves = game.get_legal_moves(player)
    opp_moves = game.get_legal_moves(game.get_opponent(player))
    no_reflect_moves = set()
    for move in our_moves:
        # Get the reflection of this current move
        reflect_pt = (game.width - 1 - move[0], game.height - 1 - move[1])
        if reflect_pt not in opp_moves:
            no_reflect_moves.add(move)
    # Over-weigh the number of moves that can't be reflected and compare against the number of opponent moves
    return float(len(no_reflect_moves)**2 - len(opp_moves))


def custom_score_2(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    # Rate the moves closest to the center as better
    # The further you get from the center, the lower the score
    our_moves = game.get_legal_moves(player)
    score = 0.0
    for move in our_moves:
        width_distance = max(0.01, game.width // 2 - move[1])
        height_distance = max(0.01, game.height // 2 - move[0])
        score += 1/width_distance + 1/height_distance

    return score


def custom_score_3(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    # Play to limit the number of moves the opponent can make
    opp_moves = game.get_legal_moves(game.get_opponent(player))
    return float(100/max(0.0001, float(len(opp_moves))))


class IsolationPlayer:
    """Base class for minimax and alphabeta agents -- this class is never
    constructed or tested directly.

    ********************  DO NOT MODIFY THIS CLASS  ********************

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """
    def __init__(self, search_depth=3, score_fn=custom_score, timeout=10.):
        self.search_depth = search_depth
        self.score = score_fn
        self.time_left = None
        self.TIMER_THRESHOLD = timeout - 0.5  # Add some padding so we don't timeout

    def time_check(self):
        """Raise an exception if we're out of time"""
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()


class MinimaxPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using depth-limited minimax
    search. You must finish and test this player to make sure it properly uses
    minimax to return a good move before the search time limit expires.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        **************  YOU DO NOT NEED TO MODIFY THIS FUNCTION  *************

        For fixed-depth search, this function simply wraps the call to the
        minimax method, but this method provides a common interface for all
        Isolation agents, and you will replace it in the AlphaBetaPlayer with
        iterative deepening search.

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left

        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout or there are no moves
        best_move = (-1, -1)

        if self.terminal_test(game):  # player can't move
            return best_move

        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            best_move = self.minimax(game, self.search_depth)

        except SearchTimeout:
            pass  # Handle any actions required after timeout as needed

        # Return the best move from the last completed search iteration
        return best_move

    def terminal_test(self, game):
        """ Return True if the game is over for the active player
        and False otherwise.
        """
        self.time_check()
        return not bool(game.get_legal_moves())

    def min_value(self, game, depth):
        """ Return the value for a win (+inf) if the game is over,
        otherwise return the minimum value over all legal child
        nodes.
        """
        v = float("inf")
        if self.terminal_test(game):
            return v
        if not depth:
            return self.score(game, self)
        for m in game.get_legal_moves():
            v = min(v, self.max_value(game.forecast_move(m), depth-1))
        return v

    def max_value(self, game, depth):
        """ Return the value for a loss (-inf) if the game is over,
        otherwise return the maximum value over all legal child
        nodes.
        """
        v = float("-inf")
        if self.terminal_test(game):
            return v
        if not depth:
            return self.score(game, self)
        for m in game.get_legal_moves():
            v = max(v, self.min_value(game.forecast_move(m), depth-1))
        return v

    def minimax(self, game, depth):
        """Implement depth-limited minimax search algorithm as described in
        the lectures.

        This should be a modified version of MINIMAX-DECISION in the AIMA text.
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Minimax-Decision.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """
        return max(game.get_legal_moves(),
                   key=lambda m: self.min_value(game.forecast_move(m), depth-1))


class AlphaBetaPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using iterative deepening minimax
    search with alpha-beta pruning. You must finish and test this player to
    make sure it returns a good move before the search time limit expires.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        Modify the get_move() method from the MinimaxPlayer class to implement
        iterative deepening search instead of fixed-depth search.

        **********************************************************************
        NOTE: If time_left() < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left

        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        best_move = (-1, -1)
        search_depth = 1

        # If this is the first one or two moves, attempt to take the center square (or something close to it)
        if game.move_count == 0 or game.move_count == 1:
            first_move = (game.width // 2, game.height // 2)
            if first_move in game.get_legal_moves(game.active_player):
                return first_move

        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            while True:
                best_move = self.alphabeta(game, search_depth)
                search_depth += 1
        except SearchTimeout:
            pass  # Handle any actions required after timeout as needed

        # Return the best move from the last completed search iteration
        return best_move

    def min_value(self, game, depth, alpha, beta):
        """ Return the value for a win (+inf) if the game is over,
        otherwise return the minimum value over all legal child
        nodes.
        """
        self.time_check()
        if not depth:
            # Ran out of plies... return the heuristic score of this board
            return self.score(game, self)

        score = float("inf")
        legal_moves = game.get_legal_moves()
        if not legal_moves:  # player can't move
            return score

        for move in game.get_legal_moves():
            score = min(score, self.max_value(game.forecast_move(move), depth-1, alpha, beta))
            if score <= alpha:
                break
            beta = min(beta, score)
        return score

    def max_value(self, game, depth, alpha, beta):
        """ Return the value for a loss (-inf) if the game is over,
        otherwise return the maximum value over all legal child
        nodes.
        """
        self.time_check()
        if not depth:
            # Ran out of plies... return the heuristic score of this board
            return self.score(game, self)

        score = float("-inf")
        legal_moves = game.get_legal_moves()
        if not legal_moves:  # player can't move
            return score

        for move in legal_moves:
            score = max(score, self.min_value(game.forecast_move(move), depth-1, alpha, beta))
            if score >= beta:
                break
            alpha = max(alpha, score)
        return score

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf")):
        """Implement depth-limited minimax search with alpha-beta pruning as
        described in the lectures.

        This should be a modified version of ALPHA-BETA-SEARCH in the AIMA text
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Alpha-Beta-Search.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """
        self.time_check()

        best_score = float("-inf")
        best_move = (-1, -1)
        legal_moves = game.get_legal_moves()
        if not legal_moves:  # player can't move
            return best_move

        for move in legal_moves:
            score = self.min_value(game.forecast_move(move), depth-1, alpha, beta)
            alpha = max(alpha, score)

            if score > best_score:
                best_score = score
                best_move = move

        return best_move
