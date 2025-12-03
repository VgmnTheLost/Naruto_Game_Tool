import os
import sys
import traceback
from dataclasses import dataclass
from typing import Optional, Dict

from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QLabel, QApplication, QPushButton, QGraphicsOpacityEffect, QWidget
from pynput import keyboard

customConfig = {
    "countdown_time": 13.4,  # 倒计时时间,单位秒
    "detect_interval": 50,  # 检测间隔,单位毫秒
    "rgb_tolerance": 3,  # 色值容差
    "distance_sq_threshold": 12288,  # 欧式距离阈值
    "close": "\\",  # 关闭程序按键
    "clear_left_countdown": "z",  # 清除左侧倒计时按键
    "clear_right_countdown": "c",  # 清除右侧倒计时按键
    "clear_all_countdown": "v",  # 清除全部倒计时按键

    # 主窗口
    "main_window_pos": (810, 200),  # 主窗口位置
    "main_window_size": (300, 150),  # 主窗口大小
    # 文本,几何参数,背景色,文本边框色,字体,字体大小,粗细设置,边框大小,边框圆角半径,不透明度
    "settings_button": ("设置", (50, 120, 50, 30), "#00FFFF", "#000000", "楷体", "20", "bold", "0", "10", 1.0),
    "close_button": ("关闭", (200, 120, 50, 30), "#FF0000", "#000000", "楷体", "20", "bold", "0", "10", 1.0),

    # 设置窗口
    "show_scope_button": ("显示范围", (200, 100, 100, 30), "#FFFFFF", "#885093", "楷体", "20", "bold", "2", "0", 1.0),
    "settings_ui_geometry": (810, 400, 300, 130),  # 设置窗口位置和大小
    "scope_label_geometry": (200, 0, 100, 100),  # 显示范围标签位置和大小
    "scope_pic_size": (100, 100)  # 显示范围图片大小
}
mode_config = {
    "label_geometry": (0, 0, 100, 100),
    "pic_size": (100, 100),
    "button_config": ("决斗场", (0, 100, 100, 30), "#FFFFFF", "#82CA6B", "楷体", "20", "bold", "2", "0", 1.0),
    "battle": {
        "text": "决斗场",
        "color": "#82CA6B",
        "switch": "exercise"
    },
    "exercise": {
        "text": "训练营",
        "color": "#F3A428",
        "switch": "battle"
    }
}
points_detect_config = {
    "pos": {
        "battle": {
            "left": {
                1: (268, 158),
                2: (296, 158),
                3: (324, 158),
                4: (352, 158),
                5: (380, 158),
                6: (408, 158)
            },
            "right": {
                1: (1646, 158),
                2: (1618, 158),
                3: (1590, 158),
                4: (1562, 158),
                5: (1534, 158),
                6: (1506, 158)
            }
        },
        "exercise": {
            "left": {
                1: (250, 155),
                2: (278, 155),
                3: (306, 155),
                4: (334, 155),
                5: (362, 155),
                6: (390, 155)
            },
            "right": {
                1: (1610, 155),
                2: (1582, 155),
                3: (1554, 155),
                4: (1526, 155),
                5: (1508, 155),
                6: (1470, 155)
            }
        }
    },
    "color": [
        (0, (30, 53, 97)),  # 暗
        (1, (55, 215, 235)),  # 浅蓝
        (1, (87, 169, 255)),  # 深蓝，桃博
        (1, (255, 255, 255)),  # 白，加豆特效
        (2, (254, 153, 12)),  # 橙
        (2, (255, 243, 50))  # 黄
    ]
}
points_label_config = {
    "label_content": {
        "left": {
            0: ("◇◇◇◇", "#00000000", "#1e3561"),
            1: ("◆◇◇◇", "#00000000", "#37d7eb"),
            2: ("◆◆◇◇", "#00000000", "#37d7eb"),
            3: ("◆◆◆◇", "#00000000", "#37d7eb"),
            4: ("◆◆◆◆", "#00000000", "#fe990c"),
            5: ("◆◆◆◆◆◇", "#00000000", "#D8200D"),
            6: ("◆◆◆◆◆◆", "#00000000", "#D8200D")
        },
        "right": {
            0: ("◇◇◇◇", "#00000000", "#1e3561"),
            1: ("◇◇◇◆", "#00000000", "#37d7eb"),
            2: ("◇◇◆◆", "#00000000", "#37d7eb"),
            3: ("◇◆◆◆", "#00000000", "#37d7eb"),
            4: ("◆◆◆◆", "#00000000", "#fe990c"),
            5: ("◇◆◆◆◆◆", "#00000000", "#D8200D"),
            6: ("◆◆◆◆◆◆", "#00000000", "#D8200D")
        }
    },
    "label_pos": {
        "left": (0, 0),
        "right": (150, 0)
    },
    "label_size": (150, 30),
    "label_config": ("#000000", "#000000", "楷体", "25", "bold", "0", "0", 1.0)
}
countdown_config = {
    "time_label_geometry": (100, 35, 100, 60),
    "time_label_config": ("#FFFFFF", "#000000", "楷体", "20", "bold", "2", "0", 1.0),
    "plus_button_config": ("增加延迟", (100, 0, 100, 35), "#FFFFFF", "#FF0000", "楷体", "20", "bold", "2", "0", 1.0),
    "dec_button_config": ("减少延迟", (100, 95, 100, 35), "#FFFFFF", "#0080FF", "楷体", "20", "bold", "2", "0", 1.0),
    "init_pos": {
        "left": (0, 30),
        "right": (250, 30)
    },
    "size": (50, 30),
    "label_config": ("#FFFFFF", "#FF0000", "楷体", "25", "bold", "0", "0", 1.0)
}
special_scene = {
    "in_battle": {
        "pos": [(918, 73), (932, 72), (927, 80), (1004, 80), (1013, 74)],
        "min_rgb": (212, 13, 2),
        "max_rgb": (253, 37, 20)
    },
    "next_round": {
        "pos": [(885, 707), (1003, 675), (947, 832), (1051, 745), (997, 815), (1068, 849), (960, 920)],
        "min_rgb": (250, 23, 2),
        "max_rgb": (253, 233, 5)
    },
    "end_battle": {
        "pos": [(222, 72), (339, 72), (1204, 79), (1338, 64)],
        "min_rgb": (250, 200, 2),
        "max_rgb": (253, 203, 5)
    }
}


