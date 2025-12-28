"""收藏点模型模块"""

from .database import Database
import mysql.connector

class FavoritePoint:
    """收藏点模型"""
    @staticmethod
    def add(user_id, point_id, point_name):
        """添加收藏点"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO favorites (user_id, point_id, point_name)
            VALUES (%s, %s, %s)
            ''', (user_id, point_id, point_name))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.errors.IntegrityError:
            # 已经收藏过该点，忽略错误
            return None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def remove(user_id, point_id):
        """取消收藏点"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            DELETE FROM favorites WHERE user_id = %s AND point_id = %s
            ''', (user_id, point_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_user_favorites(user_id):
        """获取用户的所有收藏点"""
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
        SELECT * FROM favorites WHERE user_id = %s ORDER BY created_at DESC
        ''', (user_id,))
        
        favorites = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return favorites
    
    @staticmethod
    def is_favorite(user_id, point_id):
        """检查点是否被用户收藏"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT COUNT(*) FROM favorites WHERE user_id = %s AND point_id = %s
        ''', (user_id, point_id))
        
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return count > 0