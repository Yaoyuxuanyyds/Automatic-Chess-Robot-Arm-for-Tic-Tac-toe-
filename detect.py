import math
from coordinate_processor import CoordinateProcessor
import sensor, time



def euclidean_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

#合并相近的线，保障一条黑线不会被识别为两条
def merge_lines(lines_input, coord_tolerance=30):
    def is_near(line1, line2, tolerance):
        return (abs(line1.x1() - line2.x1()) <= tolerance and
                abs(line1.y1() - line2.y1()) <= tolerance and
                abs(line1.x2() - line2.x2()) <= tolerance and
                abs(line1.y2() - line2.y2()) <= tolerance)

    merged_lines_to_return = []
    for lines in lines_input:
        merged_lines = []
        while lines:
            line = lines.pop(0)
            merged = False
            for i, merged_line in enumerate(merged_lines):
                if is_near(merged_line, line, coord_tolerance):
                    #应在此合并，但合并程序有异常，暂时删除
                    #此处会删除重复的线中的一条
                    merged = True
                    break
            if not merged:
                merged_lines.append(line)
        merged_lines_to_return.append(merged_lines)
    return merged_lines_to_return

#通过线的角度，为线分组，同时抛弃孤立的线。
#角度阈值theta_tolerance，
#元素数量小于min_group_size的组会被抛弃
def filter_lines(lines, draw=True, theta_tolerance=5, min_group_size=3):
    groups = []
    # 计算组内线条的平均角度的函数
    def average_theta(group):
        return sum(line.theta() for line in group) / len(group)
    # 将线条添加到合适的组或创建新组的函数
    def add_to_group(line, groups):
        for group in groups:
            avg_theta = average_theta(group)
            if abs(line.theta() - avg_theta) <= theta_tolerance:
                group.append(line)
                return
        groups.append([line])
    # 根据角度对线条进行分类
    for line in lines:
        add_to_group(line, groups)
    # 过滤掉少于 min_group_size 的组
    valid_groups = [group for group in groups if len(group) >= min_group_size]

    if valid_groups:
        valid_groups = merge_lines(valid_groups) #合并相近的线
        #通过角度，对两组线排序
        valid_groups = sorted(valid_groups, key=lambda group: group[0][7])
        #print(valid_groups)
        if draw :
            #print(valid_groups)
            colors=((255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,255,255),(255,0,255))
            for n in range(len(valid_groups)):
                for line in valid_groups[n]:
                    #print('绘制的线',line)
                    img.draw_line(line[0],line[1],line[2],line[3], color=colors[n], thickness=2)

    return valid_groups


#find_grid_centers函数所用的工具：
#计算两条线的交叉点，
def get_intersection(line1, line2):
    # 提取线条的端点
    x1, y1, x2, y2 = line1[0], line1[1], line1[2], line1[3]
    x3, y3, x4, y4 = line2[0], line2[1], line2[2], line2[3]

    # 计算两条直线的交点
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None  # 平行线无交点

    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

    return (px, py)


#find_grid_centers函数所用的工具：
#输入16个交叉点的坐标，每4各坐标以X轴排序，并返回
def sort_points_by_x(points):
    if len(points) % 4 != 0:
        raise ValueError("points 列表的长度必须是4的倍数")

    sorted_points = []
    for i in range(0, len(points), 4):
        subset = points[i:i + 4]
        sorted_subset = sorted(subset, key=lambda p: p[0])
        sorted_points.extend(sorted_subset)

    return sorted_points

#通过横向和纵向的各4条线，计算9个方格的中心坐标
def find_grid_centers(horizontal_lines, vertical_lines):
    points = []

    # 找到所有交点
    for h_line in horizontal_lines:
        for v_line in vertical_lines:
            intersection = get_intersection(h_line, v_line)
            if intersection:
                points.append(intersection)

    # 确保交点足够形成网格
    if len(points) < 16:
        raise ValueError("交点数量不足以形成网格")

    #线交叉点

    #每4个元素按X轴排序
    points = sort_points_by_x(points)
    #调换逆时针时的序号顺序！！！
    reverse_order_map = [12,8,4,0, 13,9,5,1, 14,10,6,2, 15,11,7,3]
    points_temp = []
    #print(horizontal_lines[0])
    if horizontal_lines[0][7] < -130:
        for n in range(16):
            points_temp.append(points[reverse_order_map[n]])
        points = points_temp

    #return points
    # 计算方格中心点
    def calculate_center(p1, p2, p3, p4):
        return (round((p1[0] + p2[0] + p3[0] + p4[0]) / 4), round((p1[1] + p2[1] + p3[1] + p4[1]) / 4))

    centers = []
    rows, cols = 4, 4  # 4x4的网格形成3x3的方格
    for i in range(rows - 1):
        for j in range(cols - 1):
            p1 = points[i * cols + j]
            p2 = points[i * cols + j + 1]
            p3 = points[(i + 1) * cols + j]
            p4 = points[(i + 1) * cols + j + 1]
            centers.append(calculate_center(p1, p2, p3, p4))

    return [points, centers]






