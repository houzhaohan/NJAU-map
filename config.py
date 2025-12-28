"""配置文件"""

# 高德地图API配置
AMAP_API_KEY = '填写高德地图api'
AMAP_ROUTE_API_URL = 'https://restapi.amap.com/v3/direction'
BICYCLING_API_URL = 'https://restapi.amap.com/v4/direction/bicycling'  # 骑行api与其他类型不一样，我也不知道为什么

# 高德路线规划类型
AMAP_ROUTE_TYPES = {
    'walking': '/walking',  # 步行
    'driving': '/driving',  # 驾车
    'bicycling': '/bicycling'  # 骑行
}

# deepseek API配置
DEEPSEEK_API_KEY = '填写deepseek api'
DEEPSEEK_ROUTE_API_URL = 'https://api.deepseek.com/chat/completions'

# 地图数据配置
SHAPEFILE_PATH = './map_data/NJAU.shp'
GEOJSON_PATH = './map_data/NJAU.geojson'

# 服务器配置
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 7777  # 端口号
DEBUG = True  # 调试模式

# 路线规划配置
ROUTE_COLORS = {
    'walking': 'green',
    'driving': 'blue',
    'bicycling': 'orange'
}
ROUTE_WIDTH = 3

# mysql数据库配置
DB_CONFIG = {
    "host": "localhost",      # 数据库服务器地址
    "user": "root",           # 数据库用户名
    "password": "填写数据库密码",     # 数据库密码
    "database": "map_db",     # 数据库名称
    "port": 3306,             # MySQL服务端口
}

# 管理员账户密码
# admin
# admin123
