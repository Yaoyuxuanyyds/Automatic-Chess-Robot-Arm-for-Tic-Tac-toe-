from tic_tac_toe import Board
from put_to_board import put_to_board, recover_board_state, detect_human_move
from detect import detect
from pyb import UART


# 初始化UART
uart = UART(3, 115200)


def game():

    print("Please enter computer first (C) or you first (D): ")
    # 等待人类输入先手选择
    while True:
        if uart.any():
            data = uart.read().decode('utf-8').strip()
            if data == 'C':
                first = 'C'
                Board.COMPUTER = 'X'
                Board.HUMAN = 'O'
                print('Computer first')
                break
            elif data == 'D':
                first = 'H'
                Board.COMPUTER = 'O'
                Board.HUMAN = 'X'
                print('Human first')
                break
            elif data == '0':
                print('Exit game')
                return

    board = Board(Board.HUMAN if first == 'H' else Board.COMPUTER)
    board.display()
    first_move = 1

    current_board_state = [[' ' for _ in range(3)] for _ in range(3)]
    if_consistent = True

    while True:

        # Human move
        if board.turn == Board.HUMAN:
#            print("Human's turn. Choose your move and enter 0 to ensure.")
            is_over = 0
            while is_over == 0:
                if uart.any():
                    data = uart.read().decode('utf-8').strip()
                    if data == '0':
                        break
                    else:
                        is_over = 0
#            print("Waiting for detection...")
            if_consistent, current_board_state, move = detect_human_move(board.board)

            if not if_consistent:
                board.turn = Board.HUMAN
#                print("Move was recovered, please choose your move again!")
                board.board = current_board_state
            else:
#                print(f"Human choose {move+1}.")
                # 更新棋盘状态
                board.board = current_board_state
                board.turn = Board.COMPUTER
                board.time += 1

                first_move = 0

        # Computer move
        else:
            if first_move:
                target_grid = -1
                while True:
                    if uart.any():
                        data = uart.read().decode('utf-8').strip()
                        if data:
                            target_grid = int(data) - 1
                            if target_grid >= 0 and target_grid <= 8:
                                # print(f"Target: {target_grid + 1}")
                                break
                            else:
                                target_grid = -1
                move = (target_grid // 3, target_grid % 3)
                first_move = 0
            else:
                move = board.best_move()
#            print(f"Computer move to: {move[0] * 3 + move[1] + 1}")
            # 执行放置程序
            current_board_state = put_to_board(board.COMPUTER, move[0] * 3 + move[1])


            # 更新棋盘状态
            board.board = current_board_state
            board.turn = Board.HUMAN
            board.time += 1

            first_move = 0


        board.display()
        result = board.evaluate()
        if result:
            if result == Board.HUMAN:
#                print("Human wins!")
                uart.write('Q')
            elif result == Board.COMPUTER:
#                print("Computer wins!")
                uart.write('W')
            else:
#                print("Draw!")
                uart.write('E')
            break

        # 通知回合结束
#        print("Round end")




if __name__ == "__main__":
    game()
