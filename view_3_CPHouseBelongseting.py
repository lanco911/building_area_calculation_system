import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QGroupBox, QListWidget, QDialog, QDialogButtonBox, QScrollArea, QInputDialog, QTabWidget, QMessageBox, QComboBox, QListWidgetItem
from PyQt5.QtCore import Qt
import re

# 选择单元对话框类
class SelectUnitsDialog(QDialog): 
    def __init__(self, available_units):
        super().__init__()  # 调用父类构造函数
        self.setWindowTitle("选择单元")  # 设置窗口标题
        self.layout = QVBoxLayout()  # 创建一个垂直布局

        # 创建可选单元列表
        self.unit_list = QListWidget()  # 创建一个列表控件
        self.unit_list.addItems(available_units)  # 添加可用单元
        self.unit_list.setSelectionMode(QListWidget.MultiSelection)  # 允许多选
        self.layout.addWidget(self.unit_list)  # 将列表控件添加到布局中

        # 添加确定和取消按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)  # 连接确定按钮的信号到对话框的接受槽
        buttons.rejected.connect(self.reject)  # 连接取消按钮的信号到对话框的拒绝槽
        self.layout.addWidget(buttons)

        self.setLayout(self.layout)  # 设置对话框的布局

    # 获取选中的单元
    def get_selected_units(self):
        # 返回所有被选中的单元的文本
        return [item.text() for item in self.unit_list.selectedItems()]

