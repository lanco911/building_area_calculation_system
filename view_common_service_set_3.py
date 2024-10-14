import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QGroupBox, QListWidget, QDialog, QDialogButtonBox, QScrollArea, QInputDialog
from PyQt5.QtCore import Qt

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
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

        self.setLayout(self.layout)

    # 获取选中的单元
    def get_selected_units(self):
        return [item.text() for item in self.unit_list.selectedItems()]

# 共有建筑服务范围区设置视图类
class CommonServiceAreaSettingsView(QWidget):
    def __init__(self):
        super().__init__()
        self.available_units = ["单元1", "单元2", "单元3", "单元4", "单元5"]  # 示例可用单元
        self.group_count = 0  # 分组计数器
        self.service_areas = []  # 存储服务区控件的列表
        self.initUI()

    def initUI(self):
        # 创建主垂直布局
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # 添加服务区部分
        add_service_layout = QHBoxLayout()
        self.service_input = QLineEdit()
        self.service_input.setPlaceholderText("输入新服务区名称")
        add_service_button = QPushButton("添加服务区")
        add_service_button.clicked.connect(self.add_service_area)
        add_service_layout.addWidget(self.service_input)
        add_service_layout.addWidget(add_service_button)
        self.main_layout.addLayout(add_service_layout)

        # 创建滚动区域，用于容纳多个服务区
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        # 设置窗口标题和大小
        self.setWindowTitle('共有建筑服务范围区设置')
        self.setGeometry(300, 300, 800, 600)

    def add_service_area(self):
        service_name = self.service_input.text()
        if service_name:
            # 创建新的服务区控件
            service_widget = QGroupBox(service_name)
            service_layout = QVBoxLayout()

            # 添加分组和加载数据按钮
            buttons_layout = QHBoxLayout()
            load_data_button = QPushButton("加载数据")
            load_data_button.clicked.connect(self.load_data)
            load_data_button.setMaximumWidth(100)
            add_group_button = QPushButton("添加分组")
            add_group_button.setMaximumWidth(100)
            buttons_layout.addWidget(load_data_button)
            buttons_layout.addStretch(1)
            buttons_layout.addWidget(add_group_button)
            service_layout.addLayout(buttons_layout)

            # 创建滚动区域，用于容纳多个分组
            group_scroll_area = QScrollArea()
            group_scroll_area.setWidgetResizable(True)
            group_scroll_content = QWidget()
            group_scroll_layout = QHBoxLayout(group_scroll_content)
            group_scroll_area.setWidget(group_scroll_content)
            service_layout.addWidget(group_scroll_area)

            # 将添加分组按钮连接到新的方法
            add_group_button.clicked.connect(lambda: self.add_group(group_scroll_layout))

            # 添加保存按钮
            save_button = QPushButton("保存数据")
            save_button.setMaximumWidth(100)
            save_button_layout = QHBoxLayout()
            save_button_layout.addStretch(1)
            save_button_layout.addWidget(save_button)
            service_layout.addLayout(save_button_layout)

            # 添加删除服务区按钮
            delete_service_button = QPushButton("删除服务区")
            delete_service_button.clicked.connect(lambda: self.delete_service_area(service_widget))
            service_layout.addWidget(delete_service_button)

            service_widget.setLayout(service_layout)
            self.scroll_layout.addWidget(service_widget)
            self.service_areas.append(service_widget)
            self.service_input.clear()

    def delete_service_area(self, service_widget):
        self.scroll_layout.removeWidget(service_widget)
        self.service_areas.remove(service_widget)
        service_widget.deleteLater()

    def add_group(self, parent_layout):
        group_name, ok = QInputDialog.getText(self, '添加分组', '请输入新分组名称:')
        if ok and group_name:
            self.group_count += 1
            group_widget = QGroupBox(f"{group_name}")
            group_layout = QVBoxLayout()

            # 设置参与分摊单元布局
            participating_layout = QHBoxLayout()
            
            list_layout = QVBoxLayout()
            participating_units = QListWidget()
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
            group_widget.setFixedWidth(300)  # 增加宽度以适应按钮
            parent_layout.addWidget(group_widget)

    def delete_group(self, group_widget, parent_layout):
        parent_layout.removeWidget(group_widget)
        group_widget.deleteLater()
        self.group_count -= 1

    # 加载数据（待实现）
    def load_data(self):
        # 这里添加加载数据的逻辑
        print("加载数据")

    # 添加参与分摊单元
    def add_participating_unit(self, list_widget):
        dialog = SelectUnitsDialog(self.available_units)
        if dialog.exec_():
            selected_units = dialog.get_selected_units()
            for unit in selected_units:
                if list_widget.findItems(unit, Qt.MatchExactly) == []:
                    list_widget.addItem(unit)

    # 删除参与分摊单元
    def delete_participating_unit(self, list_widget):
        current_item = list_widget.currentItem()
        if current_item:
            # 这里可以添加处理删除单元的逻辑
            list_widget.takeItem(list_widget.row(current_item))

if __name__ == '__main__':
    # 创建应用程序实例并运行
    app = QApplication(sys.argv)
    view = CommonServiceAreaSettingsView()
    view.show()
    sys.exit(app.exec_())
