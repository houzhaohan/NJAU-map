// 首页地图功能
document.addEventListener('DOMContentLoaded', function() {
    // 初始化地图
    mapCore.initMap();
    
    // 检查URL参数
    const urlParams = new URLSearchParams(window.location.search);
    const pointId = urlParams.get('point_id');
    const showHistoryRoute = urlParams.get('showHistoryRoute') === 'true';
    
    if (showHistoryRoute) {
        // 如果需要显示历史路线，等待地图加载完成后显示
        setTimeout(() => {
            showHistoryRouteOnMap();
        }, 1000); // 等待1秒确保地图数据已加载
    } else if (pointId) {
        // 如果有兴趣点ID，在地图加载完成后显示该兴趣点
        setTimeout(() => {
            showPointOnMap(pointId);
        }, 1000); // 等待1秒确保地图数据已加载
    }
    
    // 设置事件监听
    document.getElementById('plan-route').addEventListener('click', planRoute);
    document.getElementById('clear-route').addEventListener('click', mapCore.clearRoute);
    document.getElementById('nlp-plan-route').addEventListener('click', handleNlpRequest);
    
    // 为收藏按钮添加事件委托
    document.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('favorite-btn')) {
            const pointId = e.target.getAttribute('data-id');
            const pointName = e.target.getAttribute('data-name');
            toggleFavorite(pointId, pointName, e.target);
        }
    });
    
    // 规划路线
    function planRoute() {
        const startId = document.getElementById('start-point').value;
        const endId = document.getElementById('end-point').value;
        const routeType = document.getElementById('route-type').value;
        
        if (!startId || !endId) {
            alert('请选择起点和终点');
            return;
        }
        
        // 清除现有路线
        mapCore.clearRoute();
        
        // 获取路线数据
        fetch(`/api/route?start=${startId}&end=${endId}&type=${routeType}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }
                
                // 创建路线
                const path = data.geometry.coordinates.map(coord => new AMap.LngLat(coord[0], coord[1]));
                
                mapCore.currentRoute = new AMap.Polyline({
                    path: path,
                    strokeColor: data.properties.color || '#1890FF',
                    strokeWeight: data.properties.width || 6,
                    strokeOpacity: 0.8,
                    showDir: true
                });
                
                // 将路线添加到地图
                mapCore.map.add(mapCore.currentRoute);
                
                // 调整视图以显示整个路线
                mapCore.map.setFitView([mapCore.currentRoute]);
                
                // 显示路线信息
                const startName = data.properties.start;
                const endName = data.properties.end;
                const distance = data.properties.distance ? (parseInt(data.properties.distance) / 1000).toFixed(2) : '未知';
                const duration = data.properties.duration ? Math.ceil(parseInt(data.properties.duration) / 60) : '未知';
                const routeTypeText = {
                    'walking': '步行',
                    'driving': '驾车',
                    'bicycling': '骑行'
                }[routeType] || '未知';
                
                alert(`已规划从 ${startName} 到 ${endName} 的${routeTypeText}路线\n距离: ${distance}公里\n时间: 约${duration}分钟`);
            })
            .catch(error => console.error('规划路线失败:', error));
    }
    
    // 处理自然语言路线规划请求
    async function handleNlpRequest() {
        const instruction = document.getElementById('nlp-input').value;
        const resultDiv = document.getElementById('nlp-result');
        
        if (!instruction.trim()) {
            resultDiv.innerHTML = '<span style="color: red;">请输入路线指令</span>';
            return;
        }
        
        // 显示加载状态
        resultDiv.innerHTML = '正在解析指令并规划路线...';
        
        try {
            // 发送请求到后端API
            const response = await fetch('/api/nlp_route', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({instruction})
            });
            
            const data = await response.json();
            
            // 处理响应
            if (data.error) {
                resultDiv.innerHTML = `<span style="color: red;">错误: ${data.error}</span>`;
                return;
            }
            
            // 清除旧路线并绘制新路线
            mapCore.clearRoute();
            
            // 从返回的路线数据中提取坐标
            const routeData = data.route;
            if (routeData && routeData.geometry && routeData.geometry.coordinates) {
                const path = routeData.geometry.coordinates.map(coord => 
                    new AMap.LngLat(coord[0], coord[1])
                );
                
                // 创建新路线
                mapCore.currentRoute = new AMap.Polyline({
                    path: path,
                    strokeColor: routeData.properties.color || '#ff0000',
                    strokeWeight: routeData.properties.width || 6,
                    strokeOpacity: 0.8,
                    showDir: true
                });
                
                // 添加路线到地图
                mapCore.map.add(mapCore.currentRoute);
                
                // 调整视图以显示整个路线
                mapCore.map.setFitView([mapCore.currentRoute]);
                
                // 显示成功信息
                resultDiv.innerHTML = `<span style="color: green;">成功规划路线：${data.start} → ${data.end}</span>`;
                
                // 显示路线详细信息
                const distance = routeData.properties.distance ? 
                    (parseInt(routeData.properties.distance) / 1000).toFixed(2) : '未知';
                const duration = routeData.properties.duration ? 
                    Math.ceil(parseInt(routeData.properties.duration) / 60) : '未知';
                
                // 显示路线信息提示
                alert(`已规划从 ${data.start} 到 ${data.end} 的路线\n距离: ${distance}公里\n时间: 约${duration}分钟`);
            }
        } catch (error) {
            console.error('处理自然语言路线规划请求时发生错误:', error);
            resultDiv.innerHTML = '<span style="color: red;">请求失败，请检查网络连接或稍后重试</span>';
        }
    }
    
    // 显示历史路线
    function showHistoryRouteOnMap() {
        try {
            // 从localStorage中读取路线数据
            const routeDataStr = localStorage.getItem('historyRouteData');
            if (!routeDataStr) {
                console.error('没有找到历史路线数据');
                alert('无法加载历史路线数据');
                return;
            }
            
            // 解析路线数据
            const routeData = JSON.parse(routeDataStr);
            
            // 清除现有路线
            mapCore.clearRoute();
            
            // 创建路线
            const path = routeData.geometry.coordinates.map(coord => 
                new AMap.LngLat(coord[0], coord[1])
            );
            
            mapCore.currentRoute = new AMap.Polyline({
                path: path,
                strokeColor: routeData.properties.color || '#1890FF',
                strokeWeight: routeData.properties.width || 6,
                strokeOpacity: 0.8,
                showDir: true
            });
            
            // 将路线添加到地图
            mapCore.map.add(mapCore.currentRoute);
            
            // 调整视图以显示整个路线
            mapCore.map.setFitView([mapCore.currentRoute]);
            
            // 显示路线信息
            const startName = routeData.properties.start;
            const endName = routeData.properties.end;
            const distance = routeData.properties.distance ? 
                (parseInt(routeData.properties.distance) / 1000).toFixed(2) : '未知';
            const duration = routeData.properties.duration ? 
                Math.ceil(parseInt(routeData.properties.duration) / 60) : '未知';
            
            // 显示路线信息提示
            alert(`已显示历史路线: ${startName} → ${endName}\n距离: ${distance}公里\n时间: 约${duration}分钟`);
            
            // 清除localStorage中的路线数据，避免下次访问首页时自动显示
            localStorage.removeItem('historyRouteData');
        } catch (error) {
            console.error('显示历史路线失败:', error);
            alert('显示历史路线失败，请稍后再试');
        }
    }
    
    
    // 根据兴趣点ID在地图上显示兴趣点
    function showPointOnMap(pointId) {
        fetch(`/api/points/${pointId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('获取兴趣点数据失败');
                }
                return response.json();
            })
            .then(pointData => {
                if (pointData && pointData.geometry && pointData.geometry.coordinates) {
                    const lngLat = new AMap.LngLat(
                        pointData.geometry.coordinates[0],
                        pointData.geometry.coordinates[1]
                    );
                    
                    // 将地图中心移动到该兴趣点
                    mapCore.map.setCenter(lngLat);
                    mapCore.map.setZoom(18); // 放大地图
                    
                    // 创建一个临时标记来高亮显示该兴趣点
                    const highlightMarker = new AMap.Marker({
                        position: lngLat,
                        title: pointData.properties.name,
                        icon: new AMap.Icon({
                            image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png',
                            imageSize: new AMap.Size(36, 42),
                            imageOffset: new AMap.Pixel(-18, -42)
                        })
                    });
                    
                    // 添加标记到地图
                    mapCore.map.add(highlightMarker);
                    
                    // 打开信息窗口
                    const infoWindow = new AMap.InfoWindow({
                        content: `<div>
                            <h3>${pointData.properties.name}</h3>
                            <p>地址: ${pointData.properties.address || '无'}</p>
                            <p>类型: ${pointData.properties.type || '无'}</p>
                        </div>`,
                        offset: new AMap.Pixel(0, -30)
                    });
                    
                    infoWindow.open(mapCore.map, lngLat);
                    
                    // 3秒后自动移除高亮标记（保留原有标记）
                    setTimeout(() => {
                        mapCore.map.remove(highlightMarker);
                    }, 3000);
                }
            })
            .catch(error => {
                console.error('显示兴趣点失败:', error);
                alert('无法显示该兴趣点，请稍后再试');
            });
    }
});