// 地图核心功能
// 包含地图初始化和基础数据加载功能

// 全局变量
let map = null;
let pointsData = [];
let currentRoute = null;

// 初始化地图
function initMap() {
    // 创建地图实例
    map = new AMap.Map('map', {
        zoom: 16,
        viewMode: '3D',
        center: [118.636788, 32.008672] // 设置初始中心点为南京农业大学滨江校区，好像不是正中间。。。
    });
    
    // 加载地图数据
    loadMapData();
    
    // 加载兴趣点数据
    loadPointsOfInterest();
    
    // 加载用户收藏点
    loadUserFavorites();
}

// 加载地图数据
function loadMapData() {
    fetch('/api/map-data')
        .then(response => response.json())
        .then(data => {
            // 设置地图中心点为第一个特征点
            if (data.features && data.features.length > 0) {
                const firstPoint = data.features[0].geometry.coordinates;
                map.setCenter([firstPoint[0], firstPoint[1]]);
            }
            
            // 手动将GeoJSON数据添加到地图
            if (data.features && data.features.length > 0) {
                data.features.forEach(feature => {
                    if (feature.geometry.type === 'Point') {
                        const coords = feature.geometry.coordinates;
                        const marker = new AMap.Marker({
                            position: new AMap.LngLat(coords[0], coords[1]),
                            title: feature.properties.name,
                            extData: feature.properties
                        });
                        
                        // 添加信息窗体
                        const infoWindow = new AMap.InfoWindow({
                            content: `<div>
                                <h3>${feature.properties.name}</h3>
                                <!-- <p>地址: ${feature.properties.address || '无'}</p> -->
                                <p>类型: ${feature.properties.type || '无'}</p>
                                <button class="favorite-btn" data-id="${feature.properties.id}" data-name="${feature.properties.name}">收藏</button>
                            </div>`,
                            offset: new AMap.Pixel(0, -30)
                        });
                        
                        // 点击标记时显示信息窗体
                        marker.on('click', () => {
                            infoWindow.open(map, marker.getPosition());
                        });
                        
                        // 将标记添加到地图
                        map.add(marker);
                    }
                });
            }
        })
        .catch(error => console.error('加载地图数据失败:', error));
}

// 加载兴趣点数据
function loadPointsOfInterest() {
    fetch('/api/points')
        .then(response => response.json())
        .then(data => {
            pointsData = data;
            
            // 填充下拉选择框
            const startSelect = document.getElementById('start-point');
            const endSelect = document.getElementById('end-point');
            
            // 清空现有选项
            startSelect.innerHTML = '';
            endSelect.innerHTML = '';
            
            // 添加选项
            data.forEach(point => {
                const startOption = document.createElement('option');
                startOption.value = point.id;
                startOption.textContent = point.name;
                startSelect.appendChild(startOption);
                
                const endOption = document.createElement('option');
                endOption.value = point.id;
                endOption.textContent = point.name;
                endSelect.appendChild(endOption);
            });
            
            // 填充兴趣点列表
            const poiContainer = document.getElementById('poi-container');
            if (poiContainer) {
                // 添加折叠按钮
                const poiListHeader = document.createElement('div');
                poiListHeader.className = 'poi-list-header';
                poiListHeader.innerHTML = `
                    <span class="poi-count">共 ${data.length} 个地点</span>
                    <button id="toggle-poi-list" class="toggle-btn">展开</button>
                `;
                poiContainer.parentNode.insertBefore(poiListHeader, poiContainer);
                
                // 设置初始状态为折叠
                poiContainer.style.display = 'none';
                
                // 切换按钮点击事件
                document.getElementById('toggle-poi-list').addEventListener('click', function() {
                    if (poiContainer.style.display === 'none') {
                        poiContainer.style.display = 'grid';
                        this.textContent = '折叠';
                    } else {
                        poiContainer.style.display = 'none';
                        this.textContent = '展开';
                    }
                });
                
                // 填充兴趣点数据
                poiContainer.innerHTML = '';
                
                data.forEach(point => {
                    const poiItem = document.createElement('div');
                    poiItem.className = 'poi-item';
                    poiItem.innerHTML = `
                        <div class="poi-name">${point.name}</div>
                        <div class="poi-address">${point.address || '无地址信息'}</div>
                        <div class="poi-type">${point.type || '无类型信息'}</div>
                    `;
                    
                    poiContainer.appendChild(poiItem);
                });
            }
        })
        .catch(error => console.error('加载兴趣点数据失败:', error));
}

// 清除路线
function clearRoute() {
    if (currentRoute) {
        map.remove(currentRoute);
        currentRoute = null;
    }
}

// 导出全局变量和函数
window.mapCore = {
    get map() { return map; },
    get pointsData() { return pointsData; },
    get currentRoute() { return currentRoute; },
    set currentRoute(value) { currentRoute = value; },
    initMap,
    loadMapData,
    loadPointsOfInterest,
    clearRoute
};