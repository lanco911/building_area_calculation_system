import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox
from view_1_HousingUnit import HousingUnit
from view_2_CommonPropertyHouse import CommonPropertyHouse
from view_3_CPHouseBelongseting import CPHouseBelongseting
from view_4_ApportionmentModel import ApportionmentModelView



class MainWindow(QMainWindow):
    """
    主窗口类
    
    创建应用程序的主界面，包含四个标签页：
    1. 户单元套内面积
    2. 共有建筑面积
    3. 共有建筑分摊所属设置
    4. 共有建筑面积分配模型设置
    """

    def __init__(self, controller):
        """
        初始化主窗口
        
        设置窗口标题、大小，并创建包含四个标签页的界面。
        """
        super().__init__()
        self.controller = controller
        
        # 设置窗口标题和初始大小
        self.setWindowTitle("房屋面积计算系统")
        self.setGeometry(100, 100, 1000, 600)

        # 创建标签页控件
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # 创建四个不同的视图实例
        self.housing_unit_1 = HousingUnit()
        self.common_property_house_2 = CommonPropertyHouse()
        self.common_allocation_settings_3 = CPHouseBelongseting(self.controller)
        self.apportionment_model_4 = ApportionmentModelView(self.controller)

        # 将视图添加到标签页中
        self.tab_widget.addTab(self.housing_unit_1, "户单元套内面积")
        self.tab_widget.addTab(self.common_property_house_2, "共有建筑面积")
        self.tab_widget.addTab(self.common_allocation_settings_3, "共有建筑分摊所属设置")
        self.tab_widget.addTab(self.apportionment_model_4, "共有建筑面积分配模型设置")

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
    # 添加一个模拟的 Controller 类
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

    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 创建 controller 实例
    controller = MockController()
    
    # 创建并显示主窗口，传入 controller
    main_window = MainWindow(controller)
    main_window.show()
    
    # 启动应用程序的事件循环
    sys.exit(app.exec_())
