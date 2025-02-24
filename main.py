from put_to_board import put_to_board_main
from game import game
from pyb import UART

# 初始化UART
uart = UART(3, 115200)

while True:
    over = 0
#    print("Please choose program: A or B ")
    uart.write('M')

    if over:
#        print("Over!")
        break

    # 等待人类输入
    while True:
        if uart.any():
            data = uart.read().decode('utf-8').strip()
            if data == 'A':
#                print("Running program A...")
                put_to_board_main()

                break
            elif data == 'B':
#                print("Running program B...")
                game()

                break
            elif data == '0':
                over = 1
                break

