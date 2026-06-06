"""
🍅 番茄钟 - Pomodoro Timer
简约现代风格桌面番茄钟应用
基于 PySide6 (Qt for Python) 构建
"""

import sys
import math
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect, QSizePolicy
)
from PySide6.QtCore import (
    Qt, QTimer, QRectF, QPointF, QPropertyAnimation, QEasingCurve
)
from PySide6.QtGui import (
    QPainter, QPen, QColor, QFont, QBrush, QLinearGradient,
    QRadialGradient, QPainterPath, QCursor
)

# ─── 配色方案 ────────────────────────────────────────────────
COLORS = {
    "work": {
        "primary": "#E74C3C",
        "gradient_start": "#FF6B6B",
        "gradient_end": "#C0392B",
        "bg": "#1A1A2E",
        "ring_bg": "#2D2D44",
        "text": "#FFFFFF",
        "label": "🍅 专注工作",
    },
    "short_break": {
        "primary": "#2ECC71",
        "gradient_start": "#55E6A0",
        "gradient_end": "#27AE60",
        "bg": "#1A1A2E",
        "ring_bg": "#2D2D44",
        "text": "#FFFFFF",
        "label": "☕ 短暂休息",
    },
    "long_break": {
        "primary": "#3498DB",
        "gradient_start": "#5DADE2",
        "gradient_end": "#2E86C1",
        "bg": "#1A1A2E",
        "ring_bg": "#2D2D44",
        "text": "#FFFFFF",
        "label": "🌿 长时休息",
    },
}

# ─── 时间配置（秒）─────────────────────────────────────────
TIME_CONFIG = {
    "work": 25 * 60,
    "short_break": 5 * 60,
    "long_break": 15 * 60,
}


class CircularTimer(QWidget):
    """圆形进度条控件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(260, 260)
        self._progress = 1.0
        self._time_text = "25:00"
        self._mode_color = QColor(COLORS["work"]["primary"])

    def set_progress(self, progress: float, time_text: str, color: QColor):
        self._progress = max(0.0, min(1.0, progress))
        self._time_text = time_text
        self._mode_color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        side = min(self.width(), self.height())
        center = QPointF(self.width() / 2, self.height() / 2)
        radius = side / 2 - 20

        # ── 背景圆环 ──
        pen_bg = QPen(QColor(COLORS["work"]["ring_bg"]), 10, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(
            QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2),
            int(0 * 16), int(360 * 16)
        )

        # ── 进度圆环（渐变色）──
        if self._progress > 0:
            gradient = QLinearGradient(
                QPointF(center.x(), center.y() - radius),
                QPointF(center.x(), center.y() + radius)
            )
            color_start = QColor(self._mode_color)
            color_start.setAlpha(255)
            color_end = QColor(self._mode_color).darker(130)
            color_end.setAlpha(255)
            gradient.setColorAt(0.0, color_start)
            gradient.setColorAt(1.0, color_end)

            pen_progress = QPen(QBrush(gradient), 10, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen_progress)
            span_angle = int(-self._progress * 360 * 16)
            start_angle = int(90 * 16)
            painter.drawArc(
                QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2),
                start_angle, span_angle
            )

            # ── 进度圆点 ──
            angle = math.radians(90 - self._progress * 360)
            dot_x = center.x() + radius * math.cos(angle)
            dot_y = center.y() - radius * math.sin(angle)
            painter.setPen(Qt.NoPen)
            dot_gradient = QRadialGradient(QPointF(dot_x, dot_y), 8)
            dot_gradient.setColorAt(0, QColor(255, 255, 255, 220))
            dot_gradient.setColorAt(1, QColor(255, 255, 255, 0))
            painter.setBrush(dot_gradient)
            painter.drawEllipse(QPointF(dot_x, dot_y), 8, 8)

        # ── 时间文字 ──
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Segoe UI", 48, QFont.Bold)
        painter.setFont(font)
        text_rect = QRectF(0, center.y() - 40, self.width(), 60)
        painter.drawText(text_rect, Qt.AlignCenter, self._time_text)

        # ── 底部小标签 ──
        painter.setPen(QColor(180, 180, 200, 180))
        small_font = QFont("Segoe UI", 11)
        painter.setFont(small_font)
        sub_rect = QRectF(0, center.y() + 25, self.width(), 25)
        painter.drawText(sub_rect, Qt.AlignCenter, "剩余时间")

        painter.end()


class ModeButton(QPushButton):
    """模式选择按钮"""

    def __init__(self, text: str, color: str, parent=None):
        super().__init__(text, parent)
        self._base_color = color
        self._hover = False
        self.setFixedHeight(36)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self._update_style(False)

    def _update_style(self, active: bool):
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self._base_color};
                    color: #FFFFFF;
                    border: none;
                    border-radius: 18px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 0 20px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: #8888AA;
                    border: 2px solid #3D3D5C;
                    border-radius: 18px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 0 20px;
                }}
                QPushButton:hover {{
                    border-color: {self._base_color};
                    color: {self._base_color};
                }}
            """)

    def set_active(self, active: bool):
        self._update_style(active)


