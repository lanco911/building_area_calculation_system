import pandas as pd
from PyQt5.QtWidgets import QFileDialog
import sqlite3

class BuildingAreaModel:
    """
    建筑面积模型类
    
    负责处理建筑面积数据的导入、存储和管理。
    提供了导入Excel文件和保存数据到SQLite数据库的功能。
    """

    def __init__(self):
        """
        初始化模型
        
        创建一个空列表来存储导入的数据
        """
        self.data = []  # 用于存储导入的数据
        self.headers = []  # 用于存储表头
        self.conn = sqlite3.connect('building_area.db')
        self.cursor = self.conn.cursor()
        self.initialize_tables()

    def initialize_tables(self):
        # 创建所有必要的表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS "户单元套内面积" 
                               (HID TEXT, 实际楼层 TEXT, 房号 TEXT, 主间面积 TEXT, 
                                阳台面积 TEXT, 套内面积 TEXT, 用途 TEXT)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS "共有建筑面积" 
                               (CID TEXT, 实际楼层 TEXT, 房号 TEXT, 主间面积 TEXT, 
                                阳台面积 TEXT, 套内面积 TEXT, 用途 TEXT)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS "幢总建筑面积" 
                               (ID TEXT, 实际楼层 TEXT, 房号 TEXT, 主间面积 TEXT, 
                                阳台面积 TEXT, 套内面积 TEXT, 用途 TEXT)''')
        
        self.conn.commit()

    def import_data(self):
        """
        从Excel文件导入数据
        
        使用QFileDialog让用户选择.xlsx文件，然后使用pandas读取文件内容。
        将读取的数据转换为列表格式并存储在self.data中。
        
        返回:
            list: 导入的数据列表，如果导入失败则返回空列表
        
        注意:
            - 仅支持.xlsx格式的文件
            - 如果用户取消选择文件，将返回空列表
            - 捕获并打印任何导入过程中的异常
        """
        # 打开文件对话框，让用户选择.xlsx文件
        file_path, _ = QFileDialog.getOpenFileName(None, "选择Excel文件", "", "Excel Files (*.xlsx)")
        
        if file_path:
            try:
                # 使用pandas读取Excel文件
                df = pd.read_excel(file_path)
                
                # 保存表头
                self.headers = df.columns.tolist()
                
                # 将DataFrame转换为列表
                self.data = df.values.tolist()
                
                print(f"成功导入数据，共{len(self.data)}行")
                return self.data
            except Exception as e:
                # 捕获并打印任何导入过程中的异常
                print(f"导入数据时出错：{str(e)}")
                return []
        else:
            # 用户取消选择文件
            print("未选择文件")
            return []

    def save_data(self, table_name):
        """
        保存数据到SQLite数据库
        
        将self.data中的数据保存到指定的SQLite数据库表中。
        如果表不存在，则创建新表；如果表已存在，则覆盖原有数据。
        
        参数:
            table_name (str): 要保存数据的表名
        
        返回:
            bool: 保存成功返回True，失败返回False
        """
        if not self.data or not self.headers:
            print("没有数据可保存")
            return False

        try:
            # 删除表中现有数据
            self.cursor.execute(f'DELETE FROM "{table_name}"')

            # 插入新数据
            placeholders = ', '.join(['?' for _ in self.headers])
            self.cursor.executemany(f'INSERT INTO "{table_name}" VALUES ({placeholders})', self.data)

            # 更新幢总建筑面积表
            self.update_total_building_area()

            self.conn.commit()
            print(f"成功保存数据到表 {table_name}，共{len(self.data)}行")
            return True
        except Exception as e:
            print(f"保存数据时出错：{str(e)}")
            return False

    def update_total_building_area(self):
        # 清空幢总建筑面积表
        self.cursor.execute('DELETE FROM "幢总建筑面积"')

        # 插入户单元套内面积数据
        self.cursor.execute('''INSERT INTO "幢总建筑面积" 
                               SELECT 'H' || HID, 实际楼层, 房号, 主间面积, 阳台面积, 套内面积, 用途 
                               FROM "户单元套内面积"''')

        # 插入共有建筑面积数据
        self.cursor.execute('''INSERT INTO "幢总建筑面积" 
                               SELECT 'C' || CID, 实际楼层, 房号, 主间面积, 阳台面积, 套内面积, 用途 
                               FROM "共有建筑面积"''')

    def __del__(self):
        # 确保在对象被销毁时关闭数据库连接
        self.conn.close()

    def get_table_names(self):
        """获取数据库中所有表的名称"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in self.cursor.fetchall()]

    def fetch_data_from_table(self, table_name):
        """从指定表中获取ID、房号和套内面积数据"""
        self.cursor.execute(f"SELECT ID, 房号, 套内面积 FROM '{table_name}'")
        return self.cursor.fetchall()

    def save_allocation_data(self, allocation_name, data):
        """保存分配数据到新表"""
        table_name = f"分摊所属_{allocation_name}"
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS '{table_name}' (group_name TEXT, ID TEXT, 房号 TEXT, 套内面积 TEXT)")
        self.cursor.execute(f"DELETE FROM '{table_name}'")
        self.cursor.executemany(f"INSERT INTO '{table_name}' (group_name, ID, 房号, 套内面积) VALUES (?, ?, ?, ?)", data)
        self.conn.commit()
        return table_name
