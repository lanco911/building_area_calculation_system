import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QApplication, 
                             QInputDialog, QHBoxLayout, QLabel, QComboBox, 
                             QScrollArea, QGroupBox, QLineEdit, QStyledItemDelegate,
                             QMessageBox, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFontMetrics

class CheckableComboBox(QComboBox):
    # 自定义的可勾选ComboBox类
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view().pressed.connect(self.handle_item_pressed)
        self.setModel(QStandardItemModel(self))
        self.setEditable(True)  # 设置为可编辑
        self.lineEdit().setReadOnly(True)  # 设置为只读，防止用户编辑
        self.setItemDelegate(QStyledItemDelegate())
        self.closeOnSelect = False

    def handle_item_pressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        self.check_items()

    def check_items(self):
        checkedItems = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                checkedItems.append(self.model().item(i).text())
        text = ", ".join(checkedItems)
        if self.lineEdit():
            self.lineEdit().setText(text)  # 直接设置文本，不使用 elidedText

    def addItem(self, text, data=None):
        item = QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

    def addItems(self, texts, datalist=None):
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)

    def currentData(self):
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                res.append(self.model().item(i).data())
        return res

class ApportionmentModelView(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.initUI()
        self.models = []

    def initUI(self):
        # 创建主垂直布局
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)  # 设置布局的边距
        self.setLayout(self.main_layout)

        # 添加模型按钮
        add_button = QPushButton("✚ 添加分摊模型")
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
        self.scroll_layout.setSpacing(10)  # 模型之间的间距
        self.scroll_area.setWidget(self.scroll_content) # 设置滚动区域的内容
        self.main_layout.addWidget(self.scroll_area) # 将滚动区域添加到主布局中

        # 创建底部按钮布局
        bottom_layout = QHBoxLayout()
        bottom_layout.setAlignment(Qt.AlignRight)  # 设置右对齐

        # 创建预览按钮
        preview_button = QPushButton("预览")
        preview_button.setFixedSize(100, 40)
        preview_button.clicked.connect(self.preview_models)
        bottom_layout.addWidget(preview_button)

        # 创建保存按钮
        save_button = QPushButton("保存")
        save_button.setFixedSize(100, 40)
        save_button.clicked.connect(self.save_models)
        bottom_layout.addWidget(save_button)

        # 将底部按钮布局添加到主布局
        self.main_layout.addLayout(bottom_layout)

        # 设置窗口标题和大小
        self.setWindowTitle('共有建筑面积分配模型设置')
        self.setGeometry(300, 300, 1000, 600)  # 设置窗口大小

    def add_new_model(self):
        # 获取分摊所属选项
        allocation_options = self.controller.get_allocation_options()
        
        if not allocation_options:
            QMessageBox.warning(self, "警告", "没有可用的分摊所属选项")
            return

        # 创建自定义的 QInputDialog
        dialog = QInputDialog(self)
        dialog.setWindowTitle('添加新模型')
        dialog.setLabelText('请选择分摊模型类型:')
        dialog.setComboBoxItems(allocation_options)
        dialog.setComboBoxEditable(False)
        dialog.resize(300, 200)

        # 显示对话框并获取结果
        if dialog.exec_():
            selected_option = dialog.textValue()
            allocation_tables = self.controller.get_allocation_tables(selected_option)

            if not allocation_tables:
                QMessageBox.warning(self, "警告", f"没有找到与 '{selected_option}' 相关的数据表")
                return

            # 创建新的模型控件
            model_widget = QGroupBox()
            model_layout = QVBoxLayout(model_widget)

            # 创建水平布局用于放置模型名称标签和删除按钮
            name_layout = QHBoxLayout()
            name_layout.setContentsMargins(0, 5, 0, 0)  # 设置上边距为5像素

            # 添加模型名称标签
            name_label = QLabel(f"{selected_option} - 分摊") 
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
            label.setFixedHeight(20)
            model_layout.addWidget(label)
            c_combo = CheckableComboBox()
            c_combo.setObjectName("c_combo")
            c_combo.setFixedHeight(30)
            c_combo.setMinimumWidth(200)  # 设置最小宽度
            c_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)  # 自动调整大小以适应内容
            c_combo.addItem("选择数据...")
            model_layout.addWidget(c_combo)

            # 添加参与分摊单元选择
            label = QLabel("参与分摊单元")
            label.setFixedHeight(20)
            model_layout.addWidget(label)
            h_combo = CheckableComboBox()
            h_combo.setObjectName("h_combo")
            h_combo.setFixedHeight(30)
            h_combo.setMinimumWidth(200)  # 设置最小宽度
            h_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)  # 自动调整大小以适应内容
            h_combo.addItem("选择数据...")
            model_layout.addWidget(h_combo)

            # 添加上一级分摊系数输入
            label = QLabel("上一级分摊系数")
            label.setFixedHeight(20)
            model_layout.addWidget(label)
            input_field = QLineEdit()
            input_field.setObjectName("input_field")  # 添加这行
            input_field.setFixedHeight(30)
            input_field.setPlaceholderText("请输入分摊系数")
            model_layout.addWidget(input_field)

            # 添加计算分摊系数按钮
            calc_button = QPushButton("计算分摊系数")
            calc_button.setFixedSize(100, 40)
            calc_button.clicked.connect(lambda: self.calculate_apportionment_coefficient(model_widget))
            model_layout.addWidget(calc_button)

            # 添加计算结果显示标签
            result_label = QLabel("分摊系数")
            result_label.setFixedHeight(20)
            model_layout.addWidget(result_label)

            # 添加计算结果显示文本框
            result_display = QLineEdit()
            result_display.setObjectName("result_display")  # 添加这行
            result_display.setFixedHeight(30)
            result_display.setReadOnly(True)
            result_display.setPlaceholderText("本级分摊系数结果将显示在这里")
            model_layout.addWidget(result_display)

            # 添加分摊说明
            explanation = QLabel("分摊说明:\n应分摊的共有建筑部位：未选择\n参加分摊的户名称：未选择")
            explanation.setObjectName("explanation")  # 添加这行
            model_layout.addWidget(explanation)
            

            # 设置固定宽度高度以确保横向排列时的一致性
            model_widget.setFixedSize(250, 450)  # 调整大小使其更紧凑

            # 将新模型添加到滚动区域，并设置在顶端左对齐
            self.scroll_layout.addWidget(model_widget, 0, Qt.AlignTop | Qt.AlignLeft)
            self.models.append(model_widget)

            # 更新应分摊共有建筑部位和参与分摊单元的数据
            self.update_combobox_data(c_combo, allocation_tables)
            self.update_combobox_data(h_combo, allocation_tables)

    def delete_model(self, model_widget):
        # 从布局中移除并删除指定的模型控件
        self.scroll_layout.removeWidget(model_widget)
        self.models.remove(model_widget)
        model_widget.deleteLater()

    def update_combobox_data(self, combobox, tables):
        combobox.clear()
        for table in tables:
            combobox.addItem(table)

    def preview_models(self):
        # 实现预览功能
        QMessageBox.information(self, "预览", "预览功能待实现")

    def save_models(self):
        # 实现保存功能
        QMessageBox.information(self, "保存", "保存功能待实现")

    def calculate_apportionment_coefficient(self, model_widget):
        # 获取所需的数据
        c_combo = model_widget.findChild(CheckableComboBox, "c_combo")
        h_combo = model_widget.findChild(CheckableComboBox, "h_combo")
        input_field = model_widget.findChild(QLineEdit, "input_field")
        result_display = model_widget.findChild(QLineEdit, "result_display")
        name_label = model_widget.findChildren(QLabel)[0]  # 获取第一个QLabel，假设它是名称标签

        if not all([c_combo, h_combo, input_field, result_display, name_label]):
            QMessageBox.warning(self, "错误", "无法找到所有必要的控件")
            return

        # 获取选中的数据表
        c_tables = c_combo.currentData()
        h_tables = h_combo.currentData()
        
        try:
            upper_coefficient = float(input_field.text() or 0)
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的上一级分摊系数")
            return

        # 获取模型类型
        model_type = name_label.text().split(' - ')[0]

        if not c_tables or not h_tables:
            QMessageBox.warning(self, "警告", "请选择应分摊共有建筑部位和参与分摊单元")
            return

        # 调用控制器方法计算分摊系数
        coefficient, error = self.controller.calculate_apportionment_coefficient(
            c_tables, h_tables, upper_coefficient, model_type
        )

        if error:
            QMessageBox.warning(self, "错误", error)
        else:
            # 显示计算结果，保留6位小数
            result_display.setText(f"{coefficient:.6f}")

            # 更新分摊说明
            explanation = model_widget.findChild(QLabel, "explanation")
            if explanation:
                explanation.setText(f"分摊说明:\n应分摊的共有建筑部位：{', '.join(c_tables)}\n参加分摊的户名称：{', '.join(h_tables)}")

# 用于测试的代码
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 创建一个模拟的 controller
    class MockController:
        def get_allocation_options(self):
            return ["选项1", "选项2", "选项3"]
        
        def get_allocation_tables(self, option):
            return [f"{option}_表1", f"{option}_表2", f"{option}_表3"]
    
    mock_controller = MockController()
    view = ApportionmentModelView(mock_controller)
    view.show()
    sys.exit(app.exec_())
