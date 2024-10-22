import sys
from PyQt5.QtWidgets import QApplication
from model import BuildingAreaModel
from controller import BuildingAreaController
from MainWindow import MainWindow

def main():
    """
    主函数：程序的入口点
    
    创建并初始化应用程序的主要组件，包括模型、视图和控制器。
    遵循MVC（模型-视图-控制器）设计模式，实现了程序各部分的解耦。
    """
    # 创建应用程序实例
    # 这是PyQt5应用程序的标准起点，管理整个GUI程序的生命周期
    app = QApplication(sys.argv)
    
    # 创建模型实例
    # BuildingAreaModel负责处理数据逻辑，如数据的导入和管理
    model = BuildingAreaModel()
    
    # 创建控制器实例，并将模型传递给它
    # BuildingAreaController负责协调模型和视图之间的交互
    controller = BuildingAreaController(model, None)  # 先创建controller，暂时传入None作为view
    
    # 创建主窗口(视图)实例
    # MainWindow类定义了应用程序的用户界面
    view = MainWindow(controller)  # 传递controller给MainWindow
    
    # 设置controller的view
    controller.set_view(view)  # 设置view并连接信号
    
    # 显示主窗口
    # 这使得用户界面可见
    view.show()
    
    # 运行应用程序的事件循环
    # 这保持应用程序运行，直到用户关闭它
    # sys.exit()确保应用程序干净地退出，返回退状态码给操作系统
    sys.exit(app.exec_())

if __name__ == "__main__":
    """
    程序执行的起点
    
    当这个脚本作为主程序运行时（而不是作为模块导入时），
    将调用main()函数来启动应用程序。
    """
    main()
