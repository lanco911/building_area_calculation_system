import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox
from view_housing_unit_1 import HousingUnit1
from view_common_property_house_2 import CommonPropertyHouse2
from view_common_service_set_3 import CommonAllocationSettingsView  # 导入新的视图

class MainWindow(QMainWindow):
    """
    主窗口类
    
    创建应用程序的主界面，包含三个标签页：
    1. 户单元套内面积
    2. 共有建筑面积
    3. 共有建筑分摊所属设置
    """

    def __init__(self):
        """
        初始化主窗口
        
        设置窗口标题、大小，并创建包含三个标签页的界面。
        """
        super().__init__()
        
        # 设置窗口标题和初始大小
        self.setWindowTitle("房屋面积计算系统")
        self.setGeometry(100, 100, 800, 600)

        # 创建标签页控件
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # 创建三个不同的视图实例
        self.housing_unit_1 = HousingUnit1()
        self.common_property_house_2 = CommonPropertyHouse2()
        self.common_allocation_settings_3 = CommonAllocationSettingsView()  # 创建新的视图实例

        # 将视图添加到标签页中
        self.tab_widget.addTab(self.housing_unit_1, "户单元套内面积")
        self.tab_widget.addTab(self.common_property_house_2, "共有建筑面积")
        self.tab_widget.addTab(self.common_allocation_settings_3, "共有建筑分摊所属设置")  # 添加新的标签页

    def show_message(self, title, message):
        """
        显示消息对话框
        
        :param title: 对话框标题
        :param message: 对话框内容
        """
        QMessageBox.information(self, title, message)

if __name__ == '__main__':
    """
    应用程序入口点
    
    创建QApplication实例，显示主窗口，并启动事件循环。
    """
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 创建并显示主窗口
    main_window = MainWindow()
    main_window.show()
    
    # 启动应用程序的事件循环
    sys.exit(app.exec_())
