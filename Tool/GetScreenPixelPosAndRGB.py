import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer

# 获取主屏幕上点击位置像素点的坐标和RGB值
class PrimaryScreenMouseTracker(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.Tool |  # 隐藏任务栏图标
            Qt.WindowType.FramelessWindowHint |  # 无边框
            Qt.WindowType.WindowStaysOnTopHint  # 始终顶层
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 全透明背景

        screen_size = app.primaryScreen().size()
        self.label = QLabel("左键点击屏幕任意位置输出坐标和RGB值，右键退出程序", self)
        self.label.setFont(QFont("楷体", 20, QFont.Weight.Bold))
        self.label.setStyleSheet("""
            color: #FF0000;
            background-color: rgba(0, 0, 0, 0.01);
        """)
        self.label.setFixedSize(screen_size.width(), screen_size.height())
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        QTimer.singleShot(5000, self.clear_tip_text)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            global_pos = event.globalPosition()
            x, y = int(global_pos.x()), int(global_pos.y())
            pixel = app.primaryScreen().grabWindow(0, x, y, 1, 1)
            rgb = pixel.toImage().pixelColor(0, 0)
            print(f"XY=({x}, {y}), RGB=({rgb.red()}, {rgb.green()}, {rgb.blue()})")
            event.accept()
        else:
            app.quit()
            sys.exit(666)

    def clear_tip_text(self):
        self.label.setText("")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tracker = PrimaryScreenMouseTracker()
    tracker.move(0, 0)
    tracker.show()
    sys.exit(app.exec())
