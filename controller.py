from model import BuildingAreaModel
from MainWindow import MainWindow
from PyQt5.QtWidgets import QMessageBox

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
        # 移除这里的 self.connect_signals()

    def set_view(self, view):
        self.view = view
        self.connect_signals()

    def connect_signals(self):
        """
        连接视图中的按钮信号到相应的控制器方法
        """
        # 连接住房单元1的导入和保存按钮
        housing_unit_1 = self.view.housing_unit_1
        housing_unit_1.import_button.clicked.connect(self.import_housing_unit_data)
        housing_unit_1.save_button.clicked.connect(self.save_housing_unit_data)

        # 连接公共财产房屋2的导入和保存按钮
        common_property_house_2 = self.view.common_property_house_2
        common_property_house_2.import_button.clicked.connect(self.import_common_property_data)
        common_property_house_2.save_button.clicked.connect(self.save_common_property_data)

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

    def save_housing_unit_data(self):
        """
        保存住房单元数据到数据库
        """
        data = self.view.housing_unit_1.get_table_data()
        headers = self.view.housing_unit_1.get_table_headers()
        self.model.data = data
        self.model.headers = headers
        if self.model.save_data("户单元套内面积"):
            self.view.show_message("保存成功", "户单元数据已成功保存，并更新了幢总建筑面积表")
        else:
            self.view.show_message("保存失败", "保存户单元��据时出错")

    def save_common_property_data(self):
        """
        保存公共财产数据到数据库
        """
        data = self.view.common_property_house_2.get_table_data()
        headers = self.view.common_property_house_2.get_table_headers()
        self.model.data = data
        self.model.headers = headers
        if self.model.save_data("共有建筑面积"):
            self.view.show_message("保存成功", "共有建筑数据已成功保存，并更新了幢总建筑面积表")
        else:
            self.view.show_message("保存失败", "保共有建筑数据时出错")

    def show(self):
        """
        显示主窗口
        """
        self.view.show()

    def get_table_names(self):
        """获取数据库中所有表的名称"""
        return self.model.get_table_names()

    def fetch_data_from_table(self, table_name):
        """从指定表中获取数据"""
        return self.model.fetch_data_from_table(table_name)

    def validate_allocation_data(self, data_to_save, loaded_data):
        """验证将要保存的数据"""
        saved_ids = [unit[1] for unit in data_to_save]  # 获取所有ID
        loaded_ids = [unit[0] for unit in loaded_data]  # 获取所有加载的ID

        errors = []

        # 1. 检查ID是否有重复
        duplicate_ids = set([id for id in saved_ids if saved_ids.count(id) > 1])
        if duplicate_ids:
            for id in duplicate_ids:
                rooms = [unit[2] for unit in data_to_save if unit[1] == id]
                errors.append(f"ID {id} 重复，对应房号: {', '.join(rooms)}")

        # 2. 验证数据数量是否一致，检查缺少的ID
        if len(saved_ids) != len(loaded_ids):
            missing_ids = set(loaded_ids) - set(saved_ids)
            for id in missing_ids:
                room = next(unit[1] for unit in loaded_data if unit[0] == id)
                errors.append(f"缺少 ID {id}，对应房号: {room}")

        if errors:
            return False, "数据验证失败:\n" + "\n".join(errors)
        return True, "验证通过"

    def save_allocation_data(self, allocation_name, data_to_save, loaded_data):
        """保存分配数据，包含验证步骤"""
        is_valid, message = self.validate_allocation_data(data_to_save, loaded_data)
        if not is_valid:
            return False, message
        
        created_tables = self.model.save_allocation_data(allocation_name, data_to_save)
        return True, f"数据已成功保存到以下表: {', '.join(created_tables)}"

    def delete_allocation_area(self, allocation_name):
        """删除分摊所属及其相关数据表"""
        deleted_tables = self.model.delete_allocation_tables(allocation_name)
        return deleted_tables