def checkerboard_positioning(img, img_to_draw=None):
    global checkerboard_disappear_count,checkerboard_centers,checkerboard_points, loop

    #img.rotation_corr(x_rotation=0,y_rotation=0, z_rotation=0)   #画面梯形校正
    #img.midpoint(1, bias=0.9, threshold=True, offset=5, invert=True)    #凸显黑线
    img.gamma_corr(gamma=0.8)
    lines = img.find_lines(threshold=1000, theta_margin=25, rho_margin=25)

    if lines:
        lines = filter_lines(lines,draw=False)
        if len(lines) == 2:
            if len(lines[0]) == 4 and len(lines[1]) == 4:
                [points, centers] = find_grid_centers(lines[0],lines[1])
                if centers:
                    checkerboard_disappear_count = 0
                    centers_processor.add_data(centers)
                    checkerboard_centers = centers_processor.get_filtered_data()

                if points:
                    checkerboard_disappear_count = 0
                    points_processor.add_data(points)
                    checkerboard_points = points_processor.get_filtered_data()
                else:
                    #print('找中心点失败')
                    checkerboard_disappear_count += 1
            else:
                #print('线条数量错误')
                checkerboard_disappear_count += 1
        else:
            #print('线条组数量错误')
            checkerboard_disappear_count += 1
    else:
        #print('没找到线条')
        checkerboard_disappear_count += 1

    if checkerboard_disappear_count > 20:
        checkerboard_centers = []
        checkerboard_points = []
    #求棋盘左右边界
    x_values = [coord[0] for coord in checkerboard_points]
    if x_values:
        x_min = min(x_values)
        x_max = max(x_values)
    else:
        x_min = 0
        x_max = 0
    #如果绘制
    if img_to_draw:
        if checkerboard_centers:
            #print(checkerboard_centers)
            for index in range(len(checkerboard_centers)):
                img_to_draw.draw_string(round(checkerboard_centers[index][0])-6, round(checkerboard_centers[index][1])-10 ,str(index+1),scale=2, color=(255,0,0))
        if checkerboard_points:
            for index in range(len(checkerboard_points)):
                img_to_draw.draw_cross(round(checkerboard_points[index][0]), round(checkerboard_points[index][1]), thickness=2, color=(255,0,0))
                #img_to_draw.draw_string(round(checkerboard_points[index][0])-6, round(checkerboard_points[index][1])-10 ,str(index),scale=1.5, color=(255,0,0))
        img_to_draw.draw_line(x_min,0,x_min,240,color=(255,0,0))
        img_to_draw.draw_line(x_max,0,x_max,240,color=(255,0,0))
    #print(checkerboard_points)

    return [[x_min,x_max],checkerboard_centers]



#数据（坐标）是否稳定了
last_contrast_value = []
stable_count = 0
def is_stable(value, threshold = 10, count_threshold = 15):
    global last_contrast_value,stable_count
    if not value:
        stable_count = 0
        last_contrast_value = []
        return False
    for n in range(len(value)):
        try: #解决首次last_contrast_value为空的问题
            if abs(value[n][0] - last_contrast_value[n][0] ) > threshold or\
                abs(value[n][1] - last_contrast_value[n][1] ) > threshold:
                    stable_count = 0
                    last_contrast_value = value
                    return False
        except:
            last_contrast_value = value
            return False
    stable_count += 1
    if stable_count > count_threshold:
        last_contrast_value = value
        return True
    else:
        return False

last_num = 0
stable_circle_count = 0
def is_circles_stable(num, count_threshold = 20):
    global last_num, stable_circle_count
    if last_num == 0:
        last_num = num
        return False
    if num != last_num:
        stable_circle_count = 0
        last_num = num
        return False

    stable_circle_count += 1
    if stable_circle_count > count_threshold:
        last_num = num
        stable_circle_count
        return True
    else:
        return False



def find_circles_all(img, centers, scale_factor=2):
    circles = img.find_circles(
       threshold=2000,
       x_margin=10,
       y_margin=10,
       r_margin=10,
       r_min=2,
       r_max=20,
       r_step=2,
    )

     # 对检测到的圆形进行验证和筛选
    valid_circles = []
    out_circles = []

    for c in circles:
        in_board = 0
        for center in centers:
            scaled_center = (center[0] / scale_factor, center[1] / scale_factor)
            if euclidean_distance((c.x(), c.y()), scaled_center) < c.r():
                valid_circles.append([c.x() * scale_factor, c.y() * scale_factor, c.r() * scale_factor])
                in_board = 1
                break
        if not in_board:
            out_circles.append([c.x() * scale_factor, c.y() * scale_factor, c.r() * scale_factor])

    return valid_circles, out_circles