@dataclass
# 倒计时元数据封装
class Countdown:
    remaining_time: float
    label: QLabel
    timer: QTimer


# 键盘监听线程类
class KeyListenThread(QThread):
    key_pressed: pyqtSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True
        self.listener = None

    def run(self):
        def on_press(key):
            if not self.running:
                return
            try:
                key_name = key.char if key.char is not None else str(key)
            except AttributeError:
                key_name = str(key)
            self.key_pressed.emit(key_name)

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()
        while self.running and self.listener.is_alive():
            self.msleep(100)
        if self.listener.is_alive():
            self.listener.stop()
        self.listener.join()

    def stop(self):
        self.running = False
        self.wait(1000)


# 周期性屏幕截图和检测线程类
class ScreenDetectThread(QThread):
    signal: pyqtSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        while self.running:
            try:
                self.signal.emit("screenshot")
                self.signal.emit("detect")
                self.msleep(customConfig["detect_interval"])
            except Exception as e:
                print(f"截屏检测错误: [{type(e).__name__}] {e}\n完整堆栈:\n{traceback.format_exc()}")

    def stop(self):
        self.running = False
        self.wait(1000)


# 主屏幕
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(customConfig["main_window_pos"][0], customConfig["main_window_pos"][1],
                         customConfig["main_window_size"][0], customConfig["main_window_size"][1])
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |  # 移除窗口的所有边框和标题栏
            Qt.WindowType.WindowStaysOnTopHint  # 将窗口设置为总在最顶层
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 将窗口的背景设置为完全透明

        self.cur_mode = "battle"
        self.cur_screenshot = None
        self.drag_pos = None
        self.settings_ui = None
        self.mode_pic_label = None
        self.switch_mode_button = None
        self.countdown_time_label = None
        self.pic_ui = None
        self.points_num = {
            "left": [],
            "right": [],
        }
        self.points_color = {
            "left": {
                1: -617,
                2: -617,
                3: -617,
                4: -617,
                5: -617,
                6: -617,
            },
            "right": {
                1: -617,
                2: -617,
                3: -617,
                4: -617,
                5: -617,
                6: -617,
            }
        }
        self.points: Dict[str, Optional[QLabel]] = {
            "left": None,
            "right": None
        }
        self.countdowns = {
            "left": [],
            "right": []
        }

        self.settings_button = self.create_button(customConfig["settings_button"], self.show_settings_ui)
        self.close_button = self.create_button(customConfig["close_button"], close)

        self.init_points()

        self.listen_thread = KeyListenThread()
        self.listen_thread.key_pressed.connect(self.pressed_key_event)
        self.listen_thread.start()

        self.detect_thread = ScreenDetectThread()
        self.detect_thread.signal.connect(self.main_event)
        self.detect_thread.start()

    def pressed_key_event(self, event):
        """
        按键事件
        """
        if event.lower() == customConfig["clear_left_countdown"]:
            self.remove_countdown("left")
        elif event.lower() == customConfig["clear_right_countdown"]:
            self.remove_countdown("right")
        elif event.lower() == customConfig["clear_all_countdown"]:
            self.remove_countdown("left")
            self.remove_countdown("right")
        elif event.lower() == customConfig["close"]:
            close()

    def main_event(self, event):
        """
        主要事件
        """
        if event == "screenshot":
            try:
                self.cur_screenshot = app.primaryScreen().grabWindow(0)
            except Exception as e:
                print(f"截屏错误: [{type(e).__name__}] {e}\n完整堆栈:\n{traceback.format_exc()}")
        elif event == "detect":
            try:
                if self.cur_screenshot:
                    if self.cur_mode == "battle":
                        if self.detect_special_scene("in_battle"):
                            for side in self.points:
                                if self.points[side].isHidden():
                                    self.points[side].show()
                            self.detect_points_color()
                            self.detect_points_num()
                        else:
                            if (self.detect_special_scene("next_round") or
                                    self.detect_special_scene("end_battle")):
                                self.remove_countdown("left")
                                self.remove_countdown("right")
                            for side in self.points:
                                if self.points[side].isVisible():
                                    self.points[side].hide()
                    elif self.cur_mode == "exercise":
                        for side in self.points:
                                self.points[side].show()
                        self.detect_points_color()
                        self.detect_points_num()
            except Exception as e:
                print(f"检测错误: [{type(e).__name__}] {e}\n完整堆栈:\n{traceback.format_exc()}")
        elif event == "left" or "right":
            self.create_countdown(event)

    def mousePressEvent(self, event):
        """
        鼠标按下事件，记录拖拽起始位置
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件，实现窗口拖拽
        """
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def closeEvent(self, event):
        """
        窗口关闭事件，确保线程被正确停止
        """
        self.listen_thread.stop()
        self.detect_thread.stop()
        super().closeEvent(event)

    def create_button(self, button_config, click_callback, parent=None):
        """
        创建按钮
        """
        text, geometry, bg_color, color, font_family, font_size, font_weight, border_size, border_radius, opacity = button_config
        button: QPushButton = QPushButton(text, parent if parent is not None else self)
        button.setGeometry(*geometry)
        button.setStyleSheet(f"""
            background-color: {bg_color};
            color: {color};
            font-family: "{font_family}";
            font-size: {font_size}px;
            font-weight: {font_weight};
            border: {border_size} solid {color};
            border-radius: {border_radius}px;
        """)
        opacity_effect = QGraphicsOpacityEffect(button)
        opacity_effect.setOpacity(opacity)
        button.setGraphicsEffect(opacity_effect)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.clicked.connect(click_callback)
        return button

    def create_label(self, content, geometry, label_config=None, parent=None):
        """
        创建标签
        """
        if isinstance(content, QPixmap):
            label = QLabel(parent if parent is not None else self)
            label.setGeometry(*geometry)
            label.setPixmap(content)
        else:
            bg_color, color, font_family, font_size, font_weight, border_size, border_radius, opacity = label_config
            label = QLabel(content, parent if parent is not None else self)
            label.setGeometry(*geometry)
            label.setStyleSheet(f"""
                background-color: {bg_color};
                color: {color};
                font-family: "{font_family}";
                font-size: {font_size}px;
                font-weight: {font_weight};
                border: {border_size} solid {color};
                border-radius: {border_radius}px;
            """)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            opacity_effect = QGraphicsOpacityEffect(label)
            opacity_effect.setOpacity(opacity)
            label.setGraphicsEffect(opacity_effect)
        return label

