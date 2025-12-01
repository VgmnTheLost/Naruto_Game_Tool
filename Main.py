import os
import sys
import traceback

from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPalette, QColor
from PyQt6.QtWidgets import QMainWindow, QLabel, QApplication, QPushButton, QGraphicsOpacityEffect, QWidget
from pynput import keyboard

customConfig = {
    "countdown_time": 13.4,  # 倒计时时间,单位秒
    "detect_interval": 50,  # 检测间隔,单位毫秒
    "rgb_tolerance": 3,  # 色值容差
    "distance_sq_threshold": 12288,  # 欧式距离阈值
    "close": "·",  # 关闭程序按键
    "clear_left_countdown": "z",  # 清除左侧倒计时按键
    "clear_right_countdown": "c",  # 清除右侧倒计时按键
    "clear_all_countdown": "v",  # 清除全部倒计时按键

    "main_window_pos": (810, 200),  # 主界面位置
    "main_window_size": (300, 150),  # 主界面大小
    # 按钮 —— 文本,几何参数,背景色,文本边框色,字体,字体大小,粗细设置,边框大小,边框圆角半径,不透明度
    "settings_button": ("设置", (50, 120, 50, 30), "#00FFFF", "#000000", "楷体", "20", "bold", "0", "10", 1.0),
    "close_button": ("关闭", (200, 120, 50, 30), "#FF0000", "#000000", "楷体", "20", "bold", "0", "10", 1.0),
    "mode_button": ("决斗场", (0, 100, 100, 30), "#FFFFFF", "#82CA6B", "楷体", "20", "bold", "2", "0", 1.0),
    "plus_time_button": ("增加延迟", (100, 0, 100, 35), "#FFFFFF", "#FF0000", "楷体", "20", "bold", "2", "0", 1.0),
    "dec_time_button": ("减少延迟", (100, 95, 100, 35), "#FFFFFF", "#0080FF", "楷体", "20", "bold", "2", "0", 1.0),
    "scope_show_button": ("显示范围", (200, 100, 100, 30), "#FFFFFF", "#885093", "楷体", "20", "bold", "2", "0", 1.0),

    # 设置窗口相关
    "settings_ui_geometry": (810, 400, 300, 130),  # 设置窗口位置和大小
    "settings_ui_font_family": "楷体",
    "settings_ui_font_size": "20px",  # 设置窗口字体大小
    "settings_ui_border_size": "2px",  # 设置窗口边框大小

    "mode_label_geometry": (0, 0, 100, 100),  # 模式标签位置和大小
    "mode_pic_size": (100, 100),  # 模式图片大小
    "countdown_time_label_geometry": (100, 35, 100, 60),  # 倒计时标签位置和大小
    "scope_show_label_geometry": (200, 0, 100, 100),  # 范围显示标签位置和大小
    "scope_show_pic_size": (100, 100),  # 范围显示图片大小

    # 奥义点标签设置
    "points_font": "楷体",  # 奥义点标签字体
    "points_font_size": 18,  # 奥义点标签字体大小
    "left_points_pos": (0, 0),  # 左方奥义点标签位置
    "left_points_size": (150, 30),  # 左方奥义点标签大小
    "right_points_pos": (150, 0),  # 右方奥义点标签位置
    "right_points_size": (150, 30),  # 右方奥义点标签大小
    # 倒计时标签设置
    "countdown_label_opacity": 1.0,  # 倒计时标签不透明度
    "countdown_label_font": "楷体",  # 倒计时标签字体
    "countdown_label_font_size": 20,  # 倒计时标签字体大小
    "countdown_label_font_color": "#FF0000",  # 倒计时标签字体颜色
    "countdown_label_bg_color": "#FFFFFF",  # 倒计时标签背景颜色
    "countdown_label_size": (50, 30),  # 倒计时标签大小
    "left_countdown_init_pos": (0, 30),  # 左方倒计时标签位置
    "right_countdown_init_pos": (250, 30),  # 右方倒计时标签位置
}
points_color = [
    (0, (30, 53, 97)),  # 暗
    (1, (55, 215, 235)),  # 浅蓝
    (1, (87, 169, 255)),  # 深蓝，桃博
    (1, (255, 255, 255)),  # 白，加豆特效
    (2, (254, 153, 12)),  # 橙
    (2, (255, 243, 50)),  # 黄
]
points_num = {
    "left": [],
    "right": [],
}
points_show = {
    "left": {
        0: ["◇◇◇◇", "#00000000", "#1e3561"],
        1: ["◆◇◇◇", "#00000000", "#37d7eb"],
        2: ["◆◆◇◇", "#00000000", "#37d7eb"],
        3: ["◆◆◆◇", "#00000000", "#37d7eb"],
        4: ["◆◆◆◆", "#00000000", "#fe990c"],
        5: ["◆◆◆◆◆◇", "#00000000", "#D8200D"],
        6: ["◆◆◆◆◆◆", "#00000000", "#D8200D"],
    },
    "right": {
        0: ["◇◇◇◇", "#00000000", "#1e3561"],
        1: ["◇◇◇◆", "#00000000", "#37d7eb"],
        2: ["◇◇◆◆", "#00000000", "#37d7eb"],
        3: ["◇◆◆◆", "#00000000", "#37d7eb"],
        4: ["◆◆◆◆", "#00000000", "#fe990c"],
        5: ["◇◆◆◆◆◆", "#00000000", "#D8200D"],
        6: ["◆◆◆◆◆◆", "#00000000", "#D8200D"],
    }
}
points_state = {
    "left": {
        1: -1,
        2: -1,
        3: -1,
        4: -1,
        5: -1,
        6: -1,
    },
    "right": {
        1: -1,
        2: -1,
        3: -1,
        4: -1,
        5: -1,
        6: -1,
    }
}
start_battle_detect = {
    "pos": [(433, 124), (461, 124), (1481, 124), (1453, 124)],
    "max_rgb": (253, 87, 25),
    "min_rgb": (130, 40, 10),
}
next_round_detect = {
    "pos": [(885, 707), (1003, 675), (947, 832), (1051, 745), (997, 815), (1068, 849), (960, 920)],
    "max_rgb": (253, 233, 5),
    "min_rgb": (250, 23, 2),
}
end_battle_detect = {
    "pos": [(222, 72), (339, 72), (1204, 79), (1338, 64)],
    "max_rgb": (253, 203, 5),
    "min_rgb": (250, 200, 2),
}
# todo 金水检测
hashirama_detect_battle = {
    "left": [(72, 65), (72, 75), (82, 65), (82, 75)],
    "right": [(1737, 60), (1737, 70), (1747, 60), (1747, 70)],
    "reborn_hashirama_max_rgb": (50, 50, 33),
    "reborn_hashirama_min_rgb": (49, 49, 31),
    "establish_hashirama_max_rgb": (46, 45, 28),
    "establish_hashirama_min_rgb": (46, 45, 27),
}
hashirama_detect_exercise = {
    "left": [(52, 55), (52, 65), (62, 55), (62, 65)],
    "right": [(1697, 60), (1697, 70), (1707, 60), (1707, 70)],
    "reborn_hashirama_max_rgb": (50, 49, 32),
    "reborn_hashirama_min_rgb": (50, 49, 31),
    "establish_hashirama_max_rgb": (46, 45, 28),
    "establish_hashirama_min_rgb": (45, 44, 27),
}
points_pos_battle = {
    "left": {
        1: (268, 158),
        2: (296, 158),
        3: (324, 158),
        4: (352, 158),
        5: (380, 158),
        6: (408, 158),
    },
    "right": {
        1: (1646, 158),
        2: (1618, 158),
        3: (1590, 158),
        4: (1562, 158),
        5: (1534, 158),
        6: (1506, 158),
    }
}
points_pos_exercise = {
    "left": {
        1: (250, 155),
        2: (278, 155),
        3: (306, 155),
        4: (334, 155),
        5: (362, 155),
        6: (390, 155),
    },
    "right": {
        1: (1610, 155),
        2: (1582, 155),
        3: (1554, 155),
        4: (1526, 155),
        5: (1508, 155),
        6: (1470, 155),
    }
}
countdown_init_pos = {
    "left": (0, 30),
    "right": (250, 30),
}
cur_mode = "battle"
enable_flag = False
hashirama_detect = hashirama_detect_battle
points_xy = points_pos_battle


