export const API_BASE_URL = "/api";

export function formatTimeOnly(dtStr) {
    if (!dtStr) return '';
    try {
        const dateObj = new Date(dtStr);
        const hh = String(dateObj.getHours()).padStart(2, '0');
        const mm = String(dateObj.getMinutes()).padStart(2, '0');
        return `${hh}:${mm}`;
    } catch (e) {
        return '';
    }
}

export const apiState = {
    // FORMAT DATETIME HELPER
    formatDateTime(dtStr) {
        if (!dtStr) return '';
        try {
            const dateObj = new Date(dtStr);
            const yyyy = dateObj.getFullYear();
            const mm = String(dateObj.getMonth() + 1).padStart(2, '0');
            const dd = String(dateObj.getDate()).padStart(2, '0');
            const hh = String(dateObj.getHours()).padStart(2, '0');
            const min = String(dateObj.getMinutes()).padStart(2, '0');
            return `${yyyy}-${mm}-${dd} ${hh}:${min}`;
        } catch (e) {
            return dtStr;
        }
    },

    // BACKEND FETCH UTILITY
    async apiRequest(path, method = 'GET', body = null) {
        const headers = {
            'Content-Type': 'application/json'
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        const options = { method, headers };
        if (body) {
            options.body = JSON.stringify(body);
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}${path}`, options);
            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                if (response.status === 401) {
                    localStorage.removeItem('token');
                    localStorage.removeItem('user');
                    localStorage.removeItem('currentView');
                    throw new Error("Сессия истекла. Войдите заново.");
                }
                let errorMsg = errData.detail;
                if (Array.isArray(errData.detail)) {
                    errorMsg = errData.detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join('; ');
                }
                throw new Error(errorMsg || `Ошибка сервера (HTTP ${response.status})`);
            }
            return response.json();
        } catch (e) {
            if (e.message === "Failed to fetch" || e.name === "TypeError") {
                throw new Error("Не удалось подключиться к серверу. Проверьте, запущен ли бэкенд.");
            }
            throw e;
        }
    },

    getPlaceImage(name, imagePath) {
        if (imagePath) {
            if (imagePath.startsWith("http://") || imagePath.startsWith("https://")) {
                return imagePath;
            }
            return `http://localhost:8000${imagePath}`;
        }
        return "images/place_placeholder.png";
    },
    
    getMenuItemImage(name, imagePath) {
        if (imagePath) {
            if (imagePath.startsWith("http://") || imagePath.startsWith("https://")) {
                return imagePath;
            }
            return `http://localhost:8000${imagePath}`;
        }
        return "images/food_placeholder.png";
    },
    
    formatTime(timeStr) {
        if (!timeStr) return "";
        const parts = timeStr.split(':');
        if (parts.length >= 2) {
            return `${parts[0]}:${parts[1]}`;
        }
        return timeStr;
    },
    
    getStatusDisplay(status) {
        const mapping = {
            'new': 'НОВЫЙ',
            'preparing': 'ГОТОВИТСЯ',
            'ready': 'ГОТОВ',
            'completed': 'ЗАВЕРШЕН',
            'cancelled': 'ОТМЕНЕН'
        };
        return mapping[status] || status.toUpperCase();
    },
    
    getRestaurantCount(locationId) {
        return this.foodPlaces.filter(fp => fp.location_id === locationId).length;
    }
};
