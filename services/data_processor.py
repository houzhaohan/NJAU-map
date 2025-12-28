"""处理地图数据和路线规划"""

import json
import geopandas as gpd
import config
import requests

class DataProcessor:
    def __init__(self):
        """初始化数据处理器"""
        self.shapefile_path = config.SHAPEFILE_PATH
        self.geojson_path = config.GEOJSON_PATH
        
    def load_shapefile(self):
        """加载SHP文件数据"""
        try:
            gdf = gpd.read_file(self.shapefile_path)
            return gdf
        except Exception as e:
            print(f"加载SHP文件失败: {e}")
            return None
    
    def load_geojson(self):
        """加载GeoJSON文件数据"""
        try:
            with open(self.geojson_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
            return geojson_data
        except Exception as e:
            print(f"加载GeoJSON文件失败: {e}")
            return None
    
    def convert_shapefile_to_geojson(self):
        """将SHP文件转换为GeoJSON格式"""
        try:
            gdf = self.load_shapefile()
            if gdf is not None:
                geojson_data = json.loads(gdf.to_json())
                return geojson_data
            return None
        except Exception as e:
            print(f"转换SHP文件到GeoJSON失败: {e}")
            return None
    
    def get_points_of_interest(self):
        """获取所有兴趣点"""
        geojson_data = self.load_geojson()
        if geojson_data:
            points = []
            for feature in geojson_data['features']:
                if feature['geometry']['type'] == 'Point':
                    points.append({
                        'id': feature['properties'].get('id', ''),
                        'name': feature['properties'].get('name', ''),
                        'type': feature['properties'].get('type', ''),
                        'address': feature['properties'].get('address', ''),
                        'coordinates': feature['geometry']['coordinates']
                    })
            return points
        return []
    
    def plan_route(self, start_point_id, end_point_id, route_type='walking'):
        """规划从起点到终点的路线
        
        Args:
            start_point_id: 起点ID
            end_point_id: 终点ID
            route_type: 路线类型，可选值：walking(步行)、driving(驾车)、bicycling(骑行)
            
        Returns:
            路线GeoJSON数据
        """
        points = self.get_points_of_interest()
        
        # 查找起点和终点
        start_point = None
        end_point = None
        
        for point in points:
            if point['id'] == start_point_id:
                start_point = point
            if point['id'] == end_point_id:
                end_point = point
        
        if not start_point or not end_point:
            return None
            
        # 使用高德API进行路线规划
        route_data = self.get_amap_route(
            start_point['coordinates'], 
            end_point['coordinates'],
            route_type
        )
        
        if not route_data:
            return None
            
        # 创建路线GeoJSON
        route = {
            "type": "Feature",
            "properties": {
                "start": start_point['name'],
                "end": end_point['name'],
                "color": config.ROUTE_COLORS.get(route_type, 'blue'),
                "width": config.ROUTE_WIDTH,
                "route_type": route_type,
                "distance": route_data.get('distance', '0'),
                "duration": route_data.get('duration', '0')
            },
            "geometry": {
                "type": "LineString",
                "coordinates": route_data.get('path', [])
            }
        }
        
        return route
        
    def get_amap_route(self, start_coords, end_coords, route_type='walking'):
        """使用高德API获取路线规划
        
        Args:
            start_coords: 起点坐标 [经度, 纬度]
            end_coords: 终点坐标 [经度, 纬度]
            route_type: 路线类型，可选值：walking(步行)、driving(驾车)、bicycling(骑行)
        
        Returns:
            路线数据，包含path(坐标点列表)、distance(距离)、duration(时间)
        """
        # 确保路线类型有效
        if route_type not in config.AMAP_ROUTE_TYPES:
            route_type = 'walking'
            
        # 构建API URL，骑行api与另外两种不一样
        if route_type == 'bicycling':
            api_url = config.BICYCLING_API_URL
            params = {
                'key': config.AMAP_API_KEY,
                'origin': f"{start_coords[0]},{start_coords[1]}",
                'destination': f"{end_coords[0]},{end_coords[1]}"
            }
            print(f"正在请求骑行路线API: {api_url}, 参数: {params}")
        else:
            api_url = config.AMAP_ROUTE_API_URL + config.AMAP_ROUTE_TYPES[route_type]
            # 构建请求参数
            params = {
                'key': config.AMAP_API_KEY,
                'origin': f"{start_coords[0]},{start_coords[1]}",
                'destination': f"{end_coords[0]},{end_coords[1]}",
                'output': 'json',
                'extensions': 'all'
            }
            
        try:
            # 发送请求
            response = requests.get(api_url, params=params)
            print(f"API响应状态码: {response.status_code}")
            print(f"API响应内容: {response.text}")
            
            # 尝试解析JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                print(f"无法解析API响应为JSON: {response.text}")
                return None
            
            # 检查响应状态
            if route_type == 'bicycling':
                # v4版本API的响应结构不同，状态码可能在不同的位置
                if data.get('errcode') != 0:
                    print(f"高德骑行API请求失败: 错误码={data.get('errcode')}, 错误信息={data.get('errmsg')}")
                    return None
                return self._parse_bicycling_route(data)
            else:
                if data.get('status') != '1':
                    print(f"高德API请求失败: {data.get('info')}")
                    return None
                    
                # 解析路线数据
                if route_type == 'walking':
                    return self._parse_walking_route(data)
                elif route_type == 'driving':
                    return self._parse_driving_route(data)
                
            return None
        except Exception as e:
            print(f"获取高德路线规划失败: {e}")
            return None
            
    def _parse_walking_route(self, data):
        """解析步行路线数据"""
        try:
            route = data['route']
            path = route['paths'][0]
            
            # 提取路径坐标
            coordinates = []
            for step in path['steps']:
                polyline_str = step['polyline']
                points = polyline_str.split(';')
                for point in points:
                    lng, lat = point.split(',')
                    coordinates.append([float(lng), float(lat)])
            
            return {
                'path': coordinates,
                'distance': path['distance'],
                'duration': path['duration']
            }
        except Exception as e:
            print(f"解析步行路线失败: {e}")
            return None
            
    def _parse_driving_route(self, data):
        """解析驾车路线数据"""
        try:
            route = data['route']
            path = route['paths'][0]
            
            # 提取路径坐标
            coordinates = []
            for step in path['steps']:
                polyline_str = step['polyline']
                points = polyline_str.split(';')
                for point in points:
                    lng, lat = point.split(',')
                    coordinates.append([float(lng), float(lat)])
            
            return {
                'path': coordinates,
                'distance': path['distance'],
                'duration': path['duration']
            }
        except Exception as e:
            print(f"解析驾车路线失败: {e}")
            return None
            
    def _parse_bicycling_route(self, data):
        """解析骑行路线数据"""
        try:
            print(f"开始解析骑行路线数据: {data}")
            # v4版本API的响应结构是{'data': {'paths': [...]}}，状态码在data对象之外
            if 'data' in data and 'paths' in data['data'] and len(data['data']['paths']) > 0:
                path = data['data']['paths'][0]
                
                # 提取路径坐标
                coordinates = []
                if 'steps' in path:
                    for step in path['steps']:
                        if 'polyline' in step:
                            polyline_str = step['polyline']
                            points = polyline_str.split(';')
                            for point in points:
                                try:
                                    lng, lat = point.split(',')
                                    coordinates.append([float(lng), float(lat)])
                                except Exception as inner_e:
                                    print(f"解析坐标点失败: {point}, 错误: {inner_e}")
                                    continue
                
                result = {
                    'path': coordinates,
                    'distance': path.get('distance', 0),
                    'duration': path.get('duration', 0)
                }
                print(f"解析骑行路线成功，路径点数量: {len(coordinates)}, 距离: {result['distance']}, 时间: {result['duration']}")
                return result
            
            print(f"骑行路线数据结构不符合预期: {data}")
            return None
        except Exception as e:
            print(f"解析骑行路线失败: {e}")
            return None