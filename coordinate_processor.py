class CoordinateProcessor:
    def __init__(self, coord_count, avg_count, diff_threshold, diff_reset_count, timeout_threshold):
        # 初始化处理器参数
        self.coord_count = coord_count  # 坐标数量
        self.avg_count = avg_count  # 平均次数
        self.diff_threshold = diff_threshold  # 重置数据的差异阈值
        self.diff_reset_count = diff_reset_count  # 重置数据的差异连续出现次数
        self.timeout_threshold = timeout_threshold  # 没有数据清空输出的超时时间阈值
        self.data_pool = [[] for _ in range(coord_count)]  # 数据池
        self.backup_pool = [[] for _ in range(coord_count)]  # 备份池
        self.missed_data_count = 0  # 未收到有效数据计数
        self.diff_count = 0  # 差异计数

    def add_data(self, new_data):
        if len(new_data) != self.coord_count:
            raise ValueError(f"Expected {self.coord_count} coordinates, got {len(new_data)}")

        # 检查差异
        significant_diff = False
        if self.data_pool[0]:  # 仅在存在现有数据时检查
            for i in range(self.coord_count):
                if abs(self.data_pool[i][-1][0] - new_data[i][0]) > self.diff_threshold or \
                   abs(self.data_pool[i][-1][1] - new_data[i][1]) > self.diff_threshold:
                    significant_diff = True
                    break

        if significant_diff:
            self.diff_count += 1
            if self.diff_count >= self.diff_reset_count:
                self.data_pool = [[] for _ in range(self.coord_count)]  # 重置数据池
                self.diff_count = 0
                self.missed_data_count = 0
        else:
            self.diff_count = 0
            self.missed_data_count = 0
            for i in range(self.coord_count):
                if len(self.data_pool[i]) >= self.avg_count:
                    self.data_pool[i].pop(0)  # 移除最旧的数据
                self.data_pool[i].append(new_data[i])  # 添加新数据

    def get_filtered_data(self):
        if all(len(pool) == self.avg_count for pool in self.data_pool):
            avg_data = [
                (round(sum(coord[0] for coord in pool) / len(pool)),
                 round(sum(coord[1] for coord in pool) / len(pool)))
                for pool in self.data_pool
            ]
            self.backup_pool = [list(pool) for pool in self.data_pool]  # 更新备份池
            return avg_data
        else:
            if all(len(pool) == 0 for pool in self.data_pool):
                return [(0, 0) for _ in range(self.coord_count)]
            else:
                avg_data = [
                    (round(sum(coord[0] for coord in pool) / len(pool)) if len(pool) > 0 else 0,
                     round(sum(coord[1] for coord in pool) / len(pool)) if len(pool) > 0 else 0)
                    for pool in self.data_pool
                ]
                return avg_data

    def handle_no_data(self):
        self.missed_data_count += 1
        if self.missed_data_count >= self.timeout_threshold:
            self.data_pool = [[] for _ in range(self.coord_count)]  # 清空数据池
            self.backup_pool = [[] for _ in range(self.coord_count)]  # 清空备份池
            self.missed_data_count = 0
            return False
        return True
'''
# 示例用法
processor = CoordinateProcessor(
    coord_count=16,  # 坐标数量
    avg_count=5,  # 平均次数
    diff_threshold=10,  # 重置数据的差异阈值
    diff_reset_count=3,  # 重置数据的差异连续出现次数
    timeout_threshold=2  # 没有数据清空输出的超时时间阈值
)

# 添加数据
new_data = [
    (128.477, 62.8605), (178.176, 66.288), (220.917, 69.2356), (265.437, 72.306),
    (124.168, 111.899), (173.785, 116.254), (216.456, 119.999), (260.047, 123.825),
    (119.972, 159.65), (169.657, 163.232), (212.387, 166.313), (255.28, 169.406),
    (115.987, 205.0), (165.836, 206.719), (208.707, 208.197), (251.069, 209.658)
]

processor.add_data(new_data)
filtered_data = processor.get_filtered_data()
print("Filtered Data:", filtered_data)

# 处理没有数据的情况
no_data = processor.handle_no_data()
print("No Data Handling Result:", no_data)
'''
