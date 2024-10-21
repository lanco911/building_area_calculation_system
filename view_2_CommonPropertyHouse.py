import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QHeaderView
from PyQt5.QtCore import Qt

class CommonPropertyHouse(QWidget):
    """
    共有建筑面积界面类
    
    用于显示和管理共有建筑面积的数据。
    包含一个表格用于展示数据，以及导入和保存数据的按钮。
    """

    def __init__(self):
        """
        初始化共有建筑面积界面
        
        设置窗口标题、大小，并调用initUI方法创建界面元素。
        """
        super().__init__()
        self.initUI()
        self.setWindowTitle("共有建筑面积")
        self.setGeometry(100, 100, 800, 600)

    def initUI(self):
        """
        初始化用户界面
        
        创建并布局界面元素，包括导入按钮、数据表格和保存按钮。
        """
        # 创建主窗口部件和布局
        main_layout = QVBoxLayout(self)

        # 创建顶部布局，包含导入按钮
        top_layout = QHBoxLayout()
        self.import_button = QPushButton("导入数据")
        top_layout.addWidget(self.import_button)
        top_layout.addStretch(1)
        main_layout.addLayout(top_layout)

        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["CID", "实际楼层", "房号", "主间面积", "阳台面积", "套内面积", "用途"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        # 创建底部布局，包含保存按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        self.save_button = QPushButton("保存")
        bottom_layout.addWidget(self.save_button)
        main_layout.addLayout(bottom_layout)

    def update_table(self, data):
        """
        更新表格数据
        
        :param data: 要显示在表格中的数据列表
        
        将传入的数据填充到表格中，每个列表项对应一行数据。
        """
        self.table.setRowCount(len(data))
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    def get_table_data(self):
        """
        获取表格中的所有数据
        
        返回:
            list: 包含表格所有数据的二维列表
        """
        data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data

    def get_table_headers(self):
        """
        获取表格的表头
        
        返回:
            list: 包含表格表头的列表
        """
        return ["CID", "实际楼层", "房号", "主间面积", "阳台面积", "套内面积", "用途"]

if __name__ == '__main__':
    """
    主程序入口
    
    创建QApplication实例，显示CommonPropertyHouse窗口，并启动事件循环。
    这部分代码允许该模块作为独立程序运行，方便测试和调试。
    """
    app = QApplication(sys.argv)
    common_property_house = CommonPropertyHouse()
    common_property_house.show()
    sys.exit(app.exec_())
