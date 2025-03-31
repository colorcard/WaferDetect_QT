import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, \
    QFileDialog, QComboBox
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt


class WaferDefectDetectionDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('晶圆切割缺陷检测 Demo')
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.setStyleSheet("""
            QWidget {
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 18px;
                color: #333;
            }
            QComboBox {
                padding: 10px;
                font-size: 16px;
            }
        """)

        self.button_layout = QHBoxLayout()

        self.upload_button = QPushButton('上传图像')
        self.upload_button.clicked.connect(self.upload_image)
        self.button_layout.addWidget(self.upload_button)

        self.detect_button = QPushButton('开始检测')
        self.detect_button.clicked.connect(self.start_detection)
        self.button_layout.addWidget(self.detect_button)

        self.layout.addLayout(self.button_layout)

        self.image_label = QLabel('在此处显示图像')
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.result_label = QLabel('检测结果将显示在此处')
        self.result_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.result_label)

        self.model_selection = QComboBox()
        self.model_selection.addItems(["模型1", "模型2", "模型3"])
        self.layout.addWidget(self.model_selection)

        self.image_path = ''

    def upload_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "选择图像文件", "", "图片文件 (*.jpg *.png *.jpeg)",
                                                   options=options)
        if file_name:
            self.image_path = file_name
            pixmap = QPixmap(file_name)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))

    def start_detection(self):
        if not self.image_path:
            self.result_label.setText('请先上传图像')
            return
        selected_model = self.model_selection.currentText()
        self.result_label.setText(f'使用模型 {selected_model} 进行检测 (Demo，不进行实际检测)')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WaferDefectDetectionDemo()
    window.show()
    sys.exit(app.exec_())