def get_board_state(img, checkerboard_position, checkerboard_boundary, scale_factor=2, draw=0):
    piece_color_threshold = [70, 40]

    # 初始化棋盘状态
    current_board_state = [[" " for _ in range(3)] for _ in range(3)]

    # 在棋盘内部检测圆形棋子
    in_circles, out_circles = find_circles_all(img, checkerboard_position, scale_factor)

    # 更新棋盘状态
    for c in in_circles:
        x, y, r = c

        # 获取圆内矩形区域的亮度值
        length = round(r / 2)  # /1.414是内切矩形，为了安全，/2
        piece_brightness = img.get_statistics(roi=[round(x/scale_factor) - length, round(y/scale_factor) - length, length * 2, length * 2]).mean()

        if piece_brightness > piece_color_threshold[0]:
            label = "O"
        else:  # 假设白色圆为 'O'
            label = "X"

        for idx, center in enumerate(checkerboard_position):
            if euclidean_distance((x, y), center) < r:
                row, col = divmod(idx, 3)
                current_board_state[row][col] = label
                break

        if draw:
            img.draw_circle(round(x/scale_factor), round(y/scale_factor), round(r/scale_factor), color=(0, 255, 0) if label == "O" else (255, 0, 0))
            img.draw_string(round(x/scale_factor) - 10, round(y/scale_factor) - 10, label, color=(0, 255, 0) if label == "O" else (255, 0, 0))


    for c in out_circles:
        x, y, r = c

        # 获取圆内矩形区域的亮度值
        length = round(r / 2)  # /1.414是内切矩形，为了安全，/2
        piece_brightness = img.get_statistics(roi=[round(x/scale_factor) - length, round(y/scale_factor) - length, length * 2, length * 2]).mean()

        if piece_brightness > piece_color_threshold[0]:
            label = "O"
        else:  # 假设白色圆为 'O'
            label = "X"

        c.append(label)

        if draw:
            img.draw_circle(round(x/scale_factor), round(y/scale_factor), round(r/scale_factor), color=(0, 255, 0) if label == "O" else (255, 0, 0))
            img.draw_string(round(x/scale_factor) - 10, round(y/scale_factor) - 10, label, color=(0, 255, 0) if label == "O" else (255, 0, 0))
    # 排序函数
    def sort_data(data):
        # 按棋子类型和第一项的值排序
        sorted_data = sorted(data, key=lambda x: (x[3], x[0], x[1]))
        return sorted_data

    # 排序后的数据
    out_circles = sort_data(out_circles)

    return current_board_state, out_circles





def detect():

    global centers_processor, points_processor, loop, checkerboard_disappear_count, checkerboard_centers, checkerboard_points

    #平均值滤波器
    #中心点的平均值滤波器
    centers_processor = CoordinateProcessor(
        coord_count=9,  # 坐标数量
        avg_count=30,  # 平均次数
        diff_threshold=10,  # 重置数据的差异阈值
        diff_reset_count=4,  # 重置数据的差异连续出现次数
        timeout_threshold=2  # 没有数据清空输出的超时时间阈值
    )
    #交叉点的平均值滤波器
    points_processor = CoordinateProcessor(
        coord_count=16,  # 坐标数量
        avg_count=30,  # 平均次数
        diff_threshold=10,  # 重置数据的差异阈值
        diff_reset_count=4,  # 重置数据的差异连续出现次数
        timeout_threshold=2  # 没有数据清空输出的超时时间阈值
    )

    loop = True
    checkerboard_disappear_count = 0
    checkerboard_centers = []
    checkerboard_points = []

    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_brightness(1)   #设置亮度
    sensor.set_contrast(2) #对比度
    sensor.set_gainceiling(2)   #增益上限
    sensor.skip_frames(time=500)
    clock = time.clock()

    img_QQVGA = sensor.alloc_extra_fb(160, 120, sensor.RGB565)

    while True:
        img = sensor.snapshot()
        img.lens_corr(strength=1.2, zoom=1.0)


        # 定位棋盘
        checkerboard_boundary, checkerboard_position = checkerboard_positioning(img, img_to_draw=img)
        stable = is_stable(checkerboard_position, count_threshold=10)

        img.draw_circle(10, 10, 5, fill=True, color=(0, 255, 0) if stable else (255, 0, 0))
        if stable:
            break


    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)

    while True:
        img = sensor.snapshot()
        img.lens_corr(strength=1.2, zoom=1.0)
        img_QQVGA.draw_image(img, 0, 0, x_scale=0.5, y_scale=0.5)

        current_board_state, out_circles = get_board_state(img_QQVGA, checkerboard_position, checkerboard_boundary)

        stable = is_circles_stable(len(out_circles),  count_threshold=10)
        img.draw_circle(10, 10, 5, fill=True, color=(0, 255, 0) if stable else (255, 0, 0))

        for index in range(len(checkerboard_position)):
            img.draw_string(round(checkerboard_position[index][0]) - 6, round(checkerboard_position[index][1]) - 10, str(index + 1), scale=2, color=(255, 0, 0))

        if stable:
            break


#    print(current_board_state)
#    print(out_circles)
#    print(checkerboard_position)
    return current_board_state, out_circles, checkerboard_position

if __name__ == "__main__":
    while True:
        detect()
