import math


class KalahaAI:
    def __init__(self, depth):
        self.depth = depth

    def chooseMove(self, state):
        if state.CurrentPlayerIs0 != state.ComputerIs0:
            raise ValueError("AI can only move for computer")

        best_score = -math.inf
        best_move = None
        alpha = -math.inf
        beta = math.inf

        for move in state.get_legal_moves():
            new_state = state.clone()
            extra_turn = new_state.makeMove(move, print_board=False)
            next_depth = self.depth if extra_turn else self.depth - 1

            score = self.minimax(new_state, next_depth, alpha, beta)

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, best_score)

        return best_move

    def minimax(self, state, depth, alpha, beta):
        if state.endGame:
            return state.game_result() * 1000

        if depth <= 0:
            return self.evaluate(state)

        maximizing = (state.CurrentPlayerIs0 == state.ComputerIs0)

        if maximizing:
            value = -math.inf
            for move in state.get_legal_moves():
                child = state.clone()
                extra_turn = child.makeMove(move, print_board=False)
                next_depth = depth if extra_turn else depth - 1

                value = max(value, self.minimax(child, next_depth, alpha, beta))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = math.inf
            for move in state.get_legal_moves():
                child = state.clone()
                extra_turn = child.makeMove(move, print_board=False)
                next_depth = depth if extra_turn else depth - 1

                value = min(value, self.minimax(child, next_depth, alpha, beta))
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

    def evaluate(self, state):
        board = state.board

        if state.ComputerIs0:
            computer_pits = list(range(state.Player0Start, state.Player0End))
            computer_store = state.Player0End
            human_pits = list(range(state.Player1Start, state.Player1End))
            human_store = state.Player1End
        else:
            computer_pits = list(range(state.Player1Start, state.Player1End))
            computer_store = state.Player1End
            human_pits = list(range(state.Player0Start, state.Player0End))
            human_store = state.Player0End

        computer_store_advantage = board[computer_store] - board[human_store]
        computer_side_stones = sum(board[p] for p in computer_pits)
        human_side_stones = sum(board[p] for p in human_pits)
        side_advantage = computer_side_stones - human_side_stones

        extra_turn_chances = 0
        for pit in computer_pits:
            stones = board[pit]
            if stones <= 0:
                continue

            landing = pit
            s = stones
            while s > 0:
                landing = (landing + 1) % (state.Npits * 2 + 2)
                if landing == human_store:
                    continue
                s -= 1

            if landing == computer_store:
                extra_turn_chances += 1

        capture_chances = 0
        for pit in computer_pits:
            stones = board[pit]
            if stones <= 0:
                continue

            landing = pit
            s = stones
            while s > 0:
                landing = (landing + 1) % (state.Npits * 2 + 2)
                if landing == human_store:
                    continue
                s -= 1

            if landing in computer_pits and board[landing] == 0:
                opposite = (state.Npits * 2) - landing
                if 0 <= opposite < len(board) and board[opposite] > 0:
                    capture_chances += board[opposite]

        return (
            12 * computer_store_advantage
            + 2 * side_advantage
            + 8 * extra_turn_chances
            + 3 * capture_chances
        )