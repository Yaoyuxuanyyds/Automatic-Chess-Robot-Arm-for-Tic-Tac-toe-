import math, time
from pyb import UART
from uservo import UartServoManager

# 舵机个数
servo_num = 2

# 创建串口对象 使用串口2作为控制对象
# 波特率: 115200
uart = UART(1, baudrate=115200)
# 创建舵机管理器
uservo = UartServoManager(uart, srv_num=servo_num)


def position_filter(x,y):
    if x>200:
        return x, y*1.05
    else:
        return x, y


def pixel_to_real(pixel_x, pixel_y):
    """
    将图片像素坐标转换为实际坐标系坐标。

    input:
    pixel_x -- 图片上的像素 x 坐标
    pixel_y -- 图片上的像素 y 坐标

    output:
    real_x, real_y -- 实际坐标系中的 x 和 y 坐标（厘米）
    """
    # 图片左下角的实际坐标
    bottom_left_real_x, bottom_left_real_y = -14, 5.5
    # 图片上边缘居中的实际坐标
    bottom_center_real = (0, 5.5 + 21)

    # 图片尺寸(pixel)
    image_width = 320
    image_height = 240

    # 计算实际坐标单位
    unit_x = (bottom_center_real[0] - bottom_left_real_x) / (image_width // 2)
    unit_y = (bottom_center_real[1] - bottom_left_real_y) / (image_height)

    # 转换像素坐标到实际坐标
    real_x = bottom_left_real_x + pixel_x * unit_x
    real_y = bottom_left_real_y + (image_height - pixel_y) * unit_y

    return real_x, real_y

def inverse_kinematics(x, y, l1=13, l2=8):
    """
    计算二自由度机械臂的关节角度。

    input:
    x -- 末端执行器目标 x 坐标
    y -- 末端执行器目标 y 坐标
    l1 -- 第一个连杆的长度
    l2 -- 第二个连杆的长度

    output:
    θ1, θ2 -- 两个关节的角度（弧度）
    """
    d = math.sqrt(x**2 + y**2)

    if d > (l1 + l2) or d < abs(l1 - l2):
        raise ValueError("目标点超出机械臂的工作范围")

    cos_theta2 = (x**2 + y**2 - l1**2 - l2**2) / (2 * l1 * l2)
    sin_theta2 = math.sqrt(1 - cos_theta2**2)
    θ2 = math.atan2(sin_theta2, cos_theta2)

    k1 = l1 + l2 * cos_theta2
    k2 = l2 * sin_theta2
    θ1 = math.atan2(y, x) - math.atan2(k2, k1)

    return θ1, θ2

def move_to_pixel(pixel_x, pixel_y):
    """
    根据像素坐标控制机械臂移动到目标位置。

    input:
    pixel_x -- 图片上的像素 x 坐标
    pixel_y -- 图片上的像素 y 坐标
    """
    # 将像素坐标转换为实际坐标
    # 滤波
    pixel_x, pixel_y = position_filter(pixel_x, pixel_y)

    pixel_x = 320-pixel_x
    real_x, real_y = pixel_to_real(pixel_x, pixel_y)

    # 计算关节角度
    θ1, θ2 = inverse_kinematics(real_x, real_y)

    # 转换角度为度数
    θ1_deg = math.degrees(θ1)
    θ2_deg = math.degrees(θ2)

    # 控制舵机移动
    uservo.set_servo_angle(1, θ1_deg, interval=1000)
    uservo.set_servo_angle(0, θ2_deg, interval=1000)
    uservo.wait()



# 将机械臂移动到最初始状态
def reset_arm():
    # 控制舵机移动
    uservo.set_servo_angle(1, 0, interval=1000)
    uservo.set_servo_angle(0, 0, interval=1000)
    uservo.wait()
    return

# if __name__ == "__main__":
#    # 示例像素坐标
#    pixel_x = 188
#    pixel_y = 147
#    # 控制机械臂移动到指定像素位置
#    print(pixel_to_real(pixel_x, pixel_y))
#    move_to_pixel(pixel_x, pixel_y)
#    time.sleep(2)
#    reset_arm()
