from building_area_model import BuildingAreaModel
from MainWindow import MainWindow

class BuildingAreaController:
    """
    建筑面积控制器类
    
    负责协调模型（BuildingAreaModel）和视图（MainWindow）之间的交互。
    控制数据的导入、保存和更新到相应的视图组件。
    """

    def __init__(self, model, view):
        """
        初始化控制器
        
        :param model: BuildingAreaModel 实例
        :param view: MainWindow 实例
        """
        self.model = model
        self.view = view
        self.connect_signals()

    def connect_signals(self):
        """
        连接视图中的按钮信号到相应的控制器方法
        """
        # 连接住房单元1的导入和保存按钮
        housing_unit_1 = self.view.housing_unit_1
        housing_unit_1.import_button.clicked.connect(self.import_housing_unit_data)
        housing_unit_1.save_button.clicked.connect(lambda: self.save_housing_unit_data("H"))

        # 连接公共财产房屋2的导入和保存按钮
        common_property_house_2 = self.view.common_property_house_2
        common_property_house_2.import_button.clicked.connect(self.import_common_property_data)
        common_property_house_2.save_button.clicked.connect(lambda: self.save_common_property_data("C"))

    def import_housing_unit_data(self):
        """
        导入住房单元数据并更新相应的视图
        """
        data = self.model.import_data()
        self.view.housing_unit_1.update_table(data)

    def import_common_property_data(self):
        """
        导入公共财产数据并更新相应的视图
        """
        data = self.model.import_data()
        self.view.common_property_house_2.update_table(data)

    def save_housing_unit_data(self, table_name):
        """
        保存住房单元数据到数据库
        """
        data = self.view.housing_unit_1.get_table_data()
        headers = self.view.housing_unit_1.get_table_headers()
        self.model.data = data
        self.model.headers = headers
        if self.model.save_data(table_name):
            self.view.show_message("保存成功", f"住房单元数据已成功保存到表 {table_name}")
        else:
            self.view.show_message("保存失败", "保存住房单元数据时出错")

    def save_common_property_data(self, table_name):
        """
        保存公共财产数据到数据库
        """
        data = self.view.common_property_house_2.get_table_data()
        headers = self.view.common_property_house_2.get_table_headers()
        self.model.data = data
        self.model.headers = headers
        if self.model.save_data(table_name):
            self.view.show_message("保存成功", f"公共财产数据已成功保存到表 {table_name}")
        else:
            self.view.show_message("保存失败", "保存公共财产数据时出错")

    def show(self):
        """
        显示主窗口
        """
        self.view.show()