########################################################设置-相关########################################################
    def show_settings_ui(self):
        """
        显示设置界面
        """
        if self.settings_ui is None:
            self.settings_ui = QWidget()
            self.settings_ui.setWindowTitle("设置")
            self.settings_ui.setGeometry(*customConfig["settings_ui_geometry"])

            self.mode_pic_label = self.create_label(get_scaled_pic("resource/battle.png", mode_config["pic_size"]),
                                                    mode_config["label_geometry"], parent=self.settings_ui)
            self.switch_mode_button = self.create_button(mode_config["button_config"], self.switch_mode, self.settings_ui)

            self.countdown_time_label = self.create_label(f"{customConfig['countdown_time']} 秒",
                                                          countdown_config["time_label_geometry"],
                                                          countdown_config["time_label_config"], self.settings_ui)
            self.create_button(countdown_config["plus_button_config"], lambda: self.adjust_countdown(0.1), self.settings_ui)
            self.create_button(countdown_config["dec_button_config"], lambda: self.adjust_countdown(-0.1), self.settings_ui)

            self.create_label(get_scaled_pic("resource/show_scope.png", customConfig["scope_pic_size"]),
                              customConfig["scope_label_geometry"], parent=self.settings_ui)
            self.create_button(customConfig["show_scope_button"],
                               lambda: self.show_pic("resource/x_axis.png"), self.settings_ui)

        if self.settings_ui.isVisible():
            self.settings_ui.hide()
        else:
            self.settings_ui.show()

    def switch_mode(self):
        """
        切换模式
        """
        switched_mode = mode_config[self.cur_mode]["switch"]

        mode_pic = get_scaled_pic(f"resource/{switched_mode}.png", mode_config["pic_size"])
        self.mode_pic_label.setPixmap(mode_pic)

        original_style = self.switch_mode_button.styleSheet()
        switched_color = mode_config[switched_mode]['color']
        self.switch_mode_button.setText(f"{mode_config[switched_mode]['text']}")
        self.switch_mode_button.setStyleSheet(f"""
            {original_style}
            color: {switched_color};
            border-color: {switched_color};
        """)

        self.remove_countdown("left")
        self.remove_countdown("right")
        self.update_points("left", 0)
        self.update_points("right", 0)

        self.cur_mode = switched_mode

    def adjust_countdown(self, adjust_time):
        """
        调整倒计时时间
        """
        customConfig["countdown_time"] += adjust_time
        self.countdown_time_label.setText(f"{customConfig['countdown_time']:.1f} 秒")

    def show_pic(self, pic_path):
        """
        显示图片
        """
        if self.pic_ui is not None:
            self.pic_ui.hide() if self.pic_ui.isVisible() else self.pic_ui.show()
        else:
            self.pic_ui = QWidget()
            self.pic_ui.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.Tool |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.WindowTransparentForInput)  # 无视输入
            self.pic_ui.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            screen_size = (app.primaryScreen().size().width(), app.primaryScreen().size().height())
            self.pic_ui.setGeometry(0, 0, screen_size[0], screen_size[1])
            self.create_label(get_scaled_pic(pic_path, screen_size),
                                          (0, -28, screen_size[0], screen_size[1]), parent=self.pic_ui)
            self.pic_ui.show()

