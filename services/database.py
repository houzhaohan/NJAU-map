"""数据库连接和操作模块"""

import mysql.connector
from config import DB_CONFIG
import hashlib

class Database:
    """数据库连接和操作类"""
    @staticmethod
    def get_connection():
        """获取数据库连接"""
        return mysql.connector.connect(**DB_CONFIG)
    
    @staticmethod
    def init_db():
        """初始化数据库表"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建路径规划历史记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS route_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            start_point VARCHAR(100) NOT NULL,
            end_point VARCHAR(100) NOT NULL,
            route_type VARCHAR(20) NOT NULL,
            route_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        ''')
        
        # 创建收藏点表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            point_id VARCHAR(50) NOT NULL,
            point_name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE KEY unique_user_point (user_id, point_id)
        )
        ''')
        
        # 创建收藏路线表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorite_routes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            history_id INT NOT NULL,
            start_point VARCHAR(100) NOT NULL,
            end_point VARCHAR(100) NOT NULL,
            route_type VARCHAR(20) NOT NULL,
            route_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (history_id) REFERENCES route_history(id) ON DELETE CASCADE,
            UNIQUE KEY unique_user_history (user_id, history_id)
        )
        ''')
        
        # 创建默认管理员账户
        # try:
        #     admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        #     cursor.execute('''
        #     INSERT INTO users (username, password, email, is_admin)
        #     VALUES (%s, %s, %s, %s)
        #     ''', ("admin", admin_password, "admin@example.com", True))
        #     conn.commit()
        # except mysql.connector.errors.IntegrityError:
        #     # 管理员账户已存在，忽略错误
        #     pass
        
        cursor.close()
        conn.close()