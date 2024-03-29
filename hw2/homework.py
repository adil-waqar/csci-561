import copy
from time import process_time


class Pente:
    BOARD_SIZE = 19
    WHITE = 'w'
    BLACK = 'b'

    def __init__(self, board, color, seconds_left, w_cap, b_cap, move_num):
        self.board = board
        self.color = color
        self.seconds_left = seconds_left
        self.w_cap = w_cap
        self.b_cap = b_cap
        self.move_num = move_num
        self.board_history = []
        self.move_history = []
        self.capture_history = []
        self.ci = Pente.WHITE if self.color == "WHITE" else Pente.BLACK
        self.oci = Pente.BLACK if self.color == "WHITE" else Pente.WHITE
        self.winner: str

    def check_game_end(self):
        if self.check_row_win_for(Pente.WHITE):
            self.winner = Pente.WHITE
            return True
        if self.check_row_win_for(Pente.BLACK):
            self.winner = Pente.BLACK
            return True
        if self.check_capture_win_for(Pente.BLACK):
            self.winner = Pente.BLACK
            return True
        if self.check_capture_win_for(Pente.WHITE):
            self.winner = Pente.WHITE
            return True
        return False

    def check_row_win_for(self, ci):
        # horizontal
        for y in range(Pente.BOARD_SIZE):
            for x in range(Pente.BOARD_SIZE - 4):
                if self.board[x][y] == ci \
                        and self.board[x+1][y] == ci \
                        and self.board[x+2][y] == ci \
                        and self.board[x+3][y] == ci \
                        and self.board[x+4][y] == ci:
                    return True
        # vertical
        for x in range(Pente.BOARD_SIZE):
            for y in range(Pente.BOARD_SIZE - 4):
                if self.board[x][y] == ci \
                        and self.board[x][y+1] == ci \
                        and self.board[x][y+2] == ci \
                        and self.board[x][y+3] == ci \
                        and self.board[x][y+4] == ci:
                    return True

        # diagonal
        for x in range(Pente.BOARD_SIZE - 4):
            for y in range(4, Pente.BOARD_SIZE):
                if self.board[x][y] == ci \
                        and self.board[x+1][y-1] == ci \
                        and self.board[x+2][y-2] == ci \
                        and self.board[x+3][y-3] == ci \
                        and self.board[x+4][y-4] == ci:
                    return True

        # other diagonal
        for x in range(Pente.BOARD_SIZE - 4):
            for y in range(Pente.BOARD_SIZE - 4):
                if self.board[x][y] == ci \
                        and self.board[x+1][y+1] == ci \
                        and self.board[x+2][y+2] == ci \
                        and self.board[x+3][y+3] == ci \
                        and self.board[x+4][y+4] == ci:
                    return True
        return False

    def check_capture_win_for(self, color):
        if color == Pente.WHITE:
            return self.w_cap >= 10
        else:
            return self.b_cap >= 10

    def get_valid_moves(self):
        if self.ci == Pente.WHITE:
            if self.move_num == 1:
                return [(9, 9)]
            elif self.move_num == 2:
                intersections = self.get_empty_intersections()
                # remove within 3 intersections coords
                intersections = filter(
                    lambda coord: not (
                        coord[0] >= 7 and
                        coord[0] <= 11 and
                        coord[1] >= 7 and
                        coord[1] <= 11),
                    intersections)
                return intersections

        return self.get_empty_intersections()

    def make_move(self, move):
        self.board_history.append(copy.deepcopy(self.board))
        self.capture_history.append((self.w_cap, self.b_cap))
        self.move_history.append(move)

        self.board[move[0]][move[1]] = self.ci
        self.check_for_capture(move)

        self.move_num += 1
        self.ci, self.oci = self.oci, self.ci

    def unmake_move(self):
        if self.move_history.pop():
            self.board = self.board_history.pop()
            self.move_num -= 1
            capture_history = self.capture_history.pop()
            self.w_cap = capture_history[0]
            self.b_cap = capture_history[1]
            self.ci, self.oci = self.oci, self.ci

    def check_for_capture(self, move):
        x, y = move
        # horizontal
        if y > 2 and \
                self.board[x][y-1] == self.oci \
                and self.board[x][y-2] == self.oci \
                and self.board[x][y-3] == self.ci:
            self.board[x][y-1] = '.'
            self.board[x][y-2] = '.'
            if self.ci == Pente.WHITE:
                self.w_cap += 2
            else:
                self.b_cap += 2

        if y < Pente.BOARD_SIZE - 3 and \
                self.board[x][y+1] == self.oci \
                and self.board[x][y+2] == self.oci \
                and self.board[x][y+3] == self.ci:
            self.board[x][y+1] = '.'
            self.board[x][y+2] = '.'

            if self.ci == Pente.WHITE:
                self.w_cap += 2
            else:
                self.b_cap += 2

        # vertical
        if x > 2 and \
                self.board[x-1][y] == self.oci \
                and self.board[x-2][y] == self.oci \
                and self.board[x-3][y] == self.ci:
            self.board[x-1][y] = '.'
            self.board[x-2][y] = '.'

            if self.ci == Pente.WHITE:
                self.w_cap += 2
            else:
                self.b_cap += 2

        if x < Pente.BOARD_SIZE - 3 and \
                self.board[x+1][y] == self.oci \
                and self.board[x+2][y] == self.oci \
                and self.board[x+3][y] == self.ci:
            self.board[x+1][y] = '.'
            self.board[x+2][y] = '.'

            if self.ci == Pente.WHITE:
                self.w_cap += 2
            else:
                self.b_cap += 2

        # check diagonal captures
        if (x > 2 and y > 2 and
                self.board[x-1][y-1] == self.oci and
                self.board[x-2][y-2] == self.oci and
                self.board[x-3][y-3] == self.ci):
            self.board[x-1][y-1] = '.'
            self.board[x-2][y-2] = '.'

            if self.ci == Pente.WHITE:
                self.w_cap += 2
            else:
                self.b_cap += 2

        if (x < Pente.BOARD_SIZE - 3 and y < Pente.BOARD_SIZE - 3 and
                self.board[x+1][y+1] == self.oci and
                self.board[x+2][y+2] == self.oci and
                self.board[x+3][y+3] == self.ci):
            self.board[x+1][y+1] = '.'
            self.board[x+2][y+2] = '.'

            if self.ci == Pente.WHITE:
                self.w_cap += 2
            else:
                self.b_cap += 2

        # check other diagonal captures
        if (x > 2 and y < Pente.BOARD_SIZE - 3 and
                self.board[x-1][y+1] == self.oci and
                self.board[x-2][y+2] == self.oci and
                self.board[x-3][y+3] == self.ci):
            self.board[x-1][y+1] = '.'
            self.board[x-2][y+2] = '.'

            if self.ci == Pente.WHITE:
                self.w_cap += 2
            else:
                self.b_cap += 2

        if (x < Pente.BOARD_SIZE - 3 and y < Pente.BOARD_SIZE - 3 and
                self.board[x+1][y-1] == self.oci and
                self.board[x+2][y-2] == self.oci and
                self.board[x+3][y-3] == self.ci):
            self.board[x+1][y-1] = '.'
            self.board[x+2][y-2] = '.'

            if self.ci == Pente.WHITE:
                self.w_cap += 2
            else:
                self.b_cap += 2
            return True

    def get_empty_intersections(self):
        empty_intersection = []
        for x in range(Pente.BOARD_SIZE):
            for y in range(Pente.BOARD_SIZE):
                if self.board[x][y] == ".":
                    empty_intersection.append((x, y))
        return empty_intersection


