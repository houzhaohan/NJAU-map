"""路径规划历史记录模型模块"""

from .database import Database

class RouteHistory:
    """路径规划历史记录模型"""
    @staticmethod
    def save(user_id, start_point, end_point, route_type, route_data):
        """保存路径规划历史记录"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO route_history (user_id, start_point, end_point, route_type, route_data)
            VALUES (%s, %s, %s, %s, %s)
            ''', (user_id, start_point, end_point, route_type, route_data))
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_user_history(user_id):
        """获取用户的路径规划历史记录"""
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
        SELECT * FROM route_history WHERE user_id = %s ORDER BY created_at DESC
        ''', (user_id,))
        
        history = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return history