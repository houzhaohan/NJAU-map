"""用户模型模块"""

import hashlib
import mysql.connector
from .database import Database

class User:
    """用户模型"""
    @staticmethod
    def create(username, password, email, is_admin=False):
        """创建新用户"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        # 密码加密
        hashed_password = password.encode('utf-8')
        # hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            cursor.execute('''
            INSERT INTO users (username, password, email, is_admin)
            VALUES (%s, %s, %s, %s)
            ''', (username, hashed_password, email, is_admin))
            conn.commit()
            user_id = cursor.lastrowid
            return user_id
        except mysql.connector.errors.IntegrityError as e:
            # 用户名或邮箱已存在
            return None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def authenticate(username, password):
        """验证用户登录"""
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 密码加密
        hashed_password = password.encode('utf-8')
        # hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
        SELECT * FROM users WHERE username = %s AND password = %s
        ''', (username, hashed_password))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return user
    
    @staticmethod
    def get_all_users():
        """获取所有用户（管理员功能）"""
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
        SELECT id, username, email, is_admin, created_at FROM users
        ''')
        
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return users
    
    @staticmethod
    def delete_user(user_id):
        """删除用户（管理员功能）"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            DELETE FROM users WHERE id = %s AND is_admin = FALSE
            ''', (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()