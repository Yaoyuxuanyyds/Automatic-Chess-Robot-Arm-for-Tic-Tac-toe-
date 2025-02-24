
class Board:
    NONE = ' '
    HUMAN = 'X'
    COMPUTER = 'O'

    def __init__(self, first_player):
        self.board = [[self.NONE for _ in range(3)] for _ in range(3)]
        self.turn = first_player
        self.time = 0

    def display(self):
        for i in range(3):
            row = ""
            for j in range(3):
                if self.board[i][j] == self.NONE:
                    row += f" {i * 3 + j + 1} "
                else:
                    row += f" {self.board[i][j]} "
                if j < 2:
                    row += "|"
            print(row)
            if i < 2:
                print("---+---+---")
        print()

    def is_blank(self, i, j):
        return self.board[i][j] == self.NONE

    def move(self, i, j):
        if self.is_blank(i, j):
            self.board[i][j] = self.turn
            self.turn = self.HUMAN if self.turn == self.COMPUTER else self.COMPUTER
            self.time += 1
            return True
        return False

    def evaluate(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != self.NONE:
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != self.NONE:
                return self.board[0][i]

        if self.board[0][0] == self.board[1][1] == self.board[2][2] != self.NONE:
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != self.NONE:
            return self.board[0][2]

        if self.time == 9:
            return 'D'
        return None

    def minimax(self, depth, is_maximizing):
        winner = self.evaluate()
        if winner == self.COMPUTER:
            return 10 - depth
        elif winner == self.HUMAN:
            return depth - 10
        elif winner == 'D':
            return 0

        if is_maximizing:
            best = -1000
            for i in range(3):
                for j in range(3):
                    if self.is_blank(i, j):
                        self.board[i][j] = self.COMPUTER
                        self.time += 1
                        best = max(best, self.minimax(depth + 1, False))
                        self.board[i][j] = self.NONE
                        self.time -= 1
            return best
        else:
            best = 1000
            for i in range(3):
                for j in range(3):
                    if self.is_blank(i, j):
                        self.board[i][j] = self.HUMAN
                        self.time += 1
                        best = min(best, self.minimax(depth + 1, True))
                        self.board[i][j] = self.NONE
                        self.time -= 1
            return best

    def best_move(self):
        best_val = -1000
        move = (-1, -1)
        for i in range(3):
            for j in range(3):
                if self.is_blank(i, j):
                    self.board[i][j] = self.COMPUTER
                    self.time += 1
                    move_val = self.minimax(0, False)
                    self.board[i][j] = self.NONE
                    self.time -= 1
                    if move_val > best_val:
                        move = (i, j)
                        best_val = move_val
        return move