# 共有建筑分摊所属设置视图类
class CPHouseBelongseting(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.available_units = []
        self.group_count = 0
        self.allocation_areas = []
        self.current_parent_table = None  # 添加变量存储当前选择的父表
        self.initUI()

    def initUI(self):
        # 创建主垂直布局
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # 创建顶部水平布局，用于放置添加分摊所属按钮
        top_layout = QHBoxLayout()
        
        # 添加分摊所属按钮
        add_allocation_button = QPushButton("添加分摊所属")
        add_allocation_button.clicked.connect(self.add_allocation_area)  # 连接按钮点击信号到添加分摊所属的方法
        add_allocation_button.setMaximumWidth(120)  # 设置按钮的最大宽度
        top_layout.addWidget(add_allocation_button)
        top_layout.addStretch(1)  # 添加弹性空间，将钮推到左边
        
        self.main_layout.addLayout(top_layout)

        # 创建标签页控件并设置标签位置在左侧
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.West)  # 设置标签页位置在左侧
        self.main_layout.addWidget(self.tab_widget)

        # 设置窗口标题和大小
        self.setWindowTitle('共有建筑分摊所属设置')
        self.setGeometry(300, 300, 1000, 600)  # 增加窗口宽度

    def add_allocation_area(self):
        # 弹出输入对话框
        allocation_name, ok = QInputDialog.getText(self, '添加分摊所属', '请输入新分摊所属名称:')
        if ok and allocation_name:
            # 创建新的分摊所属控件
            allocation_widget = QWidget()
            allocation_layout = QVBoxLayout(allocation_widget)

            # 添加按钮布局
            buttons_layout = QHBoxLayout()
            load_data_button = QPushButton("加载数据")
            load_data_button.clicked.connect(lambda: self.load_data(allocation_widget))
            load_data_button.setMaximumWidth(100)
            select_common_parts_button = QPushButton("选择分摊公共建筑部位")
            select_common_parts_button.setMaximumWidth(180)
            add_group_button = QPushButton("添加分组")
            add_group_button.setMaximumWidth(100)
            buttons_layout.addWidget(load_data_button)
            buttons_layout.addWidget(select_common_parts_button)
            buttons_layout.addStretch(1)
            buttons_layout.addWidget(add_group_button)
            allocation_layout.addLayout(buttons_layout)

            # 创建水平布局，用于放置公共建筑部位和其他分组
            content_layout = QHBoxLayout()

            # 创建公共建筑部位的垂直布局
            common_parts_layout = QVBoxLayout()
            content_layout.addLayout(common_parts_layout)

            # 创建滚动区域，用于容纳其他分组
            group_scroll_area = QScrollArea()
            group_scroll_area.setWidgetResizable(True)
            group_scroll_content = QWidget()
            group_scroll_layout = QHBoxLayout(group_scroll_content)
            group_scroll_layout.setAlignment(Qt.AlignLeft)
            group_scroll_layout.addStretch(1)
            group_scroll_area.setWidget(group_scroll_content)
            content_layout.addWidget(group_scroll_area)

            allocation_layout.addLayout(content_layout)

            # 连接按钮点击事件
            select_common_parts_button.clicked.connect(lambda: self.add_common_parts_group(common_parts_layout))
            add_group_button.clicked.connect(lambda: self.add_group(group_scroll_layout))

            # 添加保存和删除按钮
            bottom_buttons_layout = QHBoxLayout()
            save_button = QPushButton("保存数据")
            save_button.clicked.connect(lambda: self.save_data(allocation_widget))
            save_button.setMaximumWidth(100)
            delete_allocation_button = QPushButton("删除分摊所属")
            delete_allocation_button.setMaximumWidth(120)
            delete_allocation_button.clicked.connect(lambda: self.delete_allocation_area(self.tab_widget.indexOf(allocation_widget)))
            bottom_buttons_layout.addStretch(1)
            bottom_buttons_layout.addWidget(save_button)
            bottom_buttons_layout.addWidget(delete_allocation_button)
            allocation_layout.addLayout(bottom_buttons_layout)

            # 将新创建的分摊所属控件添加到标签页中
            self.tab_widget.addTab(allocation_widget, allocation_name)
            self.allocation_areas.append(allocation_widget)

            # 切换到新添加的标签页
            self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

    def delete_allocation_area(self, index):
        if index != -1:
            allocation_widget = self.tab_widget.widget(index)
            allocation_name = self.tab_widget.tabText(index)
            
            # 确认对话框
            reply = QMessageBox.question(self, '确认删除', 
                                         f"确定要删除分摊所属 '{allocation_name}' 及其相关数据吗？\n" +
                                         "注意：这将同时删除所有子分摊所属！",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # 删除数据库中的相关表
                deleted_tables = self.controller.delete_allocation_area(allocation_name)
                
                # 从表名中提取所有相关的分摊所属名称
                deleted_allocations = set()
                if deleted_tables:  # 如果有删除的表
                    for table in deleted_tables:
                        # 从表名中提取分摊所属名称
                        match = re.match(r'分摊所属_([^_]+)', table)
                        if match:
                            deleted_allocations.add(match.group(1))
                else:
                    # 如果没有删除的表，至少删除当前的分摊所属
                    deleted_allocations.add(allocation_name)
                
                # 删除所有相关的分摊所属控件
                tabs_to_remove = []
                for i in range(self.tab_widget.count()):
                    tab_text = self.tab_widget.tabText(i)
                    if tab_text in deleted_allocations:
                        tabs_to_remove.append(i)
                
                # 从后往前删除标签页，避免索引变化的问题
                for i in sorted(tabs_to_remove, reverse=True):
                    widget = self.tab_widget.widget(i)
                    self.tab_widget.removeTab(i)
                    if widget in self.allocation_areas:
                        self.allocation_areas.remove(widget)
                    widget.deleteLater()
                
                # 显示删除结果
                if deleted_tables:
                    message = "已删除以下分摊所属：\n"
                    message += "\n".join(sorted(deleted_allocations))
                    message += "\n\n对应的数据表：\n"
                    message += "\n".join(sorted(deleted_tables))
                    QMessageBox.information(self, "删除成功", message)
                else:
                    QMessageBox.information(self, "删除成功", 
                                          f"已删除分摊所属 '{allocation_name}'")

    def add_group(self, parent_layout):
        # 弹出对话框获取新分组名称
        group_name, ok = QInputDialog.getText(self, '添加分组', '请输入新分组名称:')
        if ok and group_name:
            # 在用户输入的名称后添加"范围各单元"
            full_group_name = f"{group_name}范围各单元"
            self.group_count += 1  # 增加分组计数
            group_widget = QGroupBox(f"{full_group_name}")  # 使用完整的分组名称
            group_layout = QVBoxLayout()

            # 设置参与分摊单元布局
            participating_layout = QHBoxLayout()
            
            list_layout = QVBoxLayout()
            participating_units = QListWidget()  # 创建参与分摊单元的列表控件
            list_layout.addWidget(participating_units)
            participating_layout.addLayout(list_layout)
            
            # 添加和删除单元的按钮
            buttons_layout = QVBoxLayout()
            buttons_layout.addWidget(QLabel(""))  # 添加空白标签作为占位符
            add_participating_button = QPushButton("添加")
            add_participating_button.setMaximumWidth(60)
            add_participating_button.clicked.connect(lambda: self.add_participating_unit(participating_units))
            delete_participating_button = QPushButton("删除")
            delete_participating_button.setMaximumWidth(60)
            delete_participating_button.clicked.connect(lambda: self.delete_participating_unit(participating_units))
            buttons_layout.addWidget(add_participating_button)
            buttons_layout.addWidget(delete_participating_button)
            buttons_layout.addStretch(1)  # 添加弹性空间
            participating_layout.addLayout(buttons_layout)
            
            group_layout.addLayout(participating_layout)
            
            # 添加删除分组按钮，并将其放在右边
            delete_group_layout = QHBoxLayout()
            delete_group_layout.addStretch(1)  # 添加弹性空间，将按钮推到右边
            delete_group_button = QPushButton("删除分组")
            delete_group_button.setMaximumWidth(100)
            delete_group_button.clicked.connect(lambda: self.delete_group(group_widget, parent_layout))
            delete_group_layout.addWidget(delete_group_button)
            group_layout.addLayout(delete_group_layout)
            
            group_widget.setLayout(group_layout)
            group_widget.setFixedWidth(250)  # 设置固定宽度
            
            # 将新的分组插入到最后一个项（弹性空间）之前
            parent_layout.insertWidget(parent_layout.count() - 1, group_widget)

    def delete_group(self, group_widget, parent_layout):
        # 从布局中移除并删除指定的分组控件
        parent_layout.removeWidget(group_widget)
        group_widget.deleteLater()
        self.group_count -= 1  # 减少分组计数

    def load_data(self, allocation_widget):
        # 获取可用的分摊所属表
        available_tables = self.controller.get_available_belong_tables()
        if not available_tables:
            QMessageBox.warning(self, "警告", "没有可用的数据表")
            return
        
        # 准备显示选项（使用别名）和对应的表名
        table_aliases = [row[1] for row in available_tables]
        table_names = {row[1]: row[0] for row in available_tables}
        
        # 显示选择对话框
        alias, ok = QInputDialog.getItem(
            self, 
            "选择数据表", 
            "选择要加载的数据:", 
            table_aliases, 
            0, 
            False
        )
        
        if ok and alias:
            # 根据选择的别名获取实际的表名
            table_name = table_names[alias]
            self.current_parent_table = table_name  # 保存选择的父表名称
            data = self.controller.fetch_data_from_table(table_name)
            self.available_units = data  # 存储完整的数据
            
            # 修改显示格式，使用 "ID-房号(面积)" 的格式
            display_units = [f"{row[0]}-{row[1]}({row[2]})" for row in data]
            
            for group in allocation_widget.findChildren(QGroupBox):
                list_widget = group.findChild(QListWidget)
                if list_widget:
                    list_widget.clear()
                    for i, unit in enumerate(display_units):
                        item = QListWidgetItem(unit)
                        item.setData(Qt.UserRole, data[i])  # 存储完整的数据
                        list_widget.addItem(item)

    def save_data(self, allocation_widget):
        allocation_name = self.tab_widget.tabText(self.tab_widget.indexOf(allocation_widget))
        data = []
        
        for group in allocation_widget.findChildren(QGroupBox):
            group_name = group.title()
            list_widget = group.findChild(QListWidget)
            if list_widget:
                for i in range(list_widget.count()):
                    item = list_widget.item(i)
                    unit_data = item.data(Qt.UserRole)
                    data.append((group_name,) + unit_data)  # 添加组名和完整的单元数据
        
        # 调用控制器的保存方法，包含验证逻辑和父表信息
        success, message = self.controller.save_allocation_data(
            allocation_name, 
            data, 
            self.available_units,
            self.current_parent_table  # 传递父表名称
        )
        
        if success:
            QMessageBox.information(self, "保存成功", message)
        else:
            QMessageBox.warning(self, "数据验证失败", message + "\n请修改数据后再次尝试保存。")

    def add_participating_unit(self, list_widget):
        # 弹出选择单元对话框
        # 使用相同的显示格式
        dialog = SelectUnitsDialog([f"{unit[0]}-{unit[1]}({unit[2]})" for unit in self.available_units])
        if dialog.exec_():
            selected_units = dialog.get_selected_units()  # 获取选中的单元
            for unit in selected_units:
                # 检查单元是否已存在于列表中
                if list_widget.findItems(unit, Qt.MatchExactly) == []:
                    # 修改匹配逻辑以适应新的显示格式
                    index = next(i for i, u in enumerate(self.available_units) 
                               if f"{u[0]}-{u[1]}({u[2]})" == unit)
                    item = QListWidgetItem(unit)
                    item.setData(Qt.UserRole, self.available_units[index])
                    list_widget.addItem(item)  # 添加新单元到列表

    def delete_participating_unit(self, list_widget):
        current_item = list_widget.currentItem()  # 取当前选中的单元
        if current_item:
            # 这里可以添加处理删除单元的逻辑
            list_widget.takeItem(list_widget.row(current_item))  # 从列表中移除选中的单元

    def add_common_parts_group(self, parent_layout):
        if parent_layout.count() == 0:  # 只有当还没有添加公共建筑部位时才添加
            group_widget = QGroupBox("分摊公共建筑部位")
            group_layout = QVBoxLayout()

            # 设置参与分摊单元布局
            participating_layout = QHBoxLayout()
            
            list_layout = QVBoxLayout()
            participating_units = QListWidget()
            list_layout.addWidget(participating_units)
            participating_layout.addLayout(list_layout)
            
            # 添加和删除单元的按钮
            buttons_layout = QVBoxLayout()
            add_participating_button = QPushButton("添加")
            add_participating_button.setMaximumWidth(60)
            add_participating_button.clicked.connect(lambda: self.add_participating_unit(participating_units))
            delete_participating_button = QPushButton("删除")
            delete_participating_button.setMaximumWidth(60)
            delete_participating_button.clicked.connect(lambda: self.delete_participating_unit(participating_units))
            buttons_layout.addWidget(add_participating_button)
            buttons_layout.addWidget(delete_participating_button)
            buttons_layout.addStretch(1)
            participating_layout.addLayout(buttons_layout)
            
            group_layout.addLayout(participating_layout)
            
            group_widget.setLayout(group_layout)
            group_widget.setFixedWidth(250)
            parent_layout.addWidget(group_widget)
        else:
            QMessageBox.warning(self, "警告", "分摊公共建筑部位已存在")



if __name__ == '__main__':
    # 创建应用程序实例并运行
    # 在文件末尾，修改 main 部分
    class MockController:
        def __init__(self):
            pass
        
        def get_table_names(self):
            return ["表1", "表2", "表3"]
        
        def fetch_data_from_table(self, table_name):
            return [("1", "单元A", "类型1"), ("2", "单元B", "类型2")]
        
        def save_allocation_data(self, allocation_name, data, available_units):
            print(f"保存数据：{allocation_name}")
            print(f"数据：{data}")
            return True, "数据保存成功"
        
        def delete_allocation_area(self, allocation_name):
            print(f"删除分摊所属：{allocation_name}")
            return ["表1", "表2"]
    app = QApplication(sys.argv)
    mock_controller = MockController()  # 创建模拟的 controller
    view = CPHouseBelongseting(mock_controller)  # 传入 controller
    view.show()
    sys.exit(app.exec_())
