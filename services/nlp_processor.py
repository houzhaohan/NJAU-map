"""自然语言处理服务，用于解析用户的自然语言路线规划请求"""

import re
import json
import requests
import config
import jieba
from services.data_processor import DataProcessor

class NLPProcessor:
    def __init__(self):
        """初始化NLP处理器"""
        self.api_key = config.DEEPSEEK_API_KEY
        self.api_url = config.DEEPSEEK_ROUTE_API_URL
        self.data_processor = DataProcessor()
        self.points_data = self.data_processor.get_points_of_interest()
    
    def parse_nlp_instruction(self, instruction):
        """解析用户的自然语言指令，提取起点和终点信息
        
        Args:
            instruction: 用户输入的自然语言指令
        
        Returns:
            dict: 包含start和end的字典，如果解析失败则返回None
        """
        try:
            # 直接调用DeepSeek API解析指令
            print(f"使用DeepSeek API解析指令: {instruction}")
            
            # 检查API密钥和URL是否配置
            if not self.api_key or not self.api_url:
                print("DeepSeek API配置不完整，无法进行API调用")
                return None
            
            # 调用DeepSeek API解析指令
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            # 构建请求体，符合标准DeepSeek API格式
            prompt = f"""请从以下路线规划指令中提取起点和终点信息，并以JSON格式返回，不要添加额外说明。
            指令: {instruction}
            期望输出格式: {{"start": "起点", "end": "终点"}}
            """
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }
            
            try:
                # 发送请求，设置超时
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)
                response_data = response.json()
                
                # 检查响应是否成功
                if response.status_code != 200:
                    print(f"DeepSeek API调用失败，状态码: {response.status_code}")
                    print(f"响应内容: {response_data}")
                    return None
                
                # 提取响应内容
                if 'choices' not in response_data or not response_data['choices']:
                    print("DeepSeek API响应格式不正确，缺少choices字段")
                    return None
                
                try:
                    # 提取生成的内容
                    content = response_data['choices'][0]['message']['content']
                    
                    # 尝试解析JSON格式的响应
                    parsed_data = json.loads(content)
                    start_location = parsed_data.get('start')
                    end_location = parsed_data.get('end')
                    
                    if not start_location or not end_location:
                        print("未能从指令中提取有效的起点和终点")
                        print(f"API返回内容: {content}")
                        return None
                    
                    return {
                        'start': start_location,
                        'end': end_location
                    }
                except json.JSONDecodeError as je:
                    print(f"解析DeepSeek API返回的JSON失败: {je}")
                    print(f"API返回内容: {content if 'content' in locals() else response_data}")
                    return None
            except requests.exceptions.ConnectionError as ce:
                print(f"DeepSeek API连接失败: {ce}")
                return None
            except requests.exceptions.Timeout as te:
                print(f"DeepSeek API请求超时: {te}")
                return None
            except requests.exceptions.RequestException as e:
                print(f"DeepSeek API请求异常: {e}")
                return None
        except Exception as e:
            print(f"解析自然语言指令失败: {e}")
            return None
            
    def _parse_instruction_manually(self, instruction):
        """手动解析自然语言指令，提取起点和终点
        
        Args:
            instruction: 用户输入的自然语言指令
        
        Returns:
            dict: 包含start和end的字典，如果解析失败则返回None
        """
        try:
            # 转换为小写进行处理，这一行没用
            instruction_lower = instruction.lower()
            
            # 常见的路线规划指令模式集合
            patterns = [
                # 基础模式
                (r'从(.*?)到(.*?)', 1, 2),        # 从A到B
                (r'从(.*?)去(.*?)', 1, 2),        # 从A去B
                
                # 带引导词的模式
                (r'带我从(.*?)到(.*?)', 1, 2),    # 带我从A到B
                (r'请带我从(.*?)到(.*?)', 1, 2),  # 请带我从A到B
                (r'帮我从(.*?)到(.*?)', 1, 2),    # 帮我从A到B
                (r'我想从(.*?)到(.*?)', 1, 2),    # 我想从A到B
                
                # 询问路线模式
                (r'(.*?)到(.*?)怎么走', 1, 2),    # A到B怎么走
                (r'(.*?)到(.*?)的路线', 1, 2),    # A到B的路线
                (r'(.*?)到(.*?)的路径', 1, 2),    # A到B的路径
                (r'(.*?)到(.*?)的走法', 1, 2),    # A到B的走法
                (r'(.*?)到(.*?)如何走', 1, 2),    # A到B如何走
                (r'(.*?)到(.*?)怎么走最好', 1, 2),  # A到B怎么走最好
                
                # 反向表述模式
                (r'去(.*?)从(.*?)', 2, 1),        # 去B从A
                (r'前往(.*?)从(.*?)', 2, 1),      # 前往B从A
                
                # 口语化表述
                (r'从(.*?)出发到(.*?)', 1, 2),    # 从A出发到B
                (r'(.*?)出发到(.*?)', 1, 2),      # A出发到B
                (r'从(.*?)到(.*?)怎么走', 1, 2),  # 从A到B怎么走
                (r'从(.*?)到(.*?)怎么去', 1, 2),  # 从A到B怎么去
                (r'从(.*?)到(.*?)的路线图', 1, 2),  # 从A到B的路线图
                
                # 简化表述
                (r'(.*?)至(.*?)', 1, 2),          # A至B
                (r'(.*?)→(.*?)', 1, 2),           # A→B
                (r'(.*?)到(.*?)', 1, 2),          # A到B (备用，确保基础匹配)
            ]

            # 尝试匹配各种模式
            for pattern, start_group, end_group in patterns:
                match = re.search(pattern, instruction_lower)
                if match:
                    start = match.group(start_group).strip()
                    end = match.group(end_group).strip()
                    
                    # 过滤掉无效的起点和终点
                    if start and end and len(start) > 1 and len(end) > 1:
                        # 去除可能的多余修饰词
                        for stop_word in ['学院', '大楼', '广场']:  # 需调整
                            start = start.replace(stop_word, '') if start.endswith(stop_word) else start
                            end = end.replace(stop_word, '') if end.endswith(stop_word) else end
                            start = start.replace(stop_word, '') if start.startswith(stop_word) else start
                            end = end.replace(stop_word, '') if end.startswith(stop_word) else end
                        
                        # 过滤掉出行方式关键词
                        transportation_words = ['步行', '走路', '骑行', '骑自行车', '开车', '驾车', '打车', '乘车']
                        for word in transportation_words:
                            if start == word:
                                # 如果起点是出行方式，则可能指令结构是'出行方式+从+起点+到+终点'
                                # 尝试重新匹配指令
                                match = re.search(rf'{word}从(.*?)到(.*?)', instruction_lower)
                                if match:
                                    start = match.group(1).strip()
                                    end = match.group(2).strip()
                                    break
                            elif end == word:
                                # 如果终点是出行方式，可能是指令结构错误
                                # 在这种情况下，我们尝试交换起点和终点
                                start, end = end, start
                                break
                        
                        return {
                            'start': start,
                            'end': end
                        }
            
            # 尝试直接提取两个关键词（简单的两点之间路线）
            # 这种方式可能不太精确，但作为最后的尝试
            try:
                words = jieba.lcut(instruction_lower)
                if len(words) >= 2:
                    # 提取前两个可能的地点词
                    possible_locations = []
                    for word in words:
                        if len(word) > 1 and word not in ['从', '到', '去', '走', '路线', '路径', '怎么', '如何', '带我', '帮我', '我想']:
                            possible_locations.append(word)
                            if len(possible_locations) == 2:
                                break
                    
                    if len(possible_locations) == 2:
                        return {
                            'start': possible_locations[0],
                            'end': possible_locations[1]
                        }
            except ImportError:
                # 如果jieba库不可用，跳过此步骤
                print("jieba库不可用，跳过关键词提取")
            
            # 如果没有匹配到任何模式，返回None
            print(f"未能匹配任何指令模式: {instruction}")
            return None
        except Exception as e:
            print(f"手动解析指令失败: {e}")
            return None
    
    def find_point_id_by_name(self, location_name):
        """根据地点名称查找对应的地点ID，支持模糊匹配和关键词提取
        
        Args:
            location_name: 地点名称
        
        Returns:
            str: 地点ID，如果未找到则返回None
        """
        # 转换为小写进行模糊匹配
        location_name_lower = location_name.lower()
        
        # 优先精确匹配
        for point in self.points_data:
            if point['name'].lower() == location_name_lower:
                return point['id']
        
        # 从JSON文件加载特殊映射
        try:
            with open('map_data/reflection.json', 'r', encoding='utf-8') as f:  # 注意路径！！！
                special_mappings = json.load(f)
        except Exception as e:
            print(f"加载映射文件失败: {e}")
            special_mappings = {}
        
        # 检查是否有特殊映射
        if location_name_lower in special_mappings:
            mapped_name = special_mappings[location_name_lower]
            for point in self.points_data:
                if mapped_name in point['name'].lower():
                    return point['id']
        
        # 高级模糊匹配，使用关键词权重算法
        # 将用户输入和地点名称拆分为关键词
        user_keywords = location_name_lower.split()
        best_match = None
        highest_score = 0
        
        for point in self.points_data:
            point_name_lower = point['name'].lower()
            point_keywords = point_name_lower.split()
            
            # 计算匹配分数
            score = 0
            for user_keyword in user_keywords:
                # 完全匹配关键词得2分
                if user_keyword in point_keywords:
                    score += 2
                # 部分匹配关键词得1分
                elif any(user_keyword in point_keyword for point_keyword in point_keywords):
                    score += 1
            
            # 更新最佳匹配
            if score > highest_score:
                highest_score = score
                best_match = point['id']
        
        # 如果找到足够好的匹配（至少有一个关键词匹配）
        if best_match and highest_score > 0:
            return best_match
        
        # 检查是否是简化名称
        for point in self.points_data:
            point_name_lower = point['name'].lower()
            # 如果地点名称包含用户输入的所有关键词
            if all(keyword in point_name_lower for keyword in location_name_lower.split()):
                return point['id']
        
        # 其次模糊匹配 - 用户输入是地点名称的子字符串
        for point in self.points_data:
            if location_name_lower in point['name'].lower():
                return point['id']
        
        # 反向模糊匹配 - 地点名称包含用户输入的关键词
        keywords = location_name_lower.split()
        for point in self.points_data:
            point_name_lower = point['name'].lower()
            for keyword in keywords:
                if keyword in point_name_lower:
                    return point['id']
        
        # 如果没有找到，尝试匹配地址
        for point in self.points_data:
            if 'address' in point and point['address'] and location_name_lower in point['address'].lower():
                return point['id']
        
        return None
    
    def process_nlp_route_request(self, instruction):
        """处理自然语言路线规划请求
        
        Args:
            instruction: 用户输入的自然语言指令
        
        Returns:
            dict: 包含路线信息的字典，如果处理失败则返回包含错误信息的字典
        """
        # 解析指令
        parsed_result = self.parse_nlp_instruction(instruction)
        
        if not parsed_result:
            return {
                'error': '无法解析您的路线规划指令，请尝试使用更清晰的表达方式'
            }
        
        start_name = parsed_result['start']
        end_name = parsed_result['end']
        
        # 查找起点和终点的ID
        start_id = self.find_point_id_by_name(start_name)
        end_id = self.find_point_id_by_name(end_name)
        
        # 检查是否找到有效的起点和终点
        if not start_id:
            return {
                'error': f'未能找到与"{start_name}"匹配的地点，请尝试使用更具体的地点名称'
            }
        
        if not end_id:
            return {
                'error': f'未能找到与"{end_name}"匹配的地点，请尝试使用更具体的地点名称'
            }
        
        # 获取起点和终点的完整信息
        start_point = next((p for p in self.points_data if p['id'] == start_id), None)
        end_point = next((p for p in self.points_data if p['id'] == end_id), None)
        
        # 使用data_processor中的plan_route函数规划路线
        # 默认为步行路线
        route = self.data_processor.plan_route(start_id, end_id, route_type='walking')
        
        if not route:
            return {
                'error': f'无法规划从"{start_point["name"]}"到"{end_point["name"]}"的路线'
            }
        
        # 添加起点和终点的名称信息
        route['properties']['start_name'] = start_point['name']
        route['properties']['end_name'] = end_point['name']
        
        return {
            'route': route,
            'start': start_point['name'],
            'end': end_point['name']
        }