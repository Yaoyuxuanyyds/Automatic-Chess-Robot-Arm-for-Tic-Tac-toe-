import time
from pyb import Servo

# 创建Servo对象
servo = Servo(1)

def set_servo_angle(angle):
    """设置舵机的角度"""
#    servo.degrees(angle)
    servo.angle(angle)

P1 = -50
P2 = 50
P3 = 90

def safe_position():
    set_servo_angle(P2)

def get_piece():
    global P1, P2
    set_servo_angle(P1)
    time.sleep(0.5)
    set_servo_angle(P2)

def put_piece():
    global P1, P2, P3
    set_servo_angle(-90)
    time.sleep(0.5)
    set_servo_angle(P3)
    time.sleep(0.5)
    set_servo_angle(P2)

#get_piece()

put_piece()
#set_servo_angle(-90)