class ControlButton(QPushButton):
    """控制按钮（开始/暂停/重置）"""

    def __init__(self, text: str, icon: str, color: str, parent=None):
        super().__init__(f"{icon}  {text}", parent)
        self._color = color
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFixedHeight(48)
        self.setFixedWidth(140)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #FFFFFF;
                border: none;
                border-radius: 24px;
                font-size: 15px;
                font-weight: bold;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {QColor(color).lighter(115).name()};
            }}
            QPushButton:pressed {{
                background-color: {QColor(color).darker(110).name()};
            }}
        """)


class PomodoroApp(QMainWindow):
    """番茄钟主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(380, 540)

        # ── 状态 ──
        self._mode = "work"
        self._time_left = TIME_CONFIG["work"]
        self._total_time = TIME_CONFIG["work"]
        self._is_running = False
        self._pomodoro_count = 0

        # ── 定时器 ──
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._update_timer)

        # ── 拖拽 ──
        self._drag_pos = None

        self._init_ui()
        self._center_window()

    def _init_ui(self):
        # ── 主容器 ──
        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet("""
            #container {
                background-color: #1A1A2E;
                border-radius: 20px;
            }
        """)
        self.setCentralWidget(container)

        # 阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 10)
        container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(8)

        # ── 顶部关闭按钮 + 标题 ──
        top_bar = QHBoxLayout()
        title_label = QLabel("🍅 番茄钟")
        title_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 18px;
            font-weight: bold;
        """)
        top_bar.addWidget(title_label)
        top_bar.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666688;
                border: none;
                border-radius: 16px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #E74C3C;
                color: white;
            }
        """)
        close_btn.clicked.connect(self.close)
        top_bar.addWidget(close_btn)
        layout.addLayout(top_bar)

        # ── 模式选择 ──
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(8)

        self._btn_work = ModeButton("专注", COLORS["work"]["primary"])
        self._btn_short = ModeButton("短休", COLORS["short_break"]["primary"])
        self._btn_long = ModeButton("长休", COLORS["long_break"]["primary"])

        self._btn_work.clicked.connect(lambda: self._switch_mode("work"))
        self._btn_short.clicked.connect(lambda: self._switch_mode("short_break"))
        self._btn_long.clicked.connect(lambda: self._switch_mode("long_break"))

        self._btn_work.set_active(True)

        mode_layout.addStretch()
        mode_layout.addWidget(self._btn_work)
        mode_layout.addWidget(self._btn_short)
        mode_layout.addWidget(self._btn_long)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # ── 圆形计时器 ──
        timer_container = QHBoxLayout()
        timer_container.addStretch()
        self._circular_timer = CircularTimer()
        timer_container.addWidget(self._circular_timer)
        timer_container.addStretch()
        layout.addLayout(timer_container)

        # ── 模式标签 ──
        self._mode_label = QLabel(COLORS["work"]["label"])
        self._mode_label.setAlignment(Qt.AlignCenter)
        self._mode_label.setStyleSheet("""
            color: #E74C3C;
            font-size: 16px;
            font-weight: bold;
        """)
        layout.addWidget(self._mode_label)

        # ── 番茄计数 ──
        self._count_label = QLabel(self._format_count())
        self._count_label.setAlignment(Qt.AlignCenter)
        self._count_label.setStyleSheet("""
            color: #8888AA;
            font-size: 13px;
        """)
        layout.addWidget(self._count_label)

        # ── 控制按钮 ──
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)

        self._btn_start = ControlButton("开始", "▶", COLORS["work"]["primary"])
        self._btn_reset = ControlButton("重置", "↺", "#3D3D5C")

        self._btn_start.clicked.connect(self._toggle_timer)
        self._btn_reset.clicked.connect(self._reset_timer)

        btn_layout.addStretch()
        btn_layout.addWidget(self._btn_start)
        btn_layout.addWidget(self._btn_reset)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # ── 底部提示 ──
        tip_label = QLabel("拖拽窗口移动 · 点击模式切换")
        tip_label.setAlignment(Qt.AlignCenter)
        tip_label.setStyleSheet("color: #444466; font-size: 11px;")
        layout.addWidget(tip_label)

        # 初始显示
        self._refresh_display()

    def _center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _format_time(self, seconds: int) -> str:
        m, s = divmod(seconds, 60)
        return f"{m:02d}:{s:02d}"

    def _format_count(self) -> str:
        tomatoes = "🍅" * min(self._pomodoro_count, 12)
        if self._pomodoro_count > 12:
            tomatoes += f" +{self._pomodoro_count - 12}"
        text = f"已完成 {self._pomodoro_count} 个番茄"
        if self._pomodoro_count > 0:
            text = f"{tomatoes}  {text}"
        return text

    def _refresh_display(self):
        progress = self._time_left / self._total_time if self._total_time > 0 else 0
        color = QColor(COLORS[self._mode]["primary"])
        self._circular_timer.set_progress(progress, self._format_time(self._time_left), color)

    def _switch_mode(self, mode: str):
        if self._is_running:
            self._timer.stop()
            self._is_running = False

        self._mode = mode
        self._time_left = TIME_CONFIG[mode]
        self._total_time = TIME_CONFIG[mode]

        # 更新按钮状态
        self._btn_work.set_active(mode == "work")
        self._btn_short.set_active(mode == "short_break")
        self._btn_long.set_active(mode == "long_break")

        # 更新标签颜色
        self._mode_label.setText(COLORS[mode]["label"])
        self._mode_label.setStyleSheet(f"""
            color: {COLORS[mode]['primary']};
            font-size: 16px;
            font-weight: bold;
        """)

        # 更新开始按钮颜色
        self._btn_start.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS[mode]['primary']};
                color: #FFFFFF;
                border: none;
                border-radius: 24px;
                font-size: 15px;
                font-weight: bold;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {QColor(COLORS[mode]['primary']).lighter(115).name()};
            }}
            QPushButton:pressed {{
                background-color: {QColor(COLORS[mode]['primary']).darker(110).name()};
            }}
        """)
        self._btn_start.setText("▶  开始")

        self._refresh_display()

    def _toggle_timer(self):
        if self._is_running:
            # 暂停
            self._timer.stop()
            self._is_running = False
            self._btn_start.setText("▶  继续")
        else:
            # 开始
            self._timer.start()
            self._is_running = True
            self._btn_start.setText("⏸  暂停")

    def _reset_timer(self):
        self._timer.stop()
        self._is_running = False
        self._time_left = TIME_CONFIG[self._mode]
        self._total_time = TIME_CONFIG[self._mode]
        self._btn_start.setText("▶  开始")
        self._refresh_display()

    def _update_timer(self):
        if self._time_left > 0:
            self._time_left -= 1
            self._refresh_display()
        else:
            self._timer_finished()

    def _timer_finished(self):
        self._timer.stop()
        self._is_running = False

        # 播放提示音
        self._play_sound()

        if self._mode == "work":
            self._pomodoro_count += 1
            self._count_label.setText(self._format_count())

            # 每4个番茄 -> 长休息，否则 -> 短休息
            if self._pomodoro_count % 4 == 0:
                self._switch_mode("long_break")
            else:
                self._switch_mode("short_break")
        else:
            # 休息结束 -> 回到工作模式
            self._switch_mode("work")

    def _play_sound(self):
        """使用 QApplication 的 beep 播放系统提示音"""
        try:
            QApplication.beep()
        except Exception:
            pass

    # ── 窗口拖拽 ──
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # 全局字体
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = PomodoroApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
