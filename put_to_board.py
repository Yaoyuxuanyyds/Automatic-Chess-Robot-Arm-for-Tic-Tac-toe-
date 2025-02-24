from detect import detect
from control import move_to_pixel, reset_arm
from end_control import put_piece, get_piece, safe_position
import time
from pyb import UART

# 初始化UART
uart = UART(3, 115200)

checkerboard_position = []

def send_board_state(board):
    uart.write('S') # 提取通知发送
    for row in board:
        for cell in row:
            value = char_to_value(cell)
            uart.writechar(value & 0xFF)  # 发送低字节
            uart.writechar((value >> 8) & 0xFF)  # 发送高字节

def char_to_value(c):
    if c == 'X':
        return 1
    elif c == 'O':
        return 2
    else:
        return 0


def choose_piece(color, out_circles):
    # 从out_circles中取出指定颜色对应的点坐标
    for circle in out_circles:
        if circle[3] == color:
            return circle[0], circle[1]
    return None

def if_equal(last_board_state, current_board_state):
    if_eq = True
    for i in range(3):
        for j in range(3):
            if last_board_state[i][j] != current_board_state[i][j]:
                if_eq = False
                return if_eq
    return if_eq





# 用于手动对局程序调用的放置函数
# 完成从棋盘外取指定颜色棋子放入棋盘指定网格位置的操作
def put_to_board_main():
    global checkerboard_position
    while True:
        # 接收uart数据并解码,放置目标网格序号，棋子颜色
        uart.write('C')
        # print("Waiting for choosing color...")
        while True:
            if uart.any():
                data = uart.read().decode('utf-8').strip()
                if data:
                    if data == '*':
                        color = 'X'
                    elif data == '#':
                        color = 'O'
                    elif data == '0':
                        uart.write('O')
                        # print("Putting program is over!")
                        return
                    # print(f"{color} has been chosen!")
                    break
        # 等待网格编号输入
        uart.write('T')
        # print("Waiting for choosing grid...")
        while True:
            if uart.any():
                data = uart.read().decode('utf-8').strip()
                if data:
                    target_grid = int(data) - 1
                    if target_grid >= 0 and target_grid <= 8:
                        print(f"Target: {target_grid + 1}")
                        break
                    else:
                        target_grid = -1


        # 检测棋盘状态
        # print("Waiting for detection...")
        current_board_state, out_circles, checkerboard_position = detect()
        # print("Detection completed!")

        # 发送当前棋盘状态
        send_board_state(current_board_state)

        # 取出棋盘外的一个指定颜色棋子（先从out_circles中取一个颜色对应的点坐标，控制移动到像素坐标，使用终端舵机取棋子）
        piece_position_x, piece_position_y = choose_piece(color, out_circles)
        grid_position = checkerboard_position[target_grid]

        # print("Puting piece...")

        safe_position()
        move_to_pixel(piece_position_x, piece_position_y) # 控制终端移动到指定像素坐标
        get_piece() # 使用终端舵机取棋子
        # 移动到目标网格位置（根据目标网格序号，控制终端移动到指定像素坐标，使用终端舵机放置棋子）
        time.sleep(0.3)
        move_to_pixel(grid_position[0],grid_position[1])
        put_piece() # 使用终端舵机放置棋子

        uart.write('K')

        reset_arm()

        # print("Puting completed!")

        # 更新棋盘状态
        current_board_state[target_grid // 3][target_grid % 3] = color

        # 发送当前棋盘状态
        send_board_state(current_board_state)





# 用于对局程序调用的放置函数
def put_to_board(color, target_grid):
    global checkerboard_position

    # 检测棋盘状态
    # print("Waiting for detection...")
    current_board_state, out_circles, checkerboard_position = detect()
    # print("Detection completed!")


    # 取出棋盘外的一个指定颜色棋子（先从out_circles中取一个颜色对应的点坐标，控制移动到像素坐标，使用终端舵机取棋子）
    piece_position_x, piece_position_y = choose_piece(color, out_circles)
    grid_position = checkerboard_position[target_grid]

    # print("Puting piece...")

    safe_position()
    move_to_pixel(piece_position_x, piece_position_y) # 控制终端移动到指定像素坐标
    get_piece() # 使用终端舵机取棋子
    # 移动到目标网格位置（根据目标网格序号，控制终端移动到指定像素坐标，使用终端舵机放置棋子）
    time.sleep(0.3)
    move_to_pixel(grid_position[0],grid_position[1])
    put_piece() # 使用终端舵机放置棋子

    uart.write('K')
    reset_arm()
    # print("Puting completed!")

    # 更新棋盘状态
    current_board_state[target_grid // 3][target_grid % 3] = color

    # 发送当前棋盘状态
    send_board_state(current_board_state)

    return current_board_state




# 检测棋盘状态是否一致
def detect_invalid_move(last_board_state, current_board_state):
# 输入前后两次棋盘状态，识别出有哪个棋子被移动，返回棋子移动的目的网格和原先的位置网格序号
    move = [-1,-1]
    for i in range(3):
        for j in range(3):
            if last_board_state[i][j] != current_board_state[i][j] and last_board_state[i][j] == ' ':
                move[0] = i*3 + j # 移动的棋子目的网格序号
            elif last_board_state[i][j] != current_board_state[i][j] and current_board_state[i][j] == ' ':
                move[1] = i*3 + j # 移动的棋子原先的位置网格序号
    return move



# 恢复棋盘状态
def recover_board_state(last_board_state, current_board_state):
    global checkerboard_position
    # print("Recovering board state...")
    move = detect_invalid_move(last_board_state, current_board_state)
    if move[0] or move[1]:
        safe_position()
        move_to_pixel(checkerboard_position[move[0]][0],checkerboard_position[move[0]][1])
        get_piece()
        move_to_pixel(checkerboard_position[move[1]][0],checkerboard_position[move[1]][1])
        put_piece()
        reset_arm()
    # print("Recovering completed!")
    return last_board_state


def detect_human_move(last_board_state):
    global checkerboard_position
    # 检测
    current_board_state, out_circles, checkerboard_position = detect()
    # 判断是否有增加棋子
    if_consistent = True
    cnt_current = 0
    cnt_last = 0
    for i in range(3):
        for j in range(3):
            if current_board_state[i][j] != ' ':
                cnt_current += 1
    for i in range(3):
        for j in range(3):
            if last_board_state[i][j] != ' ':
                cnt_last += 1
    if cnt_current <= cnt_last:
        if_consistent = False

    # 恢复被移动棋子
    if not if_consistent:
        # print("Board state is inconsistent!")
        uart.write('R')
        current_board_state = recover_board_state(last_board_state, current_board_state)
        return if_consistent, current_board_state, -1

    if if_consistent:
        for i in range(3):
            for j in range(3):
                if current_board_state[i][j] != last_board_state[i][j]:
                    move = i*3+j
                    return if_consistent, current_board_state, move


if __name__ == "__main__":
    put_to_board_main()

