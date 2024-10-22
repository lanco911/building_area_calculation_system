import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication
from PyQt5.QtCore import Qt

class ApportionmentModelView(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 创建主垂直布局
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)  # 设置布局的边距
        self.setLayout(self.main_layout)

        # 添加新模型按钮
        add_button = QPushButton("+ 添加新模型")
        add_button.clicked.connect(self.add_new_model)
        add_button.setMaximumWidth(120)  # 设置按钮的最大宽度

        # 将按钮添加到布局中，并设置对齐方式
        self.main_layout.addWidget(add_button, 0, Qt.AlignLeft | Qt.AlignTop)
        
        # 添加弹性空间
        self.main_layout.addStretch(1)

        # 设置窗口标题和大小
        self.setWindowTitle('共有建筑面积分配模型设置')
        self.setGeometry(300, 300, 1000, 600)  # 设置窗口大小

    def add_new_model(self):
        # 添加新模型的逻辑
        pass

# 用于测试的代码
if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = ApportionmentModelView()
    view.show()
    sys.exit(app.exec_())
