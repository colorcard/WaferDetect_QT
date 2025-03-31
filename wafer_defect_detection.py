import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QComboBox, QStatusBar, QLineEdit, QFormLayout, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea, QFrame, QLayout, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QRect, QSize, QPoint


# 自定义 FlowLayout 类 (来源于 Qt 官方示例)
class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.itemList = []
        self.setSpacing(spacing)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(
                QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(
                QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        return y + lineHeight - rect.y()


# 自定义 ThumbnailLabel 类，用于显示缩略图及序号，在左上角绘制黑色序号
class ThumbnailLabel(QLabel):
    def __init__(self, parent=None, index=None):
        super().__init__(parent)
        self.index = index  # 序号
        # 不再自动缩放图片，确保不会因 setScaledContents 导致失真

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.index is not None:
            painter = QPainter(self)
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont("微软雅黑", 14, QFont.Bold))
            rect = QRect(0, 0, 30, 30)
            painter.fillRect(rect, QColor(255, 255, 255, 200))
            painter.drawText(rect, Qt.AlignCenter, str(self.index))


class WaferDefectDetectionDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('晶圆切割缺陷检测 Demo')
        self.setGeometry(100, 100, 950, 750)

        # 初始化图片路径列表
        self.image_paths = []

        # 设置状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 主布局：左右分栏，左侧用于预览和检测结果，右侧用于控制
        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 左侧布局
        left_layout = QVBoxLayout()

        # 创建滚动区域显示缩略图
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        preview_container = QWidget()
        # 使用自定义 FlowLayout 实现流式布局
        self.flow_layout = FlowLayout(preview_container, margin=5)
        preview_container.setLayout(self.flow_layout)
        self.scroll_area.setWidget(preview_container)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #FFFFFF;
                border: 2px solid #CCCCCC;
            }
        """)
        left_layout.addWidget(self.scroll_area, 1)

        # 检测结果表格
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["图片名称", "检测结果", "备注"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setStyleSheet("""
            QTableWidget {
                background-color: #E8F0FE;
                border: 2px solid #005792;
                font-size: 16px;
                color: #393E46;
            }
            QHeaderView::section {
                background-color: #005792;
                color: #FFFFFF;
                padding: 4px;
                border: none;
            }
        """)
        left_layout.addWidget(self.results_table, 1)
        main_layout.addLayout(left_layout, 2)

        # 右侧布局（控制区域）
        control_layout = QVBoxLayout()

        # 按钮区域：上传图像与上传模型
        button_layout = QHBoxLayout()
        self.upload_button = QPushButton('上传图像')
        self.upload_button.clicked.connect(self.upload_images)
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #005792;
                color: #FFFFFF;
                border: none;
                border-radius: 15px;
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover { background-color: #004466; }
            QPushButton:pressed { background-color: #002f3c; }
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
            QPushButton:hover { background-color: #004466; }
            QPushButton:pressed { background-color: #002f3c; }
        """)
        button_layout.addWidget(self.upload_model_button)
        control_layout.addLayout(button_layout)

        # 开始检测按钮
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
            QPushButton:hover { background-color: #004466; }
            QPushButton:pressed { background-color: #002f3c; }
        """)
        control_layout.addWidget(self.detect_button)

        # 保存结果按钮（检测完成后显示）
        self.save_results_button = QPushButton('保存结果')
        self.save_results_button.clicked.connect(self.save_results)
        self.save_results_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: #FFFFFF;
                border: none;
                border-radius: 15px;
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover { background-color: #218838; }
            QPushButton:pressed { background-color: #1E7E34; }
        """)
        self.save_results_button.setVisible(False)
        control_layout.addWidget(self.save_results_button)

        # 复选框：是否使用远程API模型
        self.remote_api_checkbox = QCheckBox("使用远程API模型")
        control_layout.addWidget(self.remote_api_checkbox)
        self.remote_api_checkbox.stateChanged.connect(self.on_remote_api_changed)

        # 模型选择下拉列表
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

        # URL输入区域
        self.form_layout = QFormLayout()
        self.model_url_label = QLabel("模型URL:")
        self.model_url_label.setStyleSheet("font-size: 16px; color: #393E46;")
        self.model_url_input = QLineEdit()
        self.model_url_input.setPlaceholderText("输入远程API模型的URL")
        self.model_url_input.setEnabled(False)
        self.form_layout.addRow(self.model_url_label, self.model_url_input)
        self.model_url_label.hide()
        self.model_url_input.hide()
        control_layout.addLayout(self.form_layout)

        control_layout.addStretch()
        main_layout.addLayout(control_layout, 1)

        self.setStyleSheet("""
            QMainWindow { background-color: #F0F0F0; }
            QWidget { font-family: "微软雅黑", sans-serif; color: #393E46; }
            QLineEdit { background-color: #FFFFFF; padding: 6px; border: 1px solid #CCCCCC; border-radius: 5px; font-size: 16px; color: #393E46; }
            QLabel { font-size: 18px; }
            QCheckBox { font-size: 16px; }
        """)

        # 在右下角重建全局水印
        self.global_watermark = QLabel("湘潭大学COLORCARD", central_widget)
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
        cw_size = self.centralWidget().size()
        wm_size = self.global_watermark.size()
        x = cw_size.width() - wm_size.width() - margin
        y = cw_size.height() - wm_size.height() - margin
        self.global_watermark.move(x, y)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_watermark()

    def upload_images(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        files, _ = QFileDialog.getOpenFileNames(self, "选择图像文件", "",
                                                "图片文件 (*.jpg *.png *.jpeg)", options=options)
        if files:
            self.image_paths = files
            while self.flow_layout.count():
                item = self.flow_layout.takeAt(0)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)
            for idx, path in enumerate(self.image_paths, start=1):
                thumb = ThumbnailLabel(index=idx)
                thumb.setFixedSize(120, 120)
                thumb.setStyleSheet("""
                    background-color: #FFFFFF;
                    border: 1px solid #CCCCCC;
                """)
                pixmap = QPixmap(path)
                # 使用 Qt.KeepAspectRatio 保持原始比例缩放图片（不失真）
                scaledPixmap = pixmap.scaled(thumb.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                thumb.setPixmap(scaledPixmap)
                thumb.setAlignment(Qt.AlignCenter)
                self.flow_layout.addWidget(thumb)
            self.status_bar.showMessage(f"共上传 {len(self.image_paths)} 张图像", 3000)

    def upload_image(self):
        self.upload_images()

    def upload_model(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "选择模型文件", "",
                                                   "模型文件 (*.h5 *.pth *.model)", options=options)
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
            if not model_url:
                self.status_bar.showMessage("错误：请填写远程API的URL！", 3000)
                return
            results = []
            for img in self.image_paths:
                result = f"远程检测结果 (Demo) - {img.split('/')[-1]}"
                results.append(result)
        else:
            if not self.image_paths:
                self.status_bar.showMessage("错误：请先上传图像！", 3000)
                return
            results = []
            for img in self.image_paths:
                result = f"本地检测结果 (Demo) - {img.split('/')[-1]}"
                results.append(result)

        num_images = len(self.image_paths)
        self.results_table.setRowCount(num_images)
        for i in range(num_images):
            image_name = self.image_paths[i].split('/')[-1]
            detection_result = results[i]
            remark = ""
            self.results_table.setItem(i, 0, QTableWidgetItem(image_name))
            self.results_table.setItem(i, 1, QTableWidgetItem(detection_result))
            self.results_table.setItem(i, 2, QTableWidgetItem(remark))
        self.status_bar.showMessage("检测完成", 3000)
        self.save_results_button.setVisible(True)

    def save_results(self):
        filename, _ = QFileDialog.getSaveFileName(self, "保存检测结果", "",
                                                  "CSV文件 (*.csv);;文本文件 (*.txt)")
        if filename:
            try:
                with open(filename, "w", encoding="utf-8-sig") as f:
                    f.write("图片名称,检测结果,备注\n")
                    row_count = self.results_table.rowCount()
                    col_count = self.results_table.columnCount()
                    for row in range(row_count):
                        row_data = []
                        for col in range(col_count):
                            item = self.results_table.item(row, col)
                            row_data.append(item.text() if item else "")
                        f.write(",".join(row_data) + "\n")
                self.status_bar.showMessage("结果已保存", 3000)
            except Exception as e:
                self.status_bar.showMessage(f"保存失败: {e}", 3000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WaferDefectDetectionDemo()
    window.show()
    sys.exit(app.exec_())