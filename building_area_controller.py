from building_area_model import BuildingAreaModel
from MainWindow import MainWindow

class BuildingAreaController:
    """
    建筑面积控制器类
    
    负责协调模型（BuildingAreaModel）和视图（MainWindow）之间的交互。
    控制数据的导入和更新到相应的视图组件。
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
        # 连接住房单元1的导入按钮
        housing_unit_1 = self.view.housing_unit_1
        housing_unit_1.import_button.clicked.connect(self.import_housing_unit_data)

        # 连接公共财产房屋2的导入按钮
        common_property_house_2 = self.view.common_property_house_2
        common_property_house_2.import_button.clicked.connect(self.import_common_property_data)

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

    def show(self):
        """
        显示主窗口
        """
        self.view.show()
