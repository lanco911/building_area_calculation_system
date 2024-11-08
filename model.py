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
        """初始化数据库表结构"""
        try:
            # 创建户单元套内面积表
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS "户单元套内面积" 
                                 (HID TEXT PRIMARY KEY, 
                                  实际楼层 TEXT, 
                                  房号 TEXT, 
                                  主间面积 TEXT, 
                                  阳台面积 TEXT, 
                                  套内面积 TEXT, 
                                  用途 TEXT)''')
            
            # 创建共有建筑面积表
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS "共有建筑面积" 
                                 (CID TEXT PRIMARY KEY, 
                                  实际楼层 TEXT, 
                                  房号 TEXT, 
                                  主间面积 TEXT, 
                                  阳台面积 TEXT, 
                                  套内面积 TEXT, 
                                  用途 TEXT)''')
            
            # 创建幢总建筑面积表
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS "幢总建筑面积" 
                                 (ID TEXT PRIMARY KEY, 
                                  实际楼层 TEXT, 
                                  房号 TEXT, 
                                  主间面积 TEXT, 
                                  阳台面积 TEXT, 
                                  套内面积 TEXT, 
                                  用途 TEXT)''')
            
            
            # 创建分摊模型关系表
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS "分摊模型关系" 
                                 (model_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  model_name TEXT NOT NULL,
                                  parent_id INTEGER,
                                  order_index INTEGER NOT NULL,
                                  FOREIGN KEY (parent_id) REFERENCES "分摊模型关系" (model_id))''')
            
            # 创建新的分摊所属关系表，增加 belong_alias 列
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS "分摊所属关系" 
                                 (belong_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  belong_name TEXT NOT NULL,
                                  belong_alias TEXT NOT NULL,
                                  parent_id INTEGER,
                                  order_index INTEGER NOT NULL,
                                  FOREIGN KEY (parent_id) REFERENCES "分摊所属关系" (belong_id))''')
            
            # 检查是否已存在整幢记录
            self.cursor.execute('''SELECT belong_id FROM "分摊所属关系" 
                                 WHERE belong_name = "分摊所属_整幢"''')
            if not self.cursor.fetchone():
                # 添加整幢记录作为默认记录，设置别名
                self.cursor.execute('''INSERT INTO "分摊所属关系" 
                                     (belong_name, belong_alias, parent_id, order_index)
                                     VALUES ("分摊所属_整幢", "整幢", NULL, 0)''')
            
            # 创建分摊系数计算过程表，确保分摊系数列在套内面积列之后
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS "分摊系数计算过程" 
                                 (ID TEXT PRIMARY KEY, 
                                  房号 TEXT, 
                                  套内面积 TEXT,
                                  分摊系数 TEXT)''')
            
            self.conn.commit()
        except Exception as e:
            print(f"初始化表时出错：{str(e)}")
            self.conn.rollback()

    def import_data(self):
        """
        从Excel文件导入数据
        
        使用QFileDialog让用户选择.xlsx文件，然后使用pandas读取文件内容。
        将读取的数据转换为列表格式并存储在self.data中。
        
        返回:
            list: 导入的数据列表，如导入失败则返回空列表
        
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

            # 更新整幢所有单元数据
            self.save_total_building_units()

            self.conn.commit()
            print(f"成功保存数据到表 {table_name}，共{len(self.data)}行")
            return True
        except Exception as e:
            print(f"保存数据时出错：{str(e)}")
            return False

    def update_total_building_area(self):
        """更新幢总建筑面积表"""
        try:
            # 清空幢总建筑面积表
            self.cursor.execute('DELETE FROM "幢总建筑面积"')

            # 插入户单元套内面积数据
            self.cursor.execute('''INSERT INTO "幢总建筑面积" 
                                 (ID, 实际楼层, 房号, 主间面积, 阳台面积, 套内面积, 用途)
                                 SELECT 'H' || HID, 实际楼层, 房号, 主间面积, 阳台面积, 套内面积, 用途 
                                 FROM "户单元套内面积"''')

            # 插入共有建筑面积数据
            self.cursor.execute('''INSERT INTO "幢总建筑面积" 
                                 (ID, 实际楼层, 房号, 主间面积, 阳台面积, 套内面积, 用途)
                                 SELECT 'C' || CID, 实际楼层, 房号, 主间面积, 阳台面积, 套内面积, 用途 
                                 FROM "共有建筑面积"''')

            self.conn.commit()
        except Exception as e:
            print(f"更新幢总建筑面积表时出错：{str(e)}")
            self.conn.rollback()

    def __del__(self):
        # 确保在对象被销毁时关闭数据库连接
        self.conn.close()

    def get_table_names(self):
        """获取数据库中所表的名称"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in self.cursor.fetchall()]

    def fetch_data_from_table(self, table_name):
        """从指定表中获取数据"""
        try:
            # 根据表名确定ID字段名
            id_field = "HID" if table_name == "户单元套内面积" else "CID" if table_name == "共有建筑面积" else "ID"
            
            # 执行查询
            self.cursor.execute(f"SELECT {id_field}, 房号, 套内面积 FROM '{table_name}'")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"获取数据时出错：{str(e)}")
            return []

    def save_allocation_data(self, allocation_name, data, parent_table=None):
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

        # 更新分摊所属关系表
        if parent_table:
            # 获取父表的belong_id
            self.cursor.execute('''SELECT belong_id FROM "分摊所属关系" WHERE belong_name = ?''', 
                              (parent_table,))
            parent_result = self.cursor.fetchone()
            parent_id = parent_result[0] if parent_result else None

            # 如果父表不存在于关系表中，先添加父表
            if parent_id is None:
                # 创建父表的别名
                parent_alias = parent_table.replace("分摊所属_", "")
                self.cursor.execute('''INSERT INTO "分摊所属关系" 
                                     (belong_name, belong_alias, parent_id, order_index)
                                     VALUES (?, ?, NULL, 
                                            (SELECT COALESCE(MAX(order_index), 0) + 1 
                                             FROM "分摊所属关系" 
                                             WHERE parent_id IS NULL))''', 
                                  (parent_table, parent_alias))
                parent_id = self.cursor.lastrowid

            # 添加或更新当前分摊所属的记录
            for table_name in created_tables:
                # 获取当前最大的order_index
                self.cursor.execute('''SELECT COALESCE(MAX(order_index), 0) 
                                     FROM "分摊所属关系" 
                                     WHERE parent_id = ?''', 
                                  (parent_id,))
                max_order = self.cursor.fetchone()[0]

                # 创建表的别名
                table_alias = table_name.replace("分摊所属_", "")

                # 检查是否已存在记录
                self.cursor.execute('''SELECT belong_id FROM "分摊所属关系" 
                                     WHERE belong_name = ?''', 
                                  (table_name,))
                existing = self.cursor.fetchone()

                if existing:
                    # 更新现有记录
                    self.cursor.execute('''UPDATE "分摊所属关系" 
                                         SET parent_id = ?, order_index = ?, belong_alias = ?
                                         WHERE belong_id = ?''',
                                      (parent_id, max_order + 1, table_alias, existing[0]))
                else:
                    # 插入新记录
                    self.cursor.execute('''INSERT INTO "分摊所属关系" 
                                         (belong_name, belong_alias, parent_id, order_index)
                                         VALUES (?, ?, ?, ?)''',
                                      (table_name, table_alias, parent_id, max_order + 1))

        self.conn.commit()
        return created_tables

    def delete_allocation_tables(self, allocation_name):
        """删除与指定分摊所属相关的所有数据表，但保留整幢表"""
        base_table_name = f"分摊所属_{allocation_name}"
        
        # 使用递归CTE获取所有需要删除的表
        self.cursor.execute("""
            WITH RECURSIVE belong_tree AS (
                -- 基础查询：获取指定分摊所属
                SELECT belong_id, belong_name, parent_id
                FROM "分摊所属关系"
                WHERE belong_name LIKE ?
                
                UNION ALL
                
                -- 递归查询：获取子分摊所属
                SELECT c.belong_id, c.belong_name, c.parent_id
                FROM "分摊所属关系" c
                JOIN belong_tree p ON c.parent_id = p.belong_id
            )
            SELECT belong_name FROM belong_tree
        """, (f"{base_table_name}%",))
        
        tables_to_delete = set(row[0] for row in self.cursor.fetchall())
        
        # 删除表和关系记录
        deleted_tables = []
        for table_name in tables_to_delete:
            if table_name != "分摊属_整幢":
                try:
                    # 删除数据表
                    self.cursor.execute(f"DROP TABLE IF EXISTS '{table_name}'")
                    # 删除关系记录
                    self.cursor.execute('''DELETE FROM "分摊所属关系" WHERE belong_name = ?''',
                                      (table_name,))
                    deleted_tables.append(table_name)
                except Exception as e:
                    print(f"删除表 {table_name} 时出错：{str(e)}")
        
        self.conn.commit()
        return deleted_tables

    def get_allocation_options(self):
        """获取分摊所属选项，不包括整幢"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '分摊所属_%'")
        tables = self.cursor.fetchall()
        
        options = set()
        for (table,) in tables:
            # 排除整幢表
            if table != "分摊所属_整幢":
                match = re.match(r'分摊所属_(.+?)_', table)
                if match:
                    options.add(match.group(1))
        
        return list(options)

    def get_allocation_tables(self, option):
        """获取指定分摊所属选项的相关数据表，不包括整幢表"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?", (f'分摊所属_{option}_%',))
        tables = self.cursor.fetchall()
        # 过滤掉整幢表
        return [table[0] for table in tables if table[0] != "分摊所属_整幢"]

    def get_total_area(self, tables):
        total_area = 0
        for table in tables:
            self.cursor.execute(f"SELECT SUM(CAST(套内面积 AS FLOAT)) FROM '{table}'")
            result = self.cursor.fetchone()
            if result[0]:
                total_area += result[0]
        return total_area

    def save_apportionment_coefficient(self, tables, coefficient, model_type):
        # 创建或更新"分摊系数计算过程"表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS "分摊系数计算过程" 
                               (ID TEXT PRIMARY KEY, 房号 TEXT, 套内面积 TEXT)''')

        # 添加新的分摊系数列和分摊公共面积列（如果不存在）
        coefficient_column = f"{model_type}_分摊系数"
        area_column = f"{model_type}_分摊公共面积"
        self.cursor.execute(f"PRAGMA table_info('分摊系数计算过程')")
        columns = [row[1] for row in self.cursor.fetchall()]
        if coefficient_column not in columns:
            self.cursor.execute(f"ALTER TABLE '分摊系数计算过程' ADD COLUMN '{coefficient_column}' TEXT")
        if area_column not in columns:
            self.cursor.execute(f"ALTER TABLE '分摊系数计算过程' ADD COLUMN '{area_column}' TEXT")

        # 将系数格式化为保留6位小数的字符串
        formatted_coefficient = f"{coefficient:.6f}"

        # 更新或插入数
        for table in tables:
            self.cursor.execute(f"SELECT ID, 房号, 套内面积 FROM '{table}'")
            rows = self.cursor.fetchall()
            for row in rows:
                # 计算分摊公共面积
                inner_area = float(row[2])
                apportioned_area = inner_area * coefficient
                formatted_apportioned_area = f"{apportioned_area:.2f}"  # 修改为保留2位小数

                # 检查是否已存在该 ID 的记录
                self.cursor.execute("SELECT * FROM '分摊系数计算过程' WHERE ID = ?", (row[0],))
                existing_record = self.cursor.fetchone()
                
                if existing_record:
                    # 如果记录已存在，更新它
                    self.cursor.execute(f'''UPDATE "分摊系数计算过程" 
                                            SET 房号 = ?, 套内面积 = ?, '{coefficient_column}' = ?, '{area_column}' = ?
                                            WHERE ID = ?''', 
                                        (row[1], row[2], formatted_coefficient, formatted_apportioned_area, row[0]))
                else:
                    # 如果记录不存在，插入新记录
                    self.cursor.execute(f'''INSERT INTO "分摊系数计算过程" 
                                            (ID, 房号, 套内面积, '{coefficient_column}', '{area_column}')
                                            VALUES (?, ?, ?, ?, ?)''', 
                                        (row[0], row[1], row[2], formatted_coefficient, formatted_apportioned_area))

        self.conn.commit()

        # 更新总分摊系数
        self.update_total_coefficient()

    def calculate_and_save_apportionable_area(self, tables, upper_coefficient, model_type):
        """计算并保存应分摊公共面积"""
        try:
            # 创建或更新"分摊系数计算过程"表
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS "分摊系数计算过程" 
                                 (ID TEXT PRIMARY KEY, 房号 TEXT, 套内面积 TEXT)''')
            
            # 添加新的应分摊公共面积列（如果不存在）
            area_column = f"{model_type}_应分摊公共面积"
            self.cursor.execute(f"PRAGMA table_info('分摊系数计算过程')")
            columns = [row[1] for row in self.cursor.fetchall()]
            if area_column not in columns:
                self.cursor.execute(f"ALTER TABLE '分摊系数计算过程' ADD COLUMN '{area_column}' TEXT")

            # 计算并保存每个ID的应分摊公共面积
            for table in tables:
                self.cursor.execute(f"SELECT ID, 房号, 套内面积 FROM '{table}'")
                rows = self.cursor.fetchall()
                for row in rows:
                    # 计算应分摊公共面积
                    inner_area = float(row[2])
                    apportionable_area = inner_area + (inner_area * upper_coefficient)
                    formatted_area = f"{apportionable_area:.2f}"  # 保留2位小数

                    # 检查是否已存在该ID的记录
                    self.cursor.execute("SELECT * FROM '分摊系数计算过程' WHERE ID = ?", (row[0],))
                    existing_record = self.cursor.fetchone()
                    
                    if existing_record:
                        # 更新现有记录
                        self.cursor.execute(f'''UPDATE "分摊系数计算过程" 
                                             SET 房号 = ?, 套内面积 = ?, '{area_column}' = ?
                                             WHERE ID = ?''', 
                                          (row[1], row[2], formatted_area, row[0]))
                    else:
                        # 构建动态SQL语句
                        columns = ["ID", "房号", "套内面积", area_column]
                        placeholders = ["?"] * len(columns)
                        sql = f'''INSERT INTO "分摊系数计算过程" ({', '.join(f'"{col}"' for col in columns)})
                                 VALUES ({', '.join(placeholders)})'''
                        self.cursor.execute(sql, (row[0], row[1], row[2], formatted_area))

                self.conn.commit()
                return True, None
        except Exception as e:
            self.conn.rollback()
            return False, str(e)

    def delete_apportionment_model_data(self, model_name):
        """删除与指定分摊模型相关的数列"""
        try:
            # 获取"分摊系数计算过程"表的列信息
            self.cursor.execute("PRAGMA table_info('分摊系数计算过程')")
            columns = [row[1] for row in self.cursor.fetchall()]

            # 找到与模型相关的列
            coefficient_column = f"{model_name}_分摊系数"
            area_column = f"{model_name}_分摊公共面积"
            apportionable_area_column = f"{model_name}_应分摊公共面积"
            columns_to_delete = []
            
            # 如果列存在，则添加到要删除的列列表中
            if coefficient_column in columns:
                columns_to_delete.append(coefficient_column)
            if area_column in columns:
                columns_to_delete.append(area_column)
            if apportionable_area_column in columns:
                columns_to_delete.append(apportionable_area_column)

            if columns_to_delete:
                # 创建新表，不包含要删除的列
                new_columns = [col for col in columns if col not in columns_to_delete]
                # 使用双引号包裹列名
                new_columns_str = ', '.join(f'"{col}"' for col in new_columns)
                self.cursor.execute(f'CREATE TABLE "temp_分摊系数计算过程" AS SELECT {new_columns_str} FROM "分摊系数计算过程"')

                # 删旧表，重命名新表
                self.cursor.execute('DROP TABLE "分摊系数计算过程"')
                self.cursor.execute('ALTER TABLE "temp_分摊系数计算过程" RENAME TO "分摊系数计算过程"')

                self.conn.commit()
                
                # 更新总分摊系数
                self.update_total_coefficient()
                
                return columns_to_delete
            else:
                return []
        except Exception as e:
            print(f"删除分摊模型数据时出错：{str(e)}")
            self.conn.rollback()
            raise

    def get_calculated_coefficients(self):
        """获取已计算的分摊系数"""
        try:
            self.cursor.execute("PRAGMA table_info('分摊系数计算过程')")
            columns = [row[1] for row in self.cursor.fetchall()]
            coefficient_columns = [col for col in columns if col.endswith('_分摊系数')]
            
            coefficients = []
            for col in coefficient_columns:
                # 使用引号包裹列名以处理特殊字符
                self.cursor.execute(f'SELECT DISTINCT "{col}" FROM "分摊系数计算过程" WHERE "{col}" IS NOT NULL')
                result = self.cursor.fetchone()
                if result:
                    model_name = col.replace('_分摊系数', '')
                    coefficients.append((model_name, result[0]))
            
            return coefficients
        except Exception as e:
            print(f"获取分摊系数时出错：{str(e)}")
            return []

    def save_apportionment_model(self, model_name, parent_model_name=None):
        """保存分摊模型及其层级关系"""
        try:
            # 获取父模型ID
            parent_id = None
            if parent_model_name:
                self.cursor.execute("SELECT model_id FROM '分摊模型关系' WHERE model_name = ?", 
                                  (parent_model_name,))
                result = self.cursor.fetchone()
                if result:
                    parent_id = result[0]
            
            # 获取当前最大的order_index
            self.cursor.execute("""
                SELECT COALESCE(MAX(order_index), 0) 
                FROM '分摊模型关系' 
                WHERE parent_id IS ? OR (parent_id IS NULL AND ? IS NULL)
            """, (parent_id, parent_id))
            max_order = self.cursor.fetchone()[0]
            
            # 插入新模型
            self.cursor.execute("""
                INSERT INTO '分摊模型关系' (model_name, parent_id, order_index)
                VALUES (?, ?, ?)
            """, (model_name, parent_id, max_order + 1))
            
            self.conn.commit()
            return True, "分摊模型保存成功"
        except Exception as e:
            return False, f"保存分摊模型失败: {str(e)}"

    def get_model_hierarchy(self):
        """获取分摊模型的层级结构"""
        self.cursor.execute("""
            WITH RECURSIVE model_tree AS (
                -- 基础查询：获取顶级模型
                SELECT 
                    model_id, 
                    model_name, 
                    parent_id, 
                    order_index,
                    0 as level,
                    CAST(order_index AS TEXT) as path
                FROM '分摊模型关系'
                WHERE parent_id IS NULL
                
                UNION ALL
                
                -- 递归查询：获取子模型
                SELECT 
                    t.model_id, 
                    t.model_name, 
                    t.parent_id, 
                    t.order_index,
                    mt.level + 1,
                    mt.path || '.' || CAST(t.order_index AS TEXT)
                FROM '分摊模型关系' t
                JOIN model_tree mt ON t.parent_id = mt.model_id
            )
            SELECT model_id, model_name, parent_id, level, path
            FROM model_tree
            ORDER BY path;
        """)
        return self.cursor.fetchall()

    def get_child_models(self, model_name):
        """取指定模型的所有子模型"""
        try:
            # 首先获取当前模型的ID
            self.cursor.execute("""
                WITH RECURSIVE model_tree AS (
                    -- 基础查询：获取指定模型
                    SELECT 
                        model_id, 
                        model_name,
                        parent_id
                    FROM '分摊模型关系'
                    WHERE model_name = ?
                    
                    UNION ALL
                    
                    -- 递归查询：获取子模型
                    SELECT 
                        t.model_id, 
                        t.model_name,
                        t.parent_id
                    FROM '分摊模型关系' t
                    JOIN model_tree mt ON t.parent_id = mt.model_id
                )
                SELECT model_name
                FROM model_tree
                WHERE model_name != ?;
            """, (model_name, model_name))
            
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"获取子模型时出错：{str(e)}")
            return []

    def delete_model_relationship(self, model_name):
        """删除模型及其子模型的关系记录"""
        try:
            # 获取要删除的模型ID
            self.cursor.execute("SELECT model_id FROM '分摊模型关系' WHERE model_name = ?", (model_name,))
            model_id = self.cursor.fetchone()
            
            if model_id:
                model_id = model_id[0]
                # 删除该模型及其所有子模型的关系记录
                self.cursor.execute("""
                    WITH RECURSIVE model_tree AS (
                        SELECT model_id FROM '分摊模型关系' WHERE model_id = ?
                        UNION ALL
                        SELECT t.model_id 
                        FROM '分摊模型关系' t
                        JOIN model_tree mt ON t.parent_id = mt.model_id
                    )
                    DELETE FROM '分摊模型关系'
                    WHERE model_id IN (SELECT model_id FROM model_tree);
                """, (model_id,))
                
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"删除模型关系时出错：{str(e)}")
            self.conn.rollback()
            return False

    def save_total_building_units(self):
        """保存整幢所有单元数据到分摊所属表"""
        try:
            # 创建分摊所属_整幢表
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS "分摊所属_整幢" 
                                 (ID TEXT, 房号 TEXT, 套内面积 TEXT)''')
            
            # 从幢总建筑面积表获取数据并保存
            self.cursor.execute('''DELETE FROM "分摊所属_整幢"''')
            self.cursor.execute('''INSERT INTO "分摊所属_整幢" 
                                 (ID, 房号, 套内面积)
                                 SELECT ID, 房号, 套内面积 
                                 FROM "幢总建筑面积"''')
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"保存整幢数据时出错：{str(e)}")
            self.conn.rollback()
            return False

    def get_available_belong_tables(self):
        """获取可用于加载的分摊所属表"""
        try:
            # 使用子查询找出所有作为父表的belong_id
            self.cursor.execute('''
                WITH parent_ids AS (
                    SELECT DISTINCT parent_id 
                    FROM "分摊所属关系" 
                    WHERE parent_id IS NOT NULL
                )
                SELECT belong_name, belong_alias
                FROM "分摊所属关系"
                WHERE belong_id NOT IN (SELECT parent_id FROM parent_ids)
                AND belong_alias NOT LIKE '%_分摊公共建筑部位'
                ORDER BY order_index
            ''')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"获取可用分摊所属表时出错：{str(e)}")
            return []

    def update_total_coefficient(self):
        """更新每个ID的总分摊系数，确保分摊系数列位于套内面积列之后"""
        try:
            # 获取当前表的所有列信息
            self.cursor.execute("PRAGMA table_info('分摊系数计算过程')")
            columns = [row[1] for row in self.cursor.fetchall()]
            
            # 如果"分摊系数"列已存在，先删除它
            if "分摊系数" in columns:
                # 创建临时表，不包含"分摊系数"列
                new_columns = [col for col in columns if col != "分摊系数"]
                # 使用双引号包裹列名
                new_columns_str = ', '.join(f'"{col}"' for col in new_columns)
                self.cursor.execute(f'CREATE TABLE "temp_分摊系数计算过程" AS SELECT {new_columns_str} FROM "分摊系数计算过程"')
                self.cursor.execute('DROP TABLE "分摊系数计算过程"')
                self.cursor.execute('ALTER TABLE "temp_分摊系数计算过程" RENAME TO "分摊系数计算过程"')
                
                # 更新列信息
                self.cursor.execute("PRAGMA table_info('分摊系数计算过程')")
                columns = [row[1] for row in self.cursor.fetchall()]

            # 获取所有以"_分摊系数"结尾的列
            coefficient_columns = [col for col in columns if col.endswith('_分摊系数')]

            # 在"套内面积"列后添加"分摊系数"列
            self.cursor.execute('ALTER TABLE "分摊系数计算过程" ADD COLUMN "分摊系数" TEXT')

            # 如果没有分摊系数列，将总系数设为0
            if not coefficient_columns:
                self.cursor.execute('UPDATE "分摊系数计算过程" SET "分摊系数" = "0"')
                self.conn.commit()
                return

            # 构建SQL语句，计算所有分摊系数的和
            coeff_sum = " + ".join([f'CAST(COALESCE("{col}", "0") AS FLOAT)' 
                                   for col in coefficient_columns])
            update_sql = f'''
                UPDATE "分摊系数计算过程"
                SET "分摊系数" = ROUND(({coeff_sum}), 6)
            '''
            
            self.cursor.execute(update_sql)
            self.conn.commit()
        except Exception as e:
            print(f"更新总分摊系数时出错：{str(e)}")
            self.conn.rollback()
