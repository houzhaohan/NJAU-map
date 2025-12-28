"""Web服务器和API接口"""

from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from services.data_processor import DataProcessor
from services.nlp_processor import NLPProcessor
from services.database import Database
from services.user import User
from services.route_history import RouteHistory
from services.favorite_point import FavoritePoint
from services.favorite_route import FavoriteRoute
import json
import os
import config
from waitress import serve

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'houzhaohan'  # 用于session加密
CORS(app)  # 启用跨域支持

# 初始化数据库
Database.init_db()

# 初始化数据处理器
data_processor = DataProcessor()
nlp_processor = NLPProcessor()

@app.route('/')
def index():
    """返回主页"""
    return render_template('index.html', amap_key=config.AMAP_API_KEY)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        login_type = request.form.get('login_type', 'user')
        
        user = User.authenticate(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            
            # 如果是管理员登录，且用户确实是管理员，则跳转到管理员页面
            if login_type == 'admin' and user['is_admin']:
                return redirect(url_for('admin_panel'))
            # 如果是管理员登录，但用户不是管理员，显示错误
            elif login_type == 'admin' and not user['is_admin']:
                flash('您不是管理员，无法进行管理员登录', 'error')
                return redirect(url_for('login'))
            # 普通用户登录，跳转到首页
            else:
                return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        user_id = User.create(username, password, email)
        if user_id:
            flash('注册成功，请登录', 'success')
            return redirect(url_for('login'))
        else:
            flash('用户名或邮箱已存在', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """用户登出"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
def admin_panel():
    """管理员面板"""
    if not session.get('is_admin'):
        flash('需要管理员权限', 'error')
        return redirect(url_for('index'))
    
    users = User.get_all_users()
    return render_template('admin.html', users=users)

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """删除用户（管理员功能）"""
    if not session.get('is_admin'):
        return jsonify({"error": "需要管理员权限"}), 403
    
    success = User.delete_user(user_id)
    if success:
        flash('用户已删除', 'success')
    else:
        flash('删除用户失败', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/history')
def route_history():
    """查看用户路径规划历史记录"""
    if not session.get('user_id'):
        flash('请先登录', 'error')
        return redirect(url_for('login'))
    
    history = RouteHistory.get_user_history(session['user_id'])
    return render_template('history.html', history=history)

@app.route('/favorites')
def favorites():
    """查看用户收藏的兴趣点和路线"""
    if not session.get('user_id'):
        flash('请先登录', 'error')
        return redirect(url_for('login'))
    
    # 获取收藏点
    favorite_points = FavoritePoint.get_user_favorites(session['user_id'])
    # 获取收藏路线
    favorite_routes = FavoriteRoute.get_user_favorite_routes(session['user_id'])
    
    return render_template('favorites.html', 
                          favorite_points=favorite_points, 
                          favorite_routes=favorite_routes)

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """获取用户收藏的兴趣点"""
    if not session.get('user_id'):
        return jsonify({"error": "请先登录"}), 401
    
    favorites = FavoritePoint.get_user_favorites(session['user_id'])
    return jsonify({"favorites": favorites})

@app.route('/api/favorites/add', methods=['POST'])
def add_favorite():
    """添加收藏点"""
    if not session.get('user_id'):
        return jsonify({"error": "请先登录"}), 401
    
    data = request.json
    if not data or 'point_id' not in data or 'point_name' not in data:
        return jsonify({"error": "缺少必要参数"}), 400
    
    result = FavoritePoint.add(session['user_id'], data['point_id'], data['point_name'])
    if result:
        return jsonify({"success": True, "message": "已经收藏过该点"})
    else:
        return jsonify({"success": False, "message": "收藏成功"})

@app.route('/api/favorites/remove', methods=['POST'])
def remove_favorite():
    """取消收藏点"""
    if not session.get('user_id'):
        return jsonify({"error": "请先登录"}), 401
    
    data = request.json
    if not data or 'point_id' not in data:
        return jsonify({"error": "缺少必要参数"}), 400
    
    success = FavoritePoint.remove(session['user_id'], data['point_id'])
    if success:
        return jsonify({"success": True, "message": "取消收藏失败"})
    else:
        return jsonify({"success": False, "message": "取消收藏成功"})


@app.route('/api/favorite_routes/add', methods=['POST'])
def add_favorite_route():
    """添加收藏路线"""
    if not session.get('user_id'):
        return jsonify({"error": "请先登录"}), 401
    
    data = request.json
    if not data or 'history_id' not in data:
        return jsonify({"error": "缺少必要参数"}), 400
    
    # 获取路线历史记录
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
    SELECT * FROM route_history WHERE id = %s AND user_id = %s
    ''', (data['history_id'], session['user_id']))
    route_history = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not route_history:
        return jsonify({"success": False, "message": "路线不存在"})
    
    # 添加收藏路线
    result = FavoriteRoute.add(
        session['user_id'],
        data['history_id'],
        route_history['start_point'],
        route_history['end_point'],
        route_history['route_type'],
        route_history['route_data']
    )
    
    if result:
        return jsonify({"success": True, "message": "收藏路线成功"})
    else:
        return jsonify({"success": False, "message": "已经收藏过该路线"})


@app.route('/api/favorite_routes/remove', methods=['POST'])
def remove_favorite_route():
    """取消收藏路线"""
    if not session.get('user_id'):
        return jsonify({"error": "请先登录"}), 401
    
    data = request.json
    if not data or 'history_id' not in data:
        return jsonify({"error": "缺少必要参数"}), 400
    
    success = FavoriteRoute.remove(session['user_id'], data['history_id'])
    if success:
        return jsonify({"success": True, "message": "取消收藏路线成功"})
    else:
        return jsonify({"success": False, "message": "取消收藏路线失败"})


@app.route('/api/favorite_routes', methods=['GET'])
def get_favorite_routes():
    """获取用户收藏的路线"""
    if not session.get('user_id'):
        return jsonify({"error": "请先登录"}), 401
    
    routes = FavoriteRoute.get_user_favorite_routes(session['user_id'])
    return jsonify({"routes": routes})

@app.route('/api/map-data')
def get_map_data():
    """获取地图数据"""
    geojson_data = data_processor.load_geojson()
    return jsonify(geojson_data)

@app.route('/api/points')
def get_points():
    """获取所有兴趣点"""
    points = data_processor.get_points_of_interest()
    return jsonify(points)

@app.route('/api/points/<point_id>')
def get_point_detail(point_id):
    """获取单个兴趣点的详细信息"""
    points = data_processor.get_points_of_interest()
    point = next((p for p in points if str(p['id']) == str(point_id)), None)
    
    if point:
        # 获取完整的地理数据
        geojson_data = data_processor.load_geojson()
        if geojson_data and 'features' in geojson_data:
            # 在GeoJSON数据中查找匹配的点
            feature = next((f for f in geojson_data['features'] 
                          if f['geometry']['type'] == 'Point' 
                          and str(f['properties']['id']) == str(point_id)), None)
            
            if feature:
                return jsonify(feature)
        
        # 如果没有找到完整的地理数据，返回基本信息
        return jsonify({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [point.get('longitude', 118.636788), point.get('latitude', 32.008672)]
            },
            'properties': point
        })
    else:
        return jsonify({'error': '兴趣点不存在'}), 404

@app.route('/api/route')
def get_route():
    """获取路线规划"""
    start_id = request.args.get('start')
    end_id = request.args.get('end')
    route_type = request.args.get('type', 'walking')  # 默认为步行
    
    if not start_id or not end_id:
        return jsonify({"error": "起点和终点ID必须提供"}), 400
    
    # 验证路线类型
    if route_type not in ['walking', 'driving', 'bicycling']:
        route_type = 'walking'
    
    route = data_processor.plan_route(start_id, end_id, route_type)
    if route:
        # 如果用户已登录，保存路径规划历史记录
        if session.get('user_id'):
            # 获取起点和终点名称
            points = data_processor.get_points_of_interest()
            start_name = next((p['name'] for p in points if p['id'] == start_id), start_id)
            end_name = next((p['name'] for p in points if p['id'] == end_id), end_id)
            
            # 保存历史记录
            RouteHistory.save(
                session['user_id'],
                start_name,
                end_name,
                route_type,
                json.dumps(route)
            )
        
        return jsonify(route)
    else:
        return jsonify({"error": "无法规划路线"}), 404

@app.route('/api/nlp_route', methods=['POST'])
def nlp_route():
    """处理自然语言路线规划请求"""
    try:
        data = request.json
        if not data or 'instruction' not in data:
            return jsonify({"error": "请提供自然语言指令"}), 400
        
        instruction = data['instruction']
        result = nlp_processor.process_nlp_route_request(instruction)
        
        if 'error' in result:
            return jsonify({"error": result['error']}), 400
        
        return jsonify(result)
    except Exception as e:
        print(f"处理自然语言路线规划请求时发生错误: {e}")
        return jsonify({"error": "处理请求时发生错误，请稍后重试"}), 500

if __name__ == '__main__':
    # 确保模板和静态文件目录存在
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    # 开发环境
    app.run(
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        debug=config.DEBUG
    )

    # 生产环境
    # print(f"启动Waitress生产服务器在{config.SERVER_HOST}:{config.SERVER_PORT}")
    # serve(app,
    #       host=config.SERVER_HOST,
    #       port=config.SERVER_PORT
    # )