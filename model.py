import pandas as pd
from PyQt5.QtWidgets import QFileDialog
import sqlite3
import re

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
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS "分摊面积" 
                               (ID TEXT PRIMARY KEY, 房号 TEXT, 套内面积 TEXT)''')
        
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
        """保存分配数据到多个表"""
        base_table_name = f"分摊所属_{allocation_name}"
        
        # 按 group_name 分组数据
        grouped_data = {}
        for item in data:
            group_name, id, room, area = item
            if group_name not in grouped_data:
                grouped_data[group_name] = []
            grouped_data[group_name].append((id, room, area))

        # 为每个组创建一个表并保存数据
        created_tables = []
        for group_name, group_data in grouped_data.items():
            table_name = f"{base_table_name}_{group_name}"
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS '{table_name}' (ID TEXT, 房号 TEXT, 套内面积 TEXT)")
            self.cursor.execute(f"DELETE FROM '{table_name}'")
            self.cursor.executemany(f"INSERT INTO '{table_name}' (ID, 房号, 套内面积) VALUES (?, ?, ?)", group_data)
            created_tables.append(table_name)

        self.conn.commit()
        return created_tables

    def delete_allocation_tables(self, allocation_name):
        """删除与指定分摊所属相关的所有数据表"""
        base_table_name = f"分摊所属_{allocation_name}"
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?", (f"{base_table_name}%",))
        tables_to_delete = self.cursor.fetchall()
        
        for (table_name,) in tables_to_delete:
            self.cursor.execute(f"DROP TABLE IF EXISTS '{table_name}'")
        
        self.conn.commit()
        return [table[0] for table in tables_to_delete]

    def get_allocation_options(self):
        """获取分摊所属选项"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '分摊所属_%'")
        tables = self.cursor.fetchall()
        
        options = set()
        for (table,) in tables:
            match = re.match(r'分摊所属_(.+?)_', table)
            if match:
                options.add(match.group(1))
        
        return list(options)

    def get_allocation_tables(self, option):
        """获取指定分摊所属选项的相关数据表"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?", (f'分摊所属_{option}_%',))
        tables = self.cursor.fetchall()
        return [table[0] for table in tables]

    def get_total_area(self, tables):
        total_area = 0
        for table in tables:
            self.cursor.execute(f"SELECT SUM(CAST(套内面积 AS FLOAT)) FROM '{table}'")
            result = self.cursor.fetchone()
            if result[0]:
                total_area += result[0]
        return total_area

    def save_apportionment_coefficient(self, tables, coefficient, model_type):
        # 创建或更新"分摊面积"表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS "分摊面积" 
                               (ID TEXT PRIMARY KEY, 房号 TEXT, 套内面积 TEXT)''')

        # 添加新的分摊系数列和分摊公共面积列（如果不存在）
        coefficient_column = f"{model_type}_分摊系数"
        area_column = f"{model_type}_分摊公共面积"
        self.cursor.execute(f"PRAGMA table_info('分摊面积')")
        columns = [row[1] for row in self.cursor.fetchall()]
        if coefficient_column not in columns:
            self.cursor.execute(f"ALTER TABLE '分摊面积' ADD COLUMN '{coefficient_column}' TEXT")
        if area_column not in columns:
            self.cursor.execute(f"ALTER TABLE '分摊面积' ADD COLUMN '{area_column}' TEXT")

        # 将系数格式化为保留6位小数的字符串
        formatted_coefficient = f"{coefficient:.6f}"

        # 更新或插入数据
        for table in tables:
            self.cursor.execute(f"SELECT ID, 房号, 套内面积 FROM '{table}'")
            rows = self.cursor.fetchall()
            for row in rows:
                # 计算分摊公共面积
                inner_area = float(row[2])
                apportioned_area = inner_area * coefficient
                formatted_apportioned_area = f"{apportioned_area:.2f}"  # 修改为保留2位小数

                # 检查是否已存在该 ID 的记录
                self.cursor.execute("SELECT * FROM '分摊面积' WHERE ID = ?", (row[0],))
                existing_record = self.cursor.fetchone()
                
                if existing_record:
                    # 如果记录已存在，更新它
                    self.cursor.execute(f'''UPDATE "分摊面积" 
                                            SET 房号 = ?, 套内面积 = ?, '{coefficient_column}' = ?, '{area_column}' = ?
                                            WHERE ID = ?''', 
                                        (row[1], row[2], formatted_coefficient, formatted_apportioned_area, row[0]))
                else:
                    # 如果记录不存在，插入新记录
                    self.cursor.execute(f'''INSERT INTO "分摊面积" 
                                            (ID, 房号, 套内面积, '{coefficient_column}', '{area_column}')
                                            VALUES (?, ?, ?, ?, ?)''', 
                                        (row[0], row[1], row[2], formatted_coefficient, formatted_apportioned_area))

        self.conn.commit()

    def delete_apportionment_model_data(self, model_name):
        """删除与指定分摊模型相关的数据列"""
        try:
            # 获取"分摊面积"表的列信息
            self.cursor.execute("PRAGMA table_info('分摊面积')")
            columns = [row[1] for row in self.cursor.fetchall()]

            # 找到与模型相关的列
            coefficient_column = f"{model_name}_分摊系数"
            area_column = f"{model_name}_分摊公共面积"
            columns_to_delete = []

            if coefficient_column in columns:
                columns_to_delete.append(coefficient_column)
            if area_column in columns:
                columns_to_delete.append(area_column)

            if columns_to_delete:
                # 创建新表，不包含要删除的列
                new_columns = [col for col in columns if col not in columns_to_delete]
                new_columns_str = ', '.join(new_columns)
                self.cursor.execute(f"CREATE TABLE temp_分摊面积 AS SELECT {new_columns_str} FROM '分摊面积'")

                # 删除旧表，重命名新表
                self.cursor.execute("DROP TABLE '分摊面积'")
                self.cursor.execute("ALTER TABLE temp_分摊面积 RENAME TO '分摊面积'")

                self.conn.commit()
                return columns_to_delete
            else:
                return []
        except Exception as e:
            print(f"删除分摊模型数据时出错：{str(e)}")
            self.conn.rollback()
            raise

    def get_calculated_coefficients(self):
        """获取已计算的分摊系数"""
        self.cursor.execute("PRAGMA table_info('分摊面积')")
        columns = [row[1] for row in self.cursor.fetchall()]
        coefficient_columns = [col for col in columns if col.endswith('_分摊系数')]
        
        coefficients = []
        for col in coefficient_columns:
            model_name = col.replace('_分摊系数', '')
            self.cursor.execute(f"SELECT DISTINCT {col} FROM '分摊面积' WHERE {col} IS NOT NULL")
            result = self.cursor.fetchone()
            if result:
                coefficients.append((model_name, result[0]))
        
        return coefficients
