import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableWidgetItem
from PyQt5.QtCore import Qt

class HousingUnit1(QWidget):
    """
    户单元套内面积界面类
    
    用于显示和管理户单元套内面积的数据。
    包含一个表格用于展示数据，以及导入和保存数据的按钮。
    """

    def __init__(self):
        """
        初始化户单元套内面积界面
        
        设置窗口标题、大小，并调用initUI方法创建界面元素。
        """
        super().__init__()
        self.initUI()
        self.setWindowTitle("户单元套内面积")
        self.setGeometry(100, 100, 800, 600)

    def initUI(self):
        """
        初始化用户界面
        
        创建并布局界面元素，包括导入按钮、数据表格和保存按钮。
        采用垂直布局作为主布局，顶部和底部使用水平布局。
        """
        # 创建主窗口部件和布局
        main_layout = QVBoxLayout(self)

        # 创建顶部布局，包含导入按钮
        top_layout = QHBoxLayout()
        self.import_button = QPushButton("导入数据")  # 导入数据按钮
        top_layout.addWidget(self.import_button)
        top_layout.addStretch(1)  # 添加弹性空间以调整布局
        main_layout.addLayout(top_layout)

        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # 设置表格的列数
        self.table.setHorizontalHeaderLabels(["HID", "实际楼层", "房号", "主间面积", "阳台面积", "套内面积"])  # 设置表头
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 设置表格列宽自适应
        main_layout.addWidget(self.table)

        # 创建底部布局，包含保存按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)  # 添加弹性空间
        self.save_button = QPushButton("保存")  # 保存按钮
        bottom_layout.addWidget(self.save_button)
        main_layout.addLayout(bottom_layout)

    def update_table(self, data):
        """
        更新表格数据
        
        :param data: 要显示在表格中的数据列表
        
        将传入的数据填充到表格中，每个列表项对应一行数据。
        自动调整表格的行数以匹配数据量。
        """
        self.table.setRowCount(len(data))  # 设置表格行数
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))  # 填充表格数据

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
        return [self.table.horizontalHeaderItem(col).text() for col in range(self.table.columnCount())]

if __name__ == '__main__':
    """
    主程序入口
    
    创建QApplication实例，显示HousingUnit1窗口，并启动事件循环。
    这部分代码允许该模块作为独立程序运行，方便测试和调试。
    """
    app = QApplication(sys.argv)
    housing_unit_1 = HousingUnit1()
    housing_unit_1.show()
    sys.exit(app.exec_())