# 键盘监听线程类，用于在后台监听键盘事件并发送信号
class KeyListenerThread(QThread):
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
                print(f"截屏检测错误: {e}")

    def stop(self):
        self.running = False
        self.wait(1000)


# 主屏幕
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(customConfig["main_window_pos"][0], customConfig["main_window_pos"][1],
                         customConfig["main_window_size"][0], customConfig["main_window_size"][1])  # 设置窗口位置和大小
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |  # 移除窗口的所有边框和标题栏
            Qt.WindowType.WindowStaysOnTopHint  # 将窗口设置为总在最顶层
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 将窗口的背景设置为完全透明

        # 定义内部变量
        self.cur_screenshot = None
        self.drag_pos = None
        self.settings_ui = None
        self.mode_switch_label = None
        self.mode_switch_button = None
        self.countdown_time_label = None
        self.plus_time_button = None
        self.dec_time_button = None
        self.scope_show_button = None
        self.scope_show_label = None
        self.pic_ui = None
        self.pic_label = None
        self.left_points_label = None
        self.right_points_label = None

        self.left_countdowns = []  # 存储左侧倒计时
        self.right_countdowns = []  # 存储右侧倒计时

        self.settings_button = self.create_button(None, customConfig["settings_button"], self.show_settings_ui)  # 创建设置按钮
        self.close_button = self.create_button(None, customConfig["close_button"], close)  # 创建关闭按钮

        self.init_points_label()  # 初始化双方奥义点标签

        # 按键监听线程
        self.listener_thread = KeyListenerThread()
        self.listener_thread.key_pressed.connect(self.key_press_event)
        self.listener_thread.start()

        # 屏幕检测线程
        self.detect_thread = ScreenDetectThread()
        self.detect_thread.signal.connect(self.main_event)
        self.detect_thread.start()

    def key_press_event(self, event):
        """
        键盘按下事件
        """
        if event.lower() == customConfig["close"]:
            close()
        elif event.lower() == customConfig["clear_left_countdown"]:
            self.clear_countdown("left")
        elif event.lower() == customConfig["clear_right_countdown"]:
            self.clear_countdown("right")
        elif event.lower() == customConfig["clear_all_countdown"]:
            self.clear_countdown("left")
            self.clear_countdown("right")
        else:
            pass

    def main_event(self, event):
        """
        主要事件
        """
        global enable_flag
        if event == "screenshot":
            try:
                self.cur_screenshot = app.primaryScreen().grabWindow(0)
            except Exception as e:
                print(f"截屏错误: {e}")
        elif event == "detect":
            try:
                if self.cur_screenshot:
                    if cur_mode == "battle":
                        if not enable_flag and self.detect_special_situation("start_battle_detect", ""):
                            enable_flag = True
                            self.left_points_label.show()
                            self.right_points_label.show()
                        if enable_flag and self.detect_special_situation("end_battle_detect", ""):
                            enable_flag = False
                            self.clear_countdown("left")
                            self.clear_countdown("right")
                            self.left_points_label.hide()
                            self.right_points_label.hide()
                        if enable_flag:
                            if self.detect_special_situation("next_round_detect", ""):
                                self.clear_countdown("left")
                                self.clear_countdown("right")
                            self.detect_points_color_state()
                            self.detect_points_num()
                    elif cur_mode == "exercise":
                        self.detect_points_color_state()
                        self.detect_points_num()
            except Exception as e:
                traceback.print_exc()
                print(f"检测错误: {e}")
        elif event == "left" or "right":
            new_pos = self.cal_new_countdown_label_pos(event)
            self.create_countdown_label(customConfig["countdown_time"], new_pos, event)

    def mousePressEvent(self, event):
        """
        鼠标按下事件，记录拖拽起始位置
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # 记录鼠标按下时的位置
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件，实现窗口拖拽
        """
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos is not None:
            # 计算新位置并移动窗口
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def closeEvent(self, event):
        """
        窗口关闭事件，确保线程被正确停止
        """
        self.listener_thread.stop()
        self.detect_thread.stop()
        super().closeEvent(event)

    def create_button(self, parent, button_config, click_callback):
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

        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # 取消焦点框
        button.clicked.connect(click_callback)  # 绑定点击事件

        return button

