// 收藏功能相关代码
document.addEventListener('DOMContentLoaded', function() {
    // 加载用户收藏点
    loadUserFavorites();
    
    // 为收藏按钮添加事件委托
    document.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('favorite-btn')) {
            const pointId = e.target.getAttribute('data-id');
            const pointName = e.target.getAttribute('data-name');
            toggleFavorite(pointId, pointName, e.target);
        }
    });
});

// 加载用户收藏点
function loadUserFavorites() {
    fetch('/api/favorites')
        .then(response => response.json())
        .then(data => {
            if (data.favorites) {
                // 更新收藏按钮状态
                data.favorites.forEach(favorite => {
                    const buttons = document.querySelectorAll(`.favorite-btn[data-id="${favorite.point_id}"]`);
                    buttons.forEach(button => {
                        button.textContent = '取消收藏';
                        button.classList.add('favorited');
                    });
                });
            }
        })
        .catch(error => console.error('加载收藏点失败:', error));
}

// 切换收藏状态
function toggleFavorite(pointId, pointName, button) {
    if (!pointId) return;
    
    const isFavorited = button.classList.contains('favorited');
    const url = isFavorited ? '/api/favorites/remove' : '/api/favorites/add';
    const data = isFavorited ? { point_id: pointId } : { point_id: pointId, point_name: pointName };
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            if (isFavorited) {
                button.textContent = '收藏';
                button.classList.remove('favorited');
            } else {
                button.textContent = '取消收藏';
                button.classList.add('favorited');
            }
            // 更新所有相同ID的按钮
            const buttons = document.querySelectorAll(`.favorite-btn[data-id="${pointId}"]`);
            buttons.forEach(btn => {
                if (btn !== button) {
                    btn.textContent = button.textContent;
                    if (isFavorited) {
                        btn.classList.remove('favorited');
                    } else {
                        btn.classList.add('favorited');
                    }
                }
            });
        } else {
            alert(result.message || '操作失败');
        }
    })
    .catch(error => {
        console.error('收藏操作失败:', error);
        alert('操作失败，请稍后再试');
    });
}