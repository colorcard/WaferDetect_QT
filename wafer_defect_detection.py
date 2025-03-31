import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QComboBox, QStatusBar, QLineEdit, QFormLayout, QCheckBox
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt


class WatermarkLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置图片区域内显示的水印文字
        self.watermark_text = "湘潭大学COLORCARD"

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.pixmap() is not None:
            painter = QPainter(self)
            # 采用柔和的深灰水印效果
            painter.setPen(QColor(100, 100, 100, 150))
            painter.setFont(QFont("微软雅黑", 22, QFont.Bold))
            margin = 10
            text_rect = painter.fontMetrics().boundingRect(self.watermark_text)
            x = self.width() - text_rect.width() - margin
            y = self.height() - margin
            painter.drawText(x, y, self.watermark_text)


class WaferDefectDetectionDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('晶圆切割缺陷检测 Demo')
        self.setGeometry(100, 100, 900, 600)

        # 设置状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 创建中央窗口及主布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)

        # 左侧区域：图片展示区域，采用传统稳重的配色
        self.image_label = WatermarkLabel('图片展示区域')
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: #FFFFFF;
            border: 2px solid #CCCCCC;
            border-radius: 10px;
            min-width: 400px;
            min-height: 400px;
        """)
        main_layout.addWidget(self.image_label, 2)

        # 右侧区域：按钮、模型选择、URL输入及检测结果显示区
        control_layout = QVBoxLayout()

        # 上传图像和上传模型按钮区域
        button_layout = QHBoxLayout()
        self.upload_button = QPushButton('上传图像')
        self.upload_button.clicked.connect(self.upload_image)
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #005792;
                color: #FFFFFF;
                border: none;
                border-radius: 15px;
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #004466;
            }
            QPushButton:pressed {
                background-color: #002f3c;
            }
        """)
        button_layout.addWidget(self.upload_button)

        self.upload_model_button = QPushButton('上传模型')
        self.upload_model_button.clicked.connect(self.upload_model)
        self.upload_model_button.setStyleSheet("""
            QPushButton {
                background-color: #005792;
                color: #FFFFFF;
                border: none;
                border-radius: 15px;
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #004466;
            }
            QPushButton:pressed {
                background-color: #002f3c;
            }
        """)
        button_layout.addWidget(self.upload_model_button)
        control_layout.addLayout(button_layout)

        # 开始检测按钮区域
        self.detect_button = QPushButton('开始检测')
        self.detect_button.clicked.connect(self.start_detection)
        self.detect_button.setStyleSheet("""
            QPushButton {
                background-color: #005792;
                color: #FFFFFF;
                border: none;
                border-radius: 15px;
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #004466;
            }
            QPushButton:pressed {
                background-color: #002f3c;
            }
        """)
        control_layout.addWidget(self.detect_button)

        # 复选框区域：选择是否使用远程API模型
        self.remote_api_checkbox = QCheckBox("使用远程API模型")
        control_layout.addWidget(self.remote_api_checkbox)
        self.remote_api_checkbox.stateChanged.connect(self.on_remote_api_changed)

        # 模型选择下拉列表（仅本地模型使用时显示）
        self.model_selection = QComboBox()
        self.model_selection.addItems(["模型1", "模型2", "模型3"])
        self.model_selection.setStyleSheet("""
            background-color: #FFFFFF;
            padding: 8px;
            border: 1px solid #CCCCCC;
            border-radius: 5px;
            font-size: 16px;
            color: #393E46;
        """)
        control_layout.addWidget(self.model_selection)

        # URL输入区域：创建一个独立的标签及输入框
        self.form_layout = QFormLayout()
        self.model_url_label = QLabel("模型URL:")
        self.model_url_label.setStyleSheet("font-size: 16px; color: #393E46;")
        self.model_url_input = QLineEdit()
        self.model_url_input.setPlaceholderText("输入远程API模型的URL")
        self.model_url_input.setEnabled(False)
        # 添加标签和输入框
        self.form_layout.addRow(self.model_url_label, self.model_url_input)
        # 默认情况隐藏整个行
        self.model_url_label.hide()
        self.model_url_input.hide()
        control_layout.addLayout(self.form_layout)

        # 检测结果显示区域
        self.result_label = QLabel('检测结果将在此处显示')
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("""
            background-color: #F0F0F0;
            border: 2px solid #005792;
            border-radius: 10px;
            padding: 10px;
        """)
        control_layout.addWidget(self.result_label)

        control_layout.addStretch()
        main_layout.addLayout(control_layout, 1)

        self.image_path = ''

        # 全局样式设置：传统、稳重的配色方案
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F0F0F0;
            }
            QWidget {
                font-family: "微软雅黑", sans-serif;
                color: #393E46;
            }
            QLineEdit {
                background-color: #FFFFFF;
                padding: 6px;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                font-size: 16px;
                color: #393E46;
            }
            QLabel {
                font-size: 18px;
            }
            QCheckBox {
                font-size: 16px;
            }
        """)

        # 全局水印（右下角）
        self.global_watermark = QLabel("湘潭大学COLORCARD", self.central_widget)
        self.global_watermark.setStyleSheet("""
            color: #222831;
            font-size: 20px;
            font-family: "微软雅黑";
            font-weight: bold;
        """)
        self.global_watermark.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.global_watermark.adjustSize()
        self.position_watermark()

    def on_remote_api_changed(self, state):
        if state == Qt.Checked:
            self.model_url_label.show()
            self.model_url_input.show()
            self.model_url_input.setEnabled(True)
            self.model_selection.hide()
        else:
            self.model_url_label.hide()
            self.model_url_input.hide()
            self.model_url_input.setEnabled(False)
            self.model_selection.show()

    def position_watermark(self):
        margin = 10
        cw_size = self.central_widget.size()
        wm_size = self.global_watermark.size()
        x = cw_size.width() - wm_size.width() - margin
        y = cw_size.height() - wm_size.height() - margin
        self.global_watermark.move(x, y)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_watermark()

    def upload_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(
            self, "选择图像文件", "", "图片文件 (*.jpg *.png *.jpeg)", options=options
        )
        if file_name:
            self.image_path = file_name
            pixmap = QPixmap(file_name)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
            self.status_bar.showMessage("图像上传成功", 3000)

    def upload_model(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(
            self, "选择模型文件", "", "模型文件 (*.h5 *.pth *.model)", options=options
        )
        if file_name:
            model_name = file_name.split("/")[-1]
            if model_name not in [self.model_selection.itemText(i) for i in range(self.model_selection.count())]:
                self.model_selection.addItem(model_name)
                self.status_bar.showMessage(f"模型 {model_name} 上传成功，并已添加至选择列表", 3000)
            else:
                self.status_bar.showMessage(f"模型 {model_name} 已存在于选择列表中", 3000)

    def start_detection(self):
        if self.remote_api_checkbox.isChecked():
            model_url = self.model_url_input.text().strip()
            if model_url:
                self.result_label.setText(f'使用远程API模型 {model_url} 进行检测 (Demo 模式)')
                self.result_label.setStyleSheet("""
                    background-color: #F0F0F0;
                    border: 2px solid #005792;
                    border-radius: 10px;
                    padding: 10px;
                """)
                self.status_bar.showMessage(f"开始使用远程API模型 {model_url} 进行检测", 3000)
            else:
                self.result_label.setText('请填写远程API的URL')
                self.result_label.setStyleSheet("""
                    background-color: #F0F0F0;
                    border: 2px solid #393E46;
                    border-radius: 10px;
                    padding: 10px;
                """)
                self.status_bar.showMessage("错误：请填写远程API的URL！", 3000)
        elif not self.image_path:
            self.result_label.setText('请先上传图像')
            self.result_label.setStyleSheet("""
                background-color: #F0F0F0;
                border: 2px solid #393E46;
                border-radius: 10px;
                padding: 10px;
            """)
            self.status_bar.showMessage("错误：请先上传图像！", 3000)
        else:
            selected_model = self.model_selection.currentText()
            self.result_label.setText(f'使用本地模型 {selected_model} 进行检测 (Demo 模式)')
            self.result_label.setStyleSheet("""
                background-color: #F0F0F0;
                border: 2px solid #005792;
                border-radius: 10px;
                padding: 10px;
            """)
            self.status_bar.showMessage(f"开始使用本地模型 {selected_model} 进行检测", 3000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WaferDefectDetectionDemo()
    window.show()
    sys.exit(app.exec_())