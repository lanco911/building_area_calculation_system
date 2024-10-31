# -*- coding: utf-8 -*-

"""
这是一个用于建筑面积分摊模型的视图模块。主要功能包括：
1. 创建和管理多个分摊模型
2. 支持选择分摊对象和参与单元
3. 计算分摊系数
4. 预览和保存分摊结果

主要包含两个核心类：
- CheckableComboBox: 可多选的下拉框组件
- ApportionmentModelView: 分摊模型的主视图界面
"""

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QApplication, 
                             QInputDialog, QHBoxLayout, QLabel, QComboBox, 
                             QScrollArea, QGroupBox, QLineEdit, QStyledItemDelegate,
                             QMessageBox, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFontMetrics

class CheckableComboBox(QComboBox):
    """
    自定义的可多选下拉框组件
    
    主要用途：
    - 在分摊模型中选择应分摊的共有建筑部位
    - 选择参与分摊的单元
    
    特点：
    - 支持多选功能
    - 显示已选项的文本���表
    - 保持选择状态
    """
    # 自定义的可勾选ComboBox
    def __init__(self, *args, **kwargs):
        """
        初始化可多选下拉框
        设置基本属性和事件连接
        """
        super().__init__(*args, **kwargs)
        self.view().pressed.connect(self.handle_item_pressed)
        self.setModel(QStandardItemModel(self))
        self.setEditable(True)  # 设置为可编辑
        self.lineEdit().setReadOnly(True)  # 设置为只读，防止用户编辑
        self.setItemDelegate(QStyledItemDelegate())
        self.closeOnSelect = False

    def handle_item_pressed(self, index):
        """
        处理项目点击事件
        当用户点击项目时切换其选中状态
        """
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
            self.lineEdit().setText(text)  # 直���设置文本，不使用 elidedText

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
    """
    分摊模型的主视图界面
    
    主要功能：
    1. 创建和管理多个分摊模型
    2. 提供分摊模型的添加、删除功能
    3. 支持计算分摊系数
    4. 提供预览和保存功能
    
    使用场景：
    - 在建筑面积分摊系统中作为主要的模型配置界面
    - 与Controller交互进行数据处理和保存
    """
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
        add_button = QPushButton("添加分摊模型")
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
        self.scroll_area.setWidget(self.scroll_content) # 设置滚动��域的内容
        self.main_layout.addWidget(self.scroll_area) # 将滚动区域添加到主布局

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
        """添加新的分摊模型"""
        # 获取分摊所属选项
        allocation_options = self.controller.get_allocation_options()
        
        if not allocation_options:
            QMessageBox.warning(self, "警告", "没���可用的分摊所属选项")
            return

        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle('添加新模型')
        layout = QVBoxLayout(dialog)
        
        # 添加模型类型选择
        type_label = QLabel("选择分摊模型类型:")
        type_combo = QComboBox()
        type_combo.addItems(allocation_options)
        layout.addWidget(type_label)
        layout.addWidget(type_combo)
        
        # 添加上级模型选择
        parent_label = QLabel("选择上级分摊模型(可空):")
        parent_combo = QComboBox()
        parent_combo.addItem("无上级模型", None)
        available_parents = self.controller.get_available_parent_models()
        for model_name, path in available_parents:
            parent_combo.addItem(f"{model_name} (层级: {path})", model_name)
        layout.addWidget(parent_label)
        layout.addWidget(parent_combo)
        
        # 添加按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            selected_type = type_combo.currentText()
            parent_model = parent_combo.currentData()
            
            # 保存模型及其层级关系
            success, message = self.controller.save_apportionment_model(
                selected_type, parent_model)
            
            if success:
                # 创建新的模型控件...
                self.create_model_widget(selected_type, parent_model)
            else:
                QMessageBox.warning(self, "错误", message)

    def delete_model(self, model_widget):
        """
        删除指定的分摊模型及其子模型
        
        功能：
        1. 确认删除操作
        2. 通过控制器删除相关数据和关系记录
        3. 从界面移除模型控件及其子模型控件
        
        参数：
        model_widget: 当前操作的模型控件
        """
        # 获取模型名称
        name_label = model_widget.findChildren(QLabel)[0]
        model_name = name_label.text().split(' - ')[0]

        # 获取子模型列表
        child_models = self.controller.get_child_models(model_name)
        
        # 构建确认消息
        confirm_message = f"确定要删除模型 '{model_name}'"
        if child_models:
            confirm_message += f" 及其子模型 ({', '.join(child_models)})"
        confirm_message += " 及其相关数据吗？"

        # 确认对话框
        reply = QMessageBox.question(self, '确认删除', confirm_message,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 调用控制器方法删除模型数据和关系记录
            success, message = self.controller.delete_apportionment_model(model_name)
            
            if success:
                # 从界面移除模型控件
                self.scroll_layout.removeWidget(model_widget)
                self.models.remove(model_widget)
                model_widget.deleteLater()
                
                # 移除子模型控件
                for child_name in child_models:
                    for model in self.models[:]:  # 使用切片创建副本进行迭代
                        child_label = model.findChildren(QLabel)[0]
                        if child_label.text().split(' - ')[0] == child_name:
                            self.scroll_layout.removeWidget(model)
                            self.models.remove(model)
                            model.deleteLater()
                
                QMessageBox.information(self, "删除成功", message)
            else:
                QMessageBox.warning(self, "删除失败", message)

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
        """计算分摊系数并保存应分摊公共面积"""
        # 获取所需的控件
        c_combo = model_widget.findChild(CheckableComboBox, "c_combo")
        h_combo = model_widget.findChild(CheckableComboBox, "h_combo")
        upper_coefficient_combo = model_widget.findChild(QComboBox, "upper_coefficient_combo")
        result_display = model_widget.findChild(QLineEdit, "result_display")
        name_label = model_widget.findChildren(QLabel)[0]

        if not all([c_combo, h_combo, upper_coefficient_combo, result_display, name_label]):
            QMessageBox.warning(self, "错误", "无法找到所有必要的控件")
            return

        # 获取选中的数据表
        c_tables = c_combo.currentData()
        h_tables = h_combo.currentData()
        
        # 获取上级分摊系数
        upper_coefficient = upper_coefficient_combo.currentData()
        if upper_coefficient is None:
            upper_coefficient = 0
        else:
            upper_coefficient = float(upper_coefficient)

        # 获取模型类型
        model_type = name_label.text().split(' - ')[0]

        if not c_tables or not h_tables:
            QMessageBox.warning(self, "警告", "请选择应分摊共有建筑部位和参与分摊单元")
            return

        # 首先计算并保存应分摊公共面积
        success, error = self.controller.calculate_and_save_apportionable_area(
            c_tables, upper_coefficient, model_type
        )
        
        if not success:
            QMessageBox.warning(self, "错误", error)
            return

        # 然后计算分摊系数
        coefficient, error = self.controller.calculate_apportionment_coefficient(
            c_tables, h_tables, upper_coefficient, model_type
        )

        if error:
            QMessageBox.warning(self, "错误", error)
        else:
            # 显示计算结果
            result_display.setText(f"{coefficient:.6f}")

            # 更新分摊说明
            explanation = model_widget.findChild(QLabel, "explanation")
            if explanation:
                explanation.setText(f"分摊说明:\n应分摊的共有建筑部位：{', '.join(c_tables)}\n参加分摊的户名称：{', '.join(h_tables)}")

    def create_model_widget(self, selected_type, parent_model):
        """
        创建新的分摊模型控件
        
        参数：
            selected_type (str): 选择的分摊模型类型
            parent_model (str): 上级分摊模型名称，如果没有则为None
        """
        # 获取分摊所属选项
        allocation_tables = self.controller.get_allocation_tables(selected_type)
        
        if not allocation_tables:
            QMessageBox.warning(self, "警告", f"没有找到 '{selected_type}' 相关的数据表")
            return

        # 创建新的模型控件
        model_widget = QGroupBox()
        model_layout = QVBoxLayout(model_widget)

        # 创建水平布局用于放置模型名称标签和删除按钮
        name_layout = QHBoxLayout()
        name_layout.setContentsMargins(0, 5, 0, 0)

        # 添加模型名称标签
        name_label = QLabel(f"{selected_type} - 分摊")
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        name_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        name_label.setFixedHeight(30)
        name_layout.addWidget(name_label)

        # 添加删除模型按钮
        delete_button = QPushButton("删除")
        delete_button.clicked.connect(lambda: self.delete_model(model_widget))
        delete_button.setFixedSize(50, 25)
        name_layout.addWidget(delete_button, 0, Qt.AlignRight)

        # 将水平布局添加到模型布局
        model_layout.addLayout(name_layout)

        # 添加应分摊共有建筑部位选择
        label = QLabel("应分摊共有建筑部位")
        label.setFixedHeight(20)
        model_layout.addWidget(label)
        c_combo = CheckableComboBox()
        c_combo.setObjectName("c_combo")
        c_combo.setFixedHeight(30)
        c_combo.setMinimumWidth(200)
        c_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        c_combo.addItems(allocation_tables)
        model_layout.addWidget(c_combo)

        # 添加参与分摊单元选择
        label = QLabel("参与分摊单元")
        label.setFixedHeight(20)
        model_layout.addWidget(label)
        h_combo = CheckableComboBox()
        h_combo.setObjectName("h_combo")
        h_combo.setFixedHeight(30)
        h_combo.setMinimumWidth(200)
        h_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        h_combo.addItems(allocation_tables)
        model_layout.addWidget(h_combo)

        # 添加上级分摊系数选择
        label = QLabel("上一级分摊系数")
        label.setFixedHeight(20)
        model_layout.addWidget(label)
        upper_coefficient_combo = QComboBox()
        upper_coefficient_combo.setObjectName("upper_coefficient_combo")
        upper_coefficient_combo.setFixedHeight(30)
        upper_coefficient_combo.setMinimumWidth(200)
        
        # 设置上级分摊系数选项
        upper_coefficient_combo.addItem("无上级分摊系数", None)
        if parent_model:
            # 如果有上级模型，获取其分摊系数
            parent_coefficients = self.controller.get_calculated_coefficients()
            for coeff in parent_coefficients:
                if coeff[0] == parent_model:
                    upper_coefficient_combo.addItem(f"{parent_model}: {coeff[1]}", float(coeff[1]))
                    upper_coefficient_combo.setCurrentIndex(1)  # 默认选择父模型的系��
        model_layout.addWidget(upper_coefficient_combo)

        # 添加计算分摊系数按钮
        calc_button = QPushButton("计算分摊系数")
        calc_button.setFixedSize(100, 40)
        calc_button.clicked.connect(lambda: self.calculate_apportionment_coefficient(model_widget))
        model_layout.addWidget(calc_button)

        # 添加计算结果显示标签
        result_label = QLabel("分摊系数")
        result_label.setFixedHeight(20)
        model_layout.addWidget(result_label)

        # 添加计算结果显示文本
        result_display = QLineEdit()
        result_display.setObjectName("result_display")
        result_display.setFixedHeight(30)
        result_display.setReadOnly(True)
        result_display.setPlaceholderText("本级分摊系数结果将显示在这里")
        model_layout.addWidget(result_display)

        # 添加分摊说明
        explanation = QLabel("分摊说明:\n应分摊的共有建筑部位：未选择\n参加分摊的户名称：未选择")
        explanation.setObjectName("explanation")
        model_layout.addWidget(explanation)

        # 设置固定宽度高度以确保横向排列时的一致性
        model_widget.setFixedSize(250, 450)

        # 将新模型添加到滚动区域，并设置在顶端左对齐
        self.scroll_layout.addWidget(model_widget, 0, Qt.AlignTop | Qt.AlignLeft)
        self.models.append(model_widget)

# 用于测试的代码
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 创建一个模拟的 controller
    class MockController:
        def get_allocation_options(self):
            return ["选项1", "选项2", "选项3"]
        
        def get_allocation_tables(self, option):
            return [f"{option}_1", f"{option}_2", f"{option}_3"]
        
        # 添加缺失的方法
        def get_calculated_coefficients(self):
            # 返回模拟的已计算系数数据
            # 每个元素是一个元组，包含 (描述, 系数)
            return [
                ("一层分摊", "0.5"),
                ("二层分摊", "0.3"),
                ("三层分摊", "0.2")
            ]
        
        # 添加其他可能需要的方法
        def calculate_apportionment_coefficient(self, c_tables, h_tables, upper_coefficient, model_type):
            # 返回模拟的计算结果和错误信息
            return 0.123456, None

        def delete_apportionment_model(self, model_name):
            # 返回模拟的删除结果
            return True, f"模型 {model_name} 删除成功"
    
    mock_controller = MockController()
    view = ApportionmentModelView(mock_controller)
    view.show()
    sys.exit(app.exec_())