class Player:
    SEARCH_DEPTH = 1
    PENTE_COL_LOOKUP = {
        0: 'A',
        1: 'B',
        2: 'C',
        3: 'D',
        4: 'E',
        5: 'F',
        6: 'G',
        7: 'H',
        8: 'J',
        9: 'K',
        10: 'L',
        11: 'M',
        12: 'N',
        13: 'O',
        14: 'P',
        15: 'Q',
        16: 'R',
        17: 'S',
        18: 'T'
    }

    def __init__(self):
        self.board: Pente
        self.ci: str
        self.best_move: str = None

    def read_input(self):
        with open("input.txt", "r") as f:
            file = f.read().splitlines()

        color = file[0]
        seconds_left = float(file[1])
        w_cap, b_cap = file[2].split(',')
        w_cap = int(w_cap)
        b_cap = int(b_cap)
        board = []
        for i in range(3, 22):
            board.append([intersection for intersection in file[i]])

        self.board = Pente(board=board, color=color,
                           seconds_left=seconds_left, w_cap=w_cap, b_cap=b_cap, move_num=0)
        self.ci = Pente.WHITE if self.board.color == "WHITE" else Pente.BLACK
        self.oci = Pente.BLACK if self.board.color == "WHITE" else Pente.WHITE
        self.board.move_num = self.calc_move_num()
        self.ci_cap = self.board.w_cap if self.ci == Pente.WHITE else self.board.b_cap
        self.oci_cap = self.board.w_cap if self.oci == Pente.WHITE else self.board.w_cap

    def write_output(self):
        with open("output.txt", "w") as f:
            f.write(self.best_move)

    def calc_move_num(self):
        move_num = 1
        for x in range(Pente.BOARD_SIZE):
            for y in range(Pente.BOARD_SIZE):
                if self.board.board[x][y] == self.ci:
                    move_num += 1
        return move_num

    def compute_move(self):
        coord = self.alpha_beta_search(Player.SEARCH_DEPTH)
        if coord:
            self.best_move = self.coord_to_pent(coord)

    def coord_to_pent(self, coord):
        row = str(Pente.BOARD_SIZE - coord[0])
        col = Player.PENTE_COL_LOOKUP[coord[1]]
        return row + col

    def alpha_beta_search(self, depth: int):
        _, best_move = self.alpha_beta_max(float("-inf"), float("inf"), depth)
        return best_move

    def alpha_beta_max(self, alpha, beta, depth):
        if self.board.check_game_end():
            return (float("inf"), None) if self.board.winner == self.ci else (float("-inf"), None)
        if not depth:
            return (self.eval(), self.board.move_history[-1])

        best_move = None
        best_value = float("-inf")

        for move in self.board.get_valid_moves():
            self.board.make_move(move)
            value, _ = self.alpha_beta_min(alpha, beta, depth - 1)
            self.board.unmake_move()

            if value > best_value:
                best_value = value
                best_move = move

            if value >= beta:
                return value, best_move

            alpha = max(alpha, value)

        return best_value, best_move

    def alpha_beta_min(self, alpha, beta, depth):
        if self.board.check_game_end():
            return (float("inf"), None) if self.board.winner == self.ci else (float("-inf"), None)
        if not depth:
            return (self.eval(), self.board.move_history[-1])

        best_move = None
        best_value = float("inf")

        for move in self.board.get_valid_moves():
            self.board.make_move(move)
            value, _ = self.alpha_beta_max(alpha, beta, depth - 1)
            self.board.unmake_move()

            if value < best_value:
                best_value = value
                best_move = move

            if value <= alpha:
                return value, best_move

            beta = min(beta, value)

        return best_value, best_move

    # check for x-pieces in a row
    def heuristic1(self):
        max = 0
        for i in range(Pente.BOARD_SIZE):
            for j in range(Pente.BOARD_SIZE):
                # skip occupied intersections
                if self.board.board[i][j] != '.':
                    continue
                # check for bounds
                # diagonal /
                count = 0
                # upper diagonal
                if ((i-4) > -1 and (i-4) < Pente.BOARD_SIZE) and ((j+4) > -1 and (j+4) < Pente.BOARD_SIZE):
                    for k in range(1, 5):
                        if self.board.board[i-k][j+k] == self.oci:
                            break
                        if self.board.board[i-k][j+k] == self.ci:
                            count += 1
                # lower diagonal
                if ((i+4) > -1 and (i+4) < Pente.BOARD_SIZE) and ((j-4) > -1 and (j-4) < Pente.BOARD_SIZE):
                    for k in range(1, 5):
                        if self.board.board[i+k][j-k] == self.oci:
                            break
                        if self.board.board[i+k][j-k] == self.ci:
                            count += 1
                if count > max:
                    max = count

                # diagonal \
                count = 0
                # upper diagonal
                if ((i-4) > -1 and (i-4) < Pente.BOARD_SIZE) and ((j-4) > -1 and (j-4) < Pente.BOARD_SIZE):
                    for k in range(1, 5):
                        if self.board.board[i-k][j-k] == self.oci:
                            break
                        if self.board.board[i-k][j-k] == self.ci:
                            count += 1
                # lower diagonal
                if ((i+4) > -1 and (i+4) < Pente.BOARD_SIZE) and ((j+4) > -1 and (j+4) < Pente.BOARD_SIZE):
                    for k in range(1, 5):
                        if self.board.board[i+k][j+k] == self.oci:
                            break
                        if self.board.board[i+k][j+k] == self.ci:
                            count += 1
                if count > max:
                    max = count

                # vertical |
                count = 0
                # upper
                if i-4 > -1:
                    for k in range(1, 5):
                        if self.board.board[i-k][j] == self.oci:
                            break
                        if self.board.board[i-k][j] == self.ci:
                            count += 1
                # lower
                if i+4 < Pente.BOARD_SIZE:
                    for k in range(1, 5):
                        if self.board.board[i+k][j] == self.oci:
                            break
                        if self.board.board[i+k][j] == self.ci:
                            count += 1
                if count > max:
                    max = count

                # horizontal
                count = 0
                # right
                if j+4 < Pente.BOARD_SIZE:
                    for k in range(1, 5):
                        if self.board.board[i][j+k] == self.oci:
                            break
                        if self.board.board[i][j+k] == self.ci:
                            count += 1
                # left
                if j-4 > -1:
                    for k in range(1, 5):
                        if self.board.board[i][j-k] == self.oci:
                            break
                        if self.board.board[i][j-k] == self.ci:
                            count += 1
                if count > max:
                    max = count
        return max

    # block enemy capture
    def heuristic2(self):
        ec_count = 0
        for x in range(Pente.BOARD_SIZE):
            for y in range(Pente.BOARD_SIZE):
                if y > 2 and \
                        self.board.board[x][y] == '.' and \
                        self.board.board[x][y-1] == self.ci \
                        and self.board.board[x][y-2] == self.ci \
                        and self.board.board[x][y-3] == self.oci:
                    ec_count += 2

                if y < Pente.BOARD_SIZE - 3 and \
                        self.board.board[x][y] == '.' and \
                        self.board.board[x][y+1] == self.ci \
                        and self.board.board[x][y+2] == self.ci \
                        and self.board.board[x][y+3] == self.oci:
                    ec_count += 2

                # vertical
                if x > 2 and \
                        self.board.board[x][y] == '.' and \
                        self.board.board[x-1][y] == self.ci \
                        and self.board.board[x-2][y] == self.ci \
                        and self.board.board[x-3][y] == self.oci:
                    ec_count += 2

                if x < Pente.BOARD_SIZE - 3 and \
                        self.board.board[x][y] == '.' and \
                        self.board.board[x+1][y] == self.ci \
                        and self.board.board[x+2][y] == self.ci \
                        and self.board.board[x+3][y] == self.oci:
                    ec_count += 2

                # check diagonal captures
                if (x > 2 and y > 2 and
                        self.board.board[x][y] == '.' and
                        self.board.board[x-1][y-1] == self.ci and
                        self.board.board[x-2][y-2] == self.ci and
                        self.board.board[x-3][y-3] == self.oci):
                    ec_count += 2

                if (x < Pente.BOARD_SIZE - 3 and y < Pente.BOARD_SIZE - 3 and
                        self.board.board[x][y] == '.' and
                        self.board.board[x+1][y+1] == self.ci and
                        self.board.board[x+2][y+2] == self.ci and
                        self.board.board[x+3][y+3] == self.oci):
                    ec_count += 2

                # check other diagonal captures
                if (x > 2 and y < Pente.BOARD_SIZE - 3 and
                        self.board.board[x][y] == '.' and
                        self.board.board[x-1][y+1] == self.ci and
                        self.board.board[x-2][y+2] == self.ci and
                        self.board.board[x-3][y+3] == self.oci):
                    ec_count += 2

                if (x < Pente.BOARD_SIZE - 3 and y < Pente.BOARD_SIZE - 3 and
                        self.board.board[x][y] == '.' and
                        self.board.board[x+1][y-1] == self.ci and
                        self.board.board[x+2][y-2] == self.ci and
                        self.board.board[x+3][y-3] == self.oci):
                    ec_count += 2

        return ec_count

    # check for opponent getting x in a row
    def heuristic3(self):
        max = 0
        for i in range(Pente.BOARD_SIZE):
            for j in range(Pente.BOARD_SIZE):
                # skip occupied intersections
                if self.board.board[i][j] != '.':
                    continue
                # check for bounds
                # diagonal /
                count = 0
                # upper diagonal
                if ((i-4) > -1 and (i-4) < Pente.BOARD_SIZE) and ((j+4) > -1 and (j+4) < Pente.BOARD_SIZE):
                    for k in range(1, 5):
                        if self.board.board[i-k][j+k] == self.ci:
                            break
                        if self.board.board[i-k][j+k] == self.oci:
                            count += 1
                # lower diagonal
                if ((i+4) > -1 and (i+4) < Pente.BOARD_SIZE) and ((j-4) > -1 and (j-4) < Pente.BOARD_SIZE):
                    for k in range(1, 5):
                        if self.board.board[i+k][j-k] == self.ci:
                            break
                        if self.board.board[i+k][j-k] == self.oci:
                            count += 1
                if count > max:
                    max = count

                # diagonal \
                count = 0
                # upper diagonal
                if ((i-4) > -1 and (i-4) < Pente.BOARD_SIZE) and ((j-4) > -1 and (j-4) < Pente.BOARD_SIZE):
                    for k in range(1, 5):
                        if self.board.board[i-k][j-k] == self.ci:
                            break
                        if self.board.board[i-k][j-k] == self.oci:
                            count += 1
                # lower diagonal
                if ((i+4) > -1 and (i+4) < Pente.BOARD_SIZE) and ((j+4) > -1 and (j+4) < Pente.BOARD_SIZE):
                    for k in range(1, 5):
                        if self.board.board[i+k][j+k] == self.ci:
                            break
                        if self.board.board[i+k][j+k] == self.oci:
                            count += 1
                if count > max:
                    max = count

                # vertical |
                count = 0
                # upper
                if i-4 > -1:
                    for k in range(1, 5):
                        if self.board.board[i-k][j] == self.ci:
                            break
                        if self.board.board[i-k][j] == self.oci:
                            count += 1
                # lower
                if i+4 < Pente.BOARD_SIZE:
                    for k in range(1, 5):
                        if self.board.board[i+k][j] == self.ci:
                            break
                        if self.board.board[i+k][j] == self.oci:
                            count += 1
                if count > max:
                    max = count

                # horizontal
                count = 0
                # rightc
                if j+4 < Pente.BOARD_SIZE:
                    for k in range(1, 5):
                        if self.board.board[i][j+k] == self.ci:
                            break
                        if self.board.board[i][j+k] == self.oci:
                            count += 1
                # left
                if j-4 > -1:
                    for k in range(1, 5):
                        if self.board.board[i][j-k] == self.ci:
                            break
                        if self.board.board[i][j-k] == self.oci:
                            count += 1
                if count > max:
                    max = count

        return max

    # encourage own capture
    def heuristic4(self):
        c_count = 0
        for x in range(Pente.BOARD_SIZE):
            for y in range(Pente.BOARD_SIZE):
                if y > 2 and \
                        self.board.board[x][y] == '.' and \
                        self.board.board[x][y-1] == self.oci \
                        and self.board.board[x][y-2] == self.oci \
                        and self.board.board[x][y-3] == self.ci:
                    c_count += 2

                if y < Pente.BOARD_SIZE - 3 and \
                        self.board.board[x][y] == '.' and \
                        self.board.board[x][y+1] == self.oci \
                        and self.board.board[x][y+2] == self.oci \
                        and self.board.board[x][y+3] == self.ci:
                    c_count += 2

                # vertical
                if x > 2 and \
                        self.board.board[x][y] == '.' and \
                        self.board.board[x-1][y] == self.oci \
                        and self.board.board[x-2][y] == self.oci \
                        and self.board.board[x-3][y] == self.ci:
                    c_count += 2

                if x < Pente.BOARD_SIZE - 3 and \
                        self.board.board[x][y] == '.' and \
                        self.board.board[x+1][y] == self.oci \
                        and self.board.board[x+2][y] == self.oci \
                        and self.board.board[x+3][y] == self.ci:
                    c_count += 2

                # check diagonal captures
                if (x > 2 and y > 2 and
                        self.board.board[x][y] == '.' and
                        self.board.board[x-1][y-1] == self.oci and
                        self.board.board[x-2][y-2] == self.oci and
                        self.board.board[x-3][y-3] == self.ci):
                    c_count += 2

                if (x < Pente.BOARD_SIZE - 3 and y < Pente.BOARD_SIZE - 3 and
                        self.board.board[x][y] == '.' and
                        self.board.board[x+1][y+1] == self.oci and
                        self.board.board[x+2][y+2] == self.oci and
                        self.board.board[x+3][y+3] == self.ci):
                    c_count += 2

                # check other diagonal captures
                if (x > 2 and y < Pente.BOARD_SIZE - 3 and
                        self.board.board[x][y] == '.' and
                        self.board.board[x-1][y+1] == self.oci and
                        self.board.board[x-2][y+2] == self.oci and
                        self.board.board[x-3][y+3] == self.ci):
                    c_count += 2

                if (x < Pente.BOARD_SIZE - 3 and y < Pente.BOARD_SIZE - 3 and
                        self.board.board[x][y] == '.' and
                        self.board.board[x+1][y-1] == self.oci and
                        self.board.board[x+2][y-2] == self.oci and
                        self.board.board[x+3][y-3] == self.ci):
                    c_count += 2

        return c_count

    # check for own cap pt2
    def heuristic5(self):
        return self.ci_cap

    def heuristic6(self):
        return self.oci_cap

    def eval(self):
        heu1 = float(self.heuristic1())
        heu2 = float(self.heuristic5())
        heu3 = float(self.heuristic2())
        heu4 = float(self.heuristic3())

        return (heu1 + heu2) - (1.2 * heu3) - (1.2 * heu4)


if __name__ == "__main__":
    player = Player()
    player.read_input()
    t1_start = process_time()
    player.compute_move()
    t1_stop = process_time()
    print("time: ", round(t1_stop - t1_start))
    if player.best_move:
        player.write_output()
        print(player.best_move)
