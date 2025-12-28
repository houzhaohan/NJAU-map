# 南农智慧地图系统

## 一、使用说明

配置完config.py后运行app.py，当前为调试模式

可以双击start.bat启动批处理文件

![1-1](docs/images/1-1.png)



浏览器打开 http://127.0.0.1:7777

![1-2](docs/images/1-2.png)

![1-3](docs/images/1-3.png)

1-4



注册账号

![1-5](docs/images/1-5.png)



登录账号后，所有的记录都会保存到MySQL数据库中

点击地图上的点，可以收藏该点

![2-1](docs/images/2-1.png)



可以在下拉框中选择起点和终点

![2-2](docs/images/2-2.png)



例如：信息管理学院到园艺学院

![2-3](docs/images/2-3.png)

![2-4](docs/images/2-4.png)



也可以用自然语言路线规划输入指令，进行模糊检索

此处使用的是deepseek api

输入一段文字，例如：信管院到园艺院

![2-5](docs/images/2-5.png)

![2-6](docs/images/2-6.png)



可以查看历史记录
![3-1](docs/images/3-1.png)



点击收藏路线

再点击我的收藏

可以看到之前收藏的地点和路线

![3-2](docs/images/3-2.png)

点击查看兴趣点，会在地图上显示这个兴趣点的信息

点击查看路线，会在地图上复现这个路线



管理员登录

![4-1](docs/images/4-1.png)



管理员面板

![4-2](docs/images/4-2.png)



## 二、安装说明

- 当前开发环境 python 3.12
- 后端框架flask，前端没有使用框架（HTML/CSS/JavaScript）
- 所需要的第三方库在requirements.txt
- 数据库 MySQL
- 操作系统 Windows



> 需求分析报告、详细设计报告、系统安装说明、系统使用说明在docs文件夹中


> map_data文件夹中的数据为2025年11月地图数据，后续不再更新


> 管理信息系统实践课小组作业

