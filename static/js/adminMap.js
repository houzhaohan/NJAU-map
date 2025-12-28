// 管理员面板相关功能
document.addEventListener('DOMContentLoaded', function() {
    // 管理员特定功能可以在这里实现
    // 添加、编辑、删除地点等管理功能，还未实现
    
    // 如果页面上有地图元素，初始化地图
    if (document.getElementById('map')) {
        mapCore.initMap();
    }
    
    // 管理员特定的事件监听和功能可以在这里添加
});

// 后续增加一些功能