########################################################检测-相关########################################################
    def detect_special_scene(self, scene):
        """
        检测特殊场景
        """
        xy_list = special_scene[scene]["pos"]
        min_rgb = special_scene[scene]["min_rgb"]
        max_rgb = special_scene[scene]["max_rgb"]
        screen_image = self.cur_screenshot.toImage()

        for x, y in xy_list:
            pixel_rgb = get_pixel_rgb(screen_image, x, y)
            if not pixel_rgb_valid(pixel_rgb, min_rgb, max_rgb, customConfig["rgb_tolerance"]):
                return False
        return True

    def detect_points_color(self):
        """
        检测奥义点颜色
        """
        screen_image = self.cur_screenshot.toImage()
        for side in points_detect_config["pos"][self.cur_mode]:
            for point, (x, y) in points_detect_config["pos"][self.cur_mode][side].items():
                rgb = get_pixel_rgb(screen_image, x, y)
                color = find_most_similar_color(points_detect_config["color"], rgb, customConfig["distance_sq_threshold"])
                self.points_color[side][point] = color

    def detect_points_num(self):
        """
        检测奥义点数量
        """
        # 规则格式：(有效颜色, 有效点位, 无效点位, 匹配数量)
        match_rules = [
            ([0], (1, 4), None, 0),
            ([1], (1, 1), (2, 4), 1),
            ([1], (1, 2), (3, 4), 2),
            ([1], (1, 3), (4, 4), 3),
            ([2], (1, 4), None, 4),
            # 特殊：六尾鸣、柱间
            ([3], (1, 1), (2, 4), 1),
            ([3], (1, 2), (3, 4), 2),
            ([3], (1, 3), (4, 4), 3),
            ([3], (1, 5), (6, 6), 5),
            ([3], (1, 6), None, 6),
            ([3], (1, 4), None, 4),
        ]

        for side in self.points_color:
            count = -617
            colors = [self.points_color[side][point] for point in range(1, 7)]
            for rule in match_rules:
                valid_color, (start, end), exclude_range, target_count = rule
                core_valid = all(colors[i - 1] in valid_color for i in range(start, end + 1))
                exclude_valid = True
                if exclude_range:
                    ex_start, ex_end = exclude_range
                    exclude_valid = all(colors[i - 1] == 0 for i in range(ex_start, ex_end + 1))
                if core_valid and exclude_valid:
                    count = target_count
                    break

            self.update_points(side, count)
            self.points_num[side].append(count)
            if len(self.points_num[side]) > 20:
                self.points_num[side].pop(0)
            self.detect_points_dec(side, 5)

    def detect_points_dec(self, side, num):
        """
        检测奥义点扣减
        """
        if len(self.points_num[side]) < 2 * num:
            return

        before = self.points_num[side][:num]
        after = self.points_num[side][-num:]
        before_all_same = all(num == before[0] for num in before)
        after_all_same = all(num == after[0] for num in after)

        if before_all_same and after_all_same:
            if (before[0] - after[0]) == 1:
                self.detect_thread.signal.emit(side)
                self.points_num[side].clear()