########################################################设置-相关########################################################
    def show_settings_ui(self):
        """
        显示设置界面
        """
        if self.settings_ui is None:
            # 设置主界面
            self.settings_ui = QWidget()
            self.settings_ui.setWindowTitle("设置")
            self.settings_ui.setGeometry(*customConfig["settings_ui_geometry"])

            # 模式图片标签
            self.mode_switch_label = QLabel(self.settings_ui)
            self.mode_switch_label.setGeometry(*customConfig["mode_label_geometry"])
            base_mode_pic = QPixmap(resource_path("resource/决斗场.png"))
            mode_pic = base_mode_pic.scaled(customConfig["mode_pic_size"][0],
                                            customConfig["mode_pic_size"][1],
                                            Qt.AspectRatioMode.KeepAspectRatio,  # 宽高比保持策略
                                            Qt.TransformationMode.SmoothTransformation)  # 平滑缩放算法
            self.mode_switch_label.setPixmap(mode_pic)
            # 模式切换按钮
            self.mode_switch_button = self.create_button(self.settings_ui, customConfig["mode_button"], self.switch_mode)

            # 倒计时时间标签
            self.countdown_time_label = QLabel(f"{customConfig['countdown_time']} 秒", self.settings_ui)
            self.countdown_time_label.setGeometry(*customConfig["countdown_time_label_geometry"])
            self.countdown_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.countdown_time_label.setStyleSheet(f"""
                background-color: #FFFFFF;
                color: #000000;
                font-family: {customConfig['settings_ui_font_family']};
                font-size: {customConfig['settings_ui_font_size']};
                font-weight: bold;
                border: {customConfig['settings_ui_border_size']} solid #00FF00;
                """)
            # 增加倒计时时间按钮
            self.plus_time_button = self.create_button(self.settings_ui, customConfig["plus_time_button"],
                                                       lambda: self.adjust_countdown(0.1))
            # 减少倒计时时间按钮
            self.dec_time_button = self.create_button(self.settings_ui, customConfig["dec_time_button"],
                                                      lambda: self.adjust_countdown(-0.1))

            # 范围显示标签
            self.scope_show_label = QLabel(self.settings_ui)
            self.scope_show_label.setGeometry(*customConfig["scope_show_label_geometry"])
            scope_show_base_pic = QPixmap(resource_path("resource/范围显示.png"))
            scope_show_pic = scope_show_base_pic.scaled(customConfig["scope_show_pic_size"][0],
                                                        customConfig["scope_show_pic_size"][1],
                                                        Qt.AspectRatioMode.KeepAspectRatio,
                                                        Qt.TransformationMode.SmoothTransformation)
            self.scope_show_label.setPixmap(scope_show_pic)
            # 范围显示按钮
            self.scope_show_button = self.create_button(self.settings_ui, customConfig["scope_show_button"],
                                                        lambda: self.show_pic(QPixmap(resource_path("resource/X轴范围显示.png"))))

        # 切换窗口的显示状态
        if self.settings_ui.isVisible():
            self.settings_ui.hide()  # 如果窗口可见，则隐藏
        else:
            self.settings_ui.show()  # 如果窗口不可见，则显示

    def switch_mode(self):
        """
        切换模式
        """
        global cur_mode, hashirama_detect, points_xy
        if cur_mode == "battle":
            base_mode_pic = QPixmap(resource_path("resource/训练营.png"))
            mode_pic = base_mode_pic.scaled(customConfig["mode_pic_size"][0],
                                            customConfig["mode_pic_size"][1],
                                            Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
            self.mode_switch_label.setPixmap(mode_pic)
            self.mode_switch_button.setText("训练营")
            self.mode_switch_button.setStyleSheet(f"""
                background-color: #FFFFFF;
                color: #F3A428;
                font-family: {customConfig['settings_ui_font_family']};
                font-size: {customConfig['settings_ui_font_size']};
                font-weight: bold;
                border: {customConfig['settings_ui_border_size']} solid #F3A428;
                """)
            cur_mode = "exercise"
            hashirama_detect = hashirama_detect_exercise
            points_xy = points_pos_exercise
        elif cur_mode == "exercise":
            base_mode_pic = QPixmap(resource_path("resource/决斗场.png"))
            mode_pic = base_mode_pic.scaled(customConfig["mode_pic_size"][0],
                                            customConfig["mode_pic_size"][1],
                                            Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
            self.mode_switch_label.setPixmap(mode_pic)
            self.mode_switch_button.setText("决斗场")
            self.mode_switch_button.setStyleSheet(f"""
                background-color: #FFFFFF;
                color: #82CA6B;
                font-family: {customConfig['settings_ui_font_family']};
                font-size: {customConfig['settings_ui_font_size']};
                font-weight: bold;
                border: {customConfig['settings_ui_border_size']} solid #82CA6B;
                """)
            cur_mode = "battle"
            hashirama_detect = hashirama_detect_battle
            points_xy = points_pos_battle
        self.clear_countdown("left")
        self.clear_countdown("right")
        self.update_points_label("left", 0)
        self.update_points_label("right", 0)

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
        if hasattr(self, 'pic_ui') and self.pic_ui is not None:
            if self.pic_ui.isVisible():
                self.pic_ui.hide()
            else:
                self.pic_ui.show()
        else:
            self.pic_ui = QWidget()
            self.pic_ui.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |  # 无边框
                Qt.WindowType.Tool |  # 隐藏任务栏图标
                Qt.WindowType.WindowStaysOnTopHint |  # 始终顶层
                Qt.WindowType.WindowTransparentForInput)  # 无视输入
            self.pic_ui.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.pic_ui.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
            self.pic_ui.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            screen_size = app.primaryScreen().size()
            self.pic_ui.setGeometry(0, 0, screen_size.width(), screen_size.height())

            self.pic_label = QLabel(self.pic_ui)
            self.pic_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.pic_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.pic_label.setGeometry(0, -28, screen_size.width(), screen_size.height())
            pic = QPixmap(pic_path)
            self.pic_label.setPixmap(
                pic.scaled(screen_size.width(), screen_size.height(), Qt.AspectRatioMode.KeepAspectRatio))
            self.pic_ui.show()

########################################################检测-相关########################################################
    def detect_points_color_state(self):
        """
        检测每个奥义点的颜色状态
        """
        screen_image = self.cur_screenshot.toImage()
        for side in points_xy:
            for point, (x, y) in points_xy[side].items():
                rgb = get_pixel_rgb(screen_image, x, y)

                state = find_most_similar_color(points_color, rgb)

                points_state[side][point] = state

    def detect_special_situation(self, situation, side):
        """
        检测是否满足特殊情况
        """
        if situation == "start_battle_detect":
            xy_list = start_battle_detect["pos"]
            min_rgb_list = [start_battle_detect["min_rgb"]]
            max_rgb_list = [start_battle_detect["max_rgb"]]
        elif situation == "next_round_detect":
            xy_list = next_round_detect["pos"]
            min_rgb_list = [next_round_detect["min_rgb"]]
            max_rgb_list = [next_round_detect["max_rgb"]]
        elif situation == "end_battle_detect":
            xy_list = end_battle_detect["pos"]
            min_rgb_list = [end_battle_detect["min_rgb"]]
            max_rgb_list = [end_battle_detect["max_rgb"]]
        elif situation == "hashirama_detect":
            xy_list = hashirama_detect[side]
            min_rgb_list = [hashirama_detect["reborn_hashirama_min_rgb"],
                            hashirama_detect["establish_hashirama_min_rgb"]]
            max_rgb_list = [hashirama_detect["reborn_hashirama_max_rgb"],
                            hashirama_detect["establish_hashirama_max_rgb"]]
        else:
            return False
        screen_image = self.cur_screenshot.toImage()
        for x, y in xy_list:
            pixel_rgb = get_pixel_rgb(screen_image, x, y)
            for min_rgb, max_rgb in zip(min_rgb_list, max_rgb_list):
                if not pixel_rgb_valid(pixel_rgb, min_rgb, max_rgb, customConfig["rgb_tolerance"]):
                    return False
        return True

    def detect_points_num(self):
        """
        检测双方奥义点的数量
        """
        # 规则格式：(有效颜色状态, 有效点位范围, 无效点位范围, 匹配数量, 是否开启柱间检测)
        match_rules = [
            # 0豆：1-4号点均无效
            ([0], (1, 4), None, 0, False),
            # 1豆：1号点有效，2-4号点无效
            ([1], (1, 1), (2, 4), 1, False),
            # 2豆：1-2号点有效，3-4号点无效
            ([1], (1, 2), (3, 4), 2, False),
            # 3豆：1-3号点有效，4号点无效
            ([1], (1, 3), (4, 4), 3, False),
            # 特殊：柱间
            # 5豆：1-5号点有效，6号点无效
            ([2], (1, 5), (6, 6), 5, True),
            # 6豆：1-6号点均有效
            ([2], (1, 6), None, 6, True),
            # 普通
            # 4豆：1-4号点均有效
            ([1, 2], (1, 4), None, 4, False),
            # 特殊：六尾鸣
            ([2], (1, 1), (2, 4), 1, False),
            ([2], (1, 2), (3, 4), 2, False),
            ([2], (1, 3), (4, 4), 3, False),
        ]
        for side in points_state:
            states = [points_state[side][point] for point in range(1, 7)]
            count = -617
            for rule in match_rules:
                valid_state, (start, end), exclude_range, target_count, flag = rule
                # 检查核心点位：是否均为有效颜色
                core_valid = all(states[i - 1] in valid_state for i in range(start, end + 1))
                # 检查排除点位：是否均为无效颜色
                exclude_valid = True
                if exclude_range:
                    ex_start, ex_end = exclude_range
                    exclude_valid = all(states[i - 1] == 0 for i in range(ex_start, ex_end + 1))
                # 匹配成功，更新数量
                if flag:
                    if self.detect_special_situation("hashirama_detect", side) and core_valid and exclude_valid:
                        count = target_count
                        break
                else:
                    if core_valid and exclude_valid:
                        count = target_count
                        break

            self.update_points_label(side, count)
            points_num[side].append(count)
            if len(points_num[side]) > 20:
                points_num[side].pop(0)
            self.detect_points_dec(side, 5)

    def detect_points_dec(self, side, num):
        """
        检测是否扣豆
        """
        if len(points_num[side]) < 2 * num:
            return

        # 1. 提取前num个和后num个数据
        before = points_num[side][:num]
        after = points_num[side][-num:]

        # 2. 检测前num个是否全部相同
        before_all_same = all(x == before[0] for x in before)
        # 3. 检测后num个是否全部相同
        after_all_same = all(x == after[0] for x in after)

        # 4. 检测后值是否比前值少1
        if before_all_same and after_all_same:
            if (before[0] - after[0]) == 1:
                self.detect_thread.signal.emit(side)
                points_num[side].clear()

#####################################################奥义点标签-相关######################################################
    def init_points_label(self, ):
        """
        初始化奥义点标签
        """
        left_points_pos = customConfig["left_points_pos"]
        left_points_size = customConfig["left_points_size"]
        right_points_pos = customConfig["right_points_pos"]
        right_points_size = customConfig["right_points_size"]
        points_font = customConfig["points_font"]
        points_font_size = customConfig["points_font_size"]

        self.left_points_label = QLabel(self)
        self.left_points_label.setGeometry(left_points_pos[0], left_points_pos[1], left_points_size[0],
                                           left_points_size[1])
        self.left_points_label.setFont(QFont(points_font, points_font_size))
        self.left_points_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.right_points_label = QLabel(self)
        self.right_points_label.setGeometry(right_points_pos[0], right_points_pos[1], right_points_size[0],
                                            right_points_size[1])
        self.right_points_label.setFont(QFont(points_font, points_font_size))
        self.right_points_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.left_points_label.show()
        self.right_points_label.show()

    def update_points_label(self, side, count):
        """
        更新奥义点标签
        """
        if count < 0:
            return
        content = points_show[side][count]
        text = content[0]
        bg_color = content[1]
        text_color = content[2]
        label = self.left_points_label if side == "left" else self.right_points_label
        label.setText(text)
        label.setStyleSheet(f"background-color: {bg_color}; color: {text_color}")

########################################################倒计时相关########################################################
    def cal_new_countdown_label_pos(self, side):
        """
        计算新倒计时标签应该放置的位置
        """
        countdown_list = self.left_countdowns if side == "left" else self.right_countdowns
        initial_pos = countdown_init_pos[side]
        occupied_positions = []
        for (label, _, pos, _) in countdown_list:
            if not label.isVisible():
                continue
            occupied_positions.append(pos)
        if initial_pos not in occupied_positions:
            return initial_pos
        x, y = initial_pos
        _, label_height = customConfig["countdown_label_size"]
        current_y = y
        while True:
            current_y += label_height
            new_pos = (x, current_y)
            if new_pos not in occupied_positions:
                return new_pos

    def create_countdown_label(self, countdown_time, pos, side):
        """
        创建倒计时标签
        """
        countdown_label_size = customConfig["countdown_label_size"]
        countdown_list = self.left_countdowns if side == "left" else self.right_countdowns

        countdown_label = QLabel(self)
        countdown_label.setGeometry(pos[0], pos[1], countdown_label_size[0], countdown_label_size[1])
        countdown_label.setFont(QFont(customConfig["countdown_label_font"], customConfig["countdown_label_font_size"]))
        countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        palette = countdown_label.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(customConfig["countdown_label_bg_color"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(customConfig["countdown_label_font_color"]))
        countdown_label.setPalette(palette)
        countdown_label.setAutoFillBackground(True)

        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(customConfig["countdown_label_opacity"])
        countdown_label.setGraphicsEffect(opacity_effect)

        remaining_time = countdown_time
        countdown_label.setText(f"{remaining_time:.1f}")
        countdown_label.show()

        timer: QTimer = QTimer(self)
        timer.setInterval(100)

        def update_countdown():
            """
            更新倒计时时间
            """
            nonlocal remaining_time
            remaining_time -= 0.1
            remaining_time = round(remaining_time, 1)
            countdown_label.setText(f"{remaining_time:.1f}")

            if remaining_time <= 0:
                timer.stop()
                countdown_label.setText("0.0")
                QTimer.singleShot(100, lambda: self.remove_countdown(countdown_label, side))

        timer.timeout.connect(update_countdown)
        timer.start()

        countdown_list.append((countdown_label, timer, pos, countdown_label_size))

    def remove_countdown(self, countdown_label, side):
        """
        移除指定倒计时
        """
        countdown_list = self.left_countdowns if side == "left" else self.right_countdowns
        for i, (cur_label, cur_timer, _, _) in enumerate(countdown_list):
            if cur_label == countdown_label:
                cur_timer.stop()
                cur_label.hide()
                cur_label.deleteLater()
                countdown_list.pop(i)
                break

    def clear_countdown(self, side):
        """
        清空指定side的所有倒计时
        """
        # 从后往前遍历，避免删除时索引变化的问题
        countdown = self.left_countdowns if side == "left" else self.right_countdowns
        for label, timer, _, _ in reversed(countdown):
            timer.stop()
            label.hide()
            label.deleteLater()
        countdown.clear()


#########################################################颜色相关########################################################
def get_pixel_rgb(image, pixel_x, pixel_y):
    """
    获取图片中指定像素点的rgb颜色
    """
    rgb = image.pixelColor(pixel_x, pixel_y)
    return rgb.red(), rgb.green(), rgb.blue()


def find_most_similar_color(color_list, target_rgb):
    """
    在RGB颜色列表中找到与目标RGB颜色最相似的颜色
    """
    min_distance_sq = customConfig["distance_sq_threshold"]
    most_similar_color = -1

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
    判断像素点rgb是否符合要求
    """
    if ((min_rgb[0] - rgb_tolerance) <= pixel_rgb[0] <= (max_rgb[0] + rgb_tolerance) and
            (min_rgb[1] - rgb_tolerance) <= pixel_rgb[1] <= (max_rgb[1] + rgb_tolerance) and
            (min_rgb[2] - rgb_tolerance) <= pixel_rgb[2] <= (max_rgb[2] + rgb_tolerance)):
        return True
    else:
        return False


def resource_path(relative_path):
    """
    使得打包后的环境和原始的开发环境，都能正确地定位到项目的资源文件
    """
    base_path = getattr(sys, '_MEIPASS', None)
    if not base_path:
        base_path = os.path.abspath(os.path.dirname(__file__))
    abs_path = os.path.join(base_path, relative_path)
    return os.path.normpath(abs_path)


def close():
    app.quit()
    sys.exit(666)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

# pyinstaller --onefile --noconsole --add-data "resource;resource" --icon=resource/icon.ico Main.py
