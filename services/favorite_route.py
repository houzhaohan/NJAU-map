"""收藏路线模型模块"""

from .database import Database
import mysql.connector

class FavoriteRoute:
    """收藏路线模型"""
    @staticmethod
    def add(user_id, history_id, start_point, end_point, route_type, route_data):
        """添加收藏路线"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO favorite_routes (user_id, history_id, start_point, end_point, route_type, route_data)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''', (user_id, history_id, start_point, end_point, route_type, route_data))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.errors.IntegrityError:
            # 已经收藏过该路线，忽略错误
            return None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def remove(user_id, history_id):
        """取消收藏路线"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            DELETE FROM favorite_routes WHERE user_id = %s AND history_id = %s
            ''', (user_id, history_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_user_favorite_routes(user_id):
        """获取用户的所有收藏路线"""
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
        SELECT * FROM favorite_routes WHERE user_id = %s ORDER BY created_at DESC
        ''', (user_id,))
        
        routes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return routes
    
    @staticmethod
    def is_favorite_route(user_id, history_id):
        """检查路线是否被用户收藏"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT COUNT(*) FROM favorite_routes WHERE user_id = %s AND history_id = %s
        ''', (user_id, history_id))
        
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return count > 0