#######################################################奥义点相关########################################################
    def init_points(self):
        """
        初始化奥义点
        """
        for side in self.points:
            pos = points_label_config["label_pos"][side]
            size = points_label_config["label_size"]
            geometry = (pos[0], pos[1], size[0], size[1])
            self.points[side] = self.create_label("", geometry, points_label_config["label_config"])
            self.points[side].show()

    def update_points(self, side, count):
        """
        更新奥义点
        """
        if count < 0:
            return
        content = points_label_config["label_content"][side][count]
        text = content[0]
        bg_color = content[1]
        text_color = content[2]
        self.points[side].setText(text)
        self.points[side].setStyleSheet(f"""
            {self.points[side].styleSheet()}
            background-color: {bg_color};
            color: {text_color};
        """)

#######################################################倒计时相关########################################################
    def cal_new_countdown_pos(self, side):
        """
        计算新倒计时位置
        """
        visible_countdowns = [countdown for countdown in self.countdowns[side] if countdown.label.isVisible()]
        x, init_y = countdown_config["init_pos"][side]
        offset_y = len(visible_countdowns) * countdown_config["size"][1]
        return x, init_y + offset_y

    def create_countdown(self, side):
        """
        创建倒计时
        """
        remaining_time = customConfig["countdown_time"]
        pos = self.cal_new_countdown_pos(side)
        size = countdown_config["size"]
        geometry = (pos[0], pos[1], size[0], size[1])

        label = self.create_label(f"{remaining_time:.1f}", geometry, countdown_config["label_config"])
        label.show()

        timer: QTimer = QTimer(self)
        timer.setInterval(100)
        timer.timeout.connect(lambda: self.update_countdown(side, countdown))
        timer.start()

        countdown = Countdown(
            remaining_time=remaining_time,
            label=label,
            timer=timer
        )
        self.countdowns[side].append(countdown)

    def update_countdown(self, side, countdown):
        """
        更新倒计时
        """
        countdown.remaining_time = round(countdown.remaining_time - 0.1, 1)
        countdown.label.setText(f"{countdown.remaining_time:.1f}")
        if countdown.remaining_time < 0.1:
            QTimer.singleShot(10, lambda: self.remove_countdown(side, countdown))

    def remove_countdown(self, side, target_countdown=None):
        """
        移除倒计时：支持删除指定倒计时或清空指定侧所有倒计时
        """
        countdowns = self.countdowns[side]
        if target_countdown is None:
            for countdown in countdowns:
                countdown.label.hide()
                countdown.label.deleteLater()
                countdown.timer.stop()
            countdowns.clear()
        else:
            target_countdown.label.hide()
            target_countdown.label.deleteLater()
            target_countdown.timer.stop()
            if target_countdown in countdowns:
                countdowns.remove(target_countdown)

