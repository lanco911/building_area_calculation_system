import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication, QInputDialog, QHBoxLayout, QLabel, QComboBox, QScrollArea, QGroupBox, QLineEdit
from PyQt5.QtCore import Qt

class ApportionmentModelView(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.models = []  # 用于存储所有模型

    def initUI(self):
        # 创建主垂直布局
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)  # 设置布局的边距
        self.setLayout(self.main_layout)

        # 添加新模型按钮
        add_button = QPushButton("✚ 添加新分摊模型")
        add_button.clicked.connect(self.add_new_model)
        add_button.setFixedSize(140, 40) # 设置按钮的最大宽度

        # 将按钮添加到布局中，并设置对齐方式
        self.main_layout.addWidget(add_button, 0, Qt.AlignLeft | Qt.AlignTop)
        
        # 创建滚动区域来容纳所有模型
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True) # 设置滚动区域可以调整大小
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)  # 设置滚动区域无边框
        self.scroll_content = QWidget() # 创建滚动内容
        self.scroll_layout = QHBoxLayout(self.scroll_content) # 创建滚动布局
        self.scroll_layout.setAlignment(Qt.AlignLeft)  # 设置左对齐
        self.scroll_layout.setSpacing(10)  # 设置模型之间的间距
        self.scroll_area.setWidget(self.scroll_content) # 设置滚动区域的内容
        self.main_layout.addWidget(self.scroll_area) # 将滚动区域添加到主布局中

        # 设置窗口标题和大小
        self.setWindowTitle('共有建筑面积分配模型设置')
        self.setGeometry(300, 300, 1000, 600)  # 设置窗口大小

    def add_new_model(self):
        # 创建自定义的 QInputDialog
        dialog = QInputDialog(self)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setWindowTitle('添加新模型')
        dialog.setLabelText('请输入新分摊模型名称:')
        dialog.resize(300, 250)  # 设置对话框的大小
        
        # 获取对话框中的文本输入框
        line_edit = dialog.findChild(QLineEdit)
        if line_edit:
            line_edit.setMinimumHeight(30)  # 设置输入框的最小高度
        
        # 显示对话框并获取结果
        ok = dialog.exec_()
        model_name = dialog.textValue()

        if ok and model_name:
            # 创建新的模型控件
            model_widget = QGroupBox()
            model_layout = QVBoxLayout(model_widget)
            model_layout.setSpacing(5)  # 减小控件之间的垂直间距

            # 创建水平布局用于放置模型名称标签和删除按钮
            name_layout = QHBoxLayout()
            name_layout.setContentsMargins(0, 5, 0, 0)  # 设置上边距为5像素

            # 添加模型名称标签
            name_label = QLabel(f"{model_name} - 分摊")
            name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 设置标签左对齐和垂直居中
            name_label.setStyleSheet("font-weight: bold; font-size: 20px;")  # 设置字体加粗并增大字体大小
            name_label.setFixedHeight(30)  # 设置固定高度以适应更大的字体
            name_layout.addWidget(name_label)

            # 添加删除模型按钮
            delete_button = QPushButton("删除")
            delete_button.clicked.connect(lambda: self.delete_model(model_widget))
            delete_button.setFixedSize(50, 25)  # 设置按钮大小
            name_layout.addWidget(delete_button, 0, Qt.AlignRight)

            # 将水平布局添加到模型布局中
            model_layout.addLayout(name_layout)

            # 添加应分摊共有建筑部位选择
            label = QLabel("应分摊共有建筑部位")
            label.setFixedHeight(20)  # 设置标签的固定高度为20像素
            model_layout.addWidget(label)
            c_combo = QComboBox()
            c_combo.setFixedHeight(30)  # 将QComboBox的高度设置为25像素，略高于之前的默认值
            c_combo.addItem("选择数据...")
            model_layout.addWidget(c_combo)

            # 添加参与分摊单元选择
            label = QLabel("参与分摊单元")
            label.setFixedHeight(20)  # 将标签高度设置为20像素
            model_layout.addWidget(label)
            h_combo = QComboBox()
            h_combo.setFixedHeight(30)  # 将QComboBox的高度设置为30像素
            h_combo.addItem("选择数据...")
            model_layout.addWidget(h_combo)

            #添加上一级分摊系数输入
            label = QLabel("上一级分摊系数")
            label.setFixedHeight(20)  # 将标签高度设置为20像素
            model_layout.addWidget(label)
            input_field = QLineEdit()
            input_field.setFixedHeight(30)  # 将QLineEdit的高度设置为30像素
            input_field.setPlaceholderText("请输入分摊系数")  # 添加占位符文本
            model_layout.addWidget(input_field)

            # 添加计算分摊系数按钮
            calc_button = QPushButton("计算分摊系数")
            calc_button.setFixedSize(100, 40)  # 设置按钮宽度为120像素，高度保持30像素
            model_layout.addWidget(calc_button)

            # 添加计算结果显示标签
            result_label = QLabel("分摊系数")
            result_label.setFixedHeight(20)  # 设置标签高度为20像素
            model_layout.addWidget(result_label)

            # 添加计算结果显示文本框
            result_display = QLineEdit()
            result_display.setFixedHeight(30)  # 设置文本框高度为30像素
            result_display.setReadOnly(True)  # 设置为只读，防止用户修改
            result_display.setPlaceholderText("本级分摊系数结果将显示在这里")
            model_layout.addWidget(result_display)

            # 添加分摊说明
            explanation = QLabel("分摊说明:\n应分摊的共有建筑部位：未选择\n参加分摊的户名称：未选择")
            model_layout.addWidget(explanation)
            

            # 设置固定宽度和高度以确保横向排列时的一致性
            model_widget.setFixedSize(250, 450)  # 调整大小使其更紧凑

            # 将新模型添加到滚动区域
            self.scroll_layout.addWidget(model_widget)
            self.models.append(model_widget)

    def delete_model(self, model_widget):
        # 从布局中移除并删除指定的模型控件
        self.scroll_layout.removeWidget(model_widget)
        self.models.remove(model_widget)
        model_widget.deleteLater()

# 用于测试的代码
if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = ApportionmentModelView()
    view.show()
    sys.exit(app.exec_())
