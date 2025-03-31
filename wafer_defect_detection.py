import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, \
    QFileDialog, QComboBox, QStatusBar
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt


class WatermarkLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置图片区域内显示的水印文字
        self.watermark_text = "湘潭大学COLORCARD"

    def paintEvent(self, event):
        # 先调用父类绘制图像
        super().paintEvent(event)
        if self.pixmap() is not None:
            painter = QPainter(self)
            # 设置水印颜色与透明度
            painter.setPen(QColor(150, 150, 150, 100))
            # 设置字体样式和大小
            painter.setFont(QFont("微软雅黑", 20))
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

        # 中央窗口及主布局（左右分栏）
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)

        # 左侧区域：图片展示（水印将绘制在图片上）
        self.image_label = WatermarkLabel('图片展示区域')
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: white;
            border: 2px solid #ccc;
            border-radius: 10px;
            min-width: 400px;
            min-height: 400px;
        """)
        main_layout.addWidget(self.image_label, 2)

        # 右侧区域：按钮、下拉菜单和检测结果
        control_layout = QVBoxLayout()

        # 第一行：上传图像和上传模型按钮
        button_layout = QHBoxLayout()
        self.upload_button = QPushButton('上传图像')
        self.upload_button.clicked.connect(self.upload_image)
        button_layout.addWidget(self.upload_button)

        self.upload_model_button = QPushButton('上传模型')
        self.upload_model_button.clicked.connect(self.upload_model)
        button_layout.addWidget(self.upload_model_button)

        control_layout.addLayout(button_layout)

        # 第二行：开始检测按钮
        self.detect_button = QPushButton('开始检测')
        self.detect_button.clicked.connect(self.start_detection)
        control_layout.addWidget(self.detect_button)

        # 第三行：模型选择下拉菜单
        self.model_selection = QComboBox()
        self.model_selection.addItems(["模型1", "模型2", "模型3"])
        control_layout.addWidget(self.model_selection)

        # 第四行：检测结果显示区域
        self.result_label = QLabel('检测结果将在此处显示')
        self.result_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.result_label)

        # 添加伸展空间，使控件靠上排列
        control_layout.addStretch()
        main_layout.addLayout(control_layout, 1)

        self.image_path = ''

        # 全局样式设置
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QWidget {
                font-family: "微软雅黑", sans-serif;
                color: #333;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 16px;
                background-color: white;
            }
            QLabel {
                font-size: 18px;
            }
        """)

        # 在软件页面添加全局水印
        self.global_watermark = QLabel("湘潭大学COLORCARD", self.central_widget)
        self.global_watermark.setStyleSheet("""
            color: rgba(150, 150, 150, 100);
            font-size: 20px;
            font-family: "微软雅黑";
        """)
        # 让水印不响应鼠标事件
        self.global_watermark.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.global_watermark.adjustSize()
        self.position_watermark()

    def position_watermark(self):
        margin = 10
        # 将水印位置设在中央窗口右下角
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
        if not self.image_path:
            self.result_label.setText('请先上传图像')
            self.status_bar.showMessage("错误：请先上传图像！", 3000)
            return
        selected_model = self.model_selection.currentText()
        self.result_label.setText(f'使用模型 {selected_model} 进行检测 (Demo 模式)')
        self.status_bar.showMessage(f"开始使用 {selected_model} 进行检测", 3000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WaferDefectDetectionDemo()
    window.show()
    sys.exit(app.exec_())