########################################################颜色相关#########################################################
def get_pixel_rgb(image, pixel_x, pixel_y):
    """
    获取图片中指定像素点的rgb颜色
    """
    rgb = image.pixelColor(pixel_x, pixel_y)
    return rgb.red(), rgb.green(), rgb.blue()


def find_most_similar_color(color_list, target_rgb, min_distance_sq):
    """
    在rgb颜色列表中找到与目标rgb颜色最相似的颜色,且二者欧式距离小于阈值
    """
    most_similar_color = -617
    tr, tg, tb = target_rgb

    for color, color_rgb in color_list:
        cr, cg, cb = color_rgb
        distance_sq = (tr - cr) ** 2 + (tg - cg) ** 2 + (tb - cb) ** 2

        if distance_sq < min_distance_sq:
            min_distance_sq = distance_sq
            most_similar_color = color

    return most_similar_color


def pixel_rgb_valid(pixel_rgb, min_rgb, max_rgb, rgb_tolerance):
    """
    判断像素点的rgb颜色是否符合要求
    """
    for cur_val, min_val, max_val in zip(pixel_rgb, min_rgb, max_rgb):
        if cur_val < (min_val - rgb_tolerance) or cur_val > (max_val + rgb_tolerance):
            return False
    return True


def resource_path(relative_path):
    """
    使得打包后的环境和原始的开发环境，都能正确地定位到项目的资源文件
    """
    base_path = getattr(sys, '_MEIPASS', None)
    if not base_path:
        base_path = os.path.abspath(os.path.dirname(__file__))
    abs_path = os.path.join(base_path, relative_path)
    return os.path.normpath(abs_path)


def get_scaled_pic(pic_path, pic_size):
    """
    获取调整大小后的图片
    """
    pic = QPixmap(resource_path(pic_path))
    return pic.scaled(pic_size[0], pic_size[1],
                      Qt.AspectRatioMode.KeepAspectRatio,  # 宽高比保持策略
                      Qt.TransformationMode.SmoothTransformation)  # 平滑缩放算法


def close():
    """
    退出程序
    """
    app.quit()
    sys.exit(666)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

# pyinstaller --onefile --noconsole --add-data "resource;resource" --icon=resource/icon.ico Main.py
