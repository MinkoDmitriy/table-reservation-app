import { formatTimeOnly, API_BASE_URL } from './api.js';
import { showConfirm } from './toast.js';

export const dashboardState = {
    managerOrders: [],
    managerReservations: [],
    managerManagedPlaceIds: [],
    managerSelectedCityId: null,
    totalOrders: 0,
    totalReservations: 0,
    revenue: 0,
    reservationStatuses: {},
    managerTab: 'orders',
    managerSelectedPlaceId: null,

    newMenuName: '',
    newMenuDesc: '',
    newMenuPrice: '',
    newMenuImagePath: '',

    adminTab: 'users',
    adminUsers: [],
    adminManagers: [],
    adminNewUserName: '',
    adminNewUserPassword: '',
    adminNewUserRole: 'client',
    adminEditUserId: null,
    adminEditUserName: '',
    adminEditUserRole: '',
    adminEditUserActive: true,
    adminNewCityName: '',
    adminNewPlaceLocationId: '',
    adminNewPlaceName: '',
    adminNewPlaceAddress: '',
    adminNewPlaceDesc: '',
    adminNewPlaceOpen: '12:00',
    adminNewPlaceClose: '23:00',
    adminNewPlaceImagePath: '',
    adminAssignManagerId: '',
    adminAssignCityId: '',

    managerCities() {
        const cityIds = new Set();
        this.foodPlaces.forEach(p => {
            if (this.managerManagedPlaceIds.includes(p.id)) {
                cityIds.add(p.location_id);
            }
        });
        return this.locations.filter(l => cityIds.has(l.id));
    },

    managerFilteredPlaceIds() {
        if (!this.managerSelectedCityId) return this.managerManagedPlaceIds;
        return this.managerManagedPlaceIds.filter(id => {
            const place = this.foodPlaces.find(p => p.id === id);
            return place && String(place.location_id) === String(this.managerSelectedCityId);
        });
    },

    adminAssignFilteredPlaces() {
        if (!this.adminAssignCityId) return this.foodPlaces;
        return this.foodPlaces.filter(p => String(p.location_id) === String(this.adminAssignCityId));
    },

    managerCombinedList() {
        const list = [];
        
        this.managerOrders.forEach(o => {
            const itemsStr = o.basket_items.map(bi => `${bi.menu_item?.name} x${bi.item_quantity}`).join(', ');
            const total = o.basket_items.reduce((acc, bi) => acc + (bi.menu_item?.price || 0) * bi.item_quantity, 0);
            list.push({
                unique_id: 'order_' + o.id,
                id: o.id,
                type: o.order_type || 'dinein',
                type_display: o.order_type === 'delivery' ? 'ДОСТАВКА' : 'В РЕСТОРАНЕ',
                display_id: `ORD-${1000 + o.id}`,
                clientName: o.user_name || `Клиент #${o.user_id}`,
                phone: o.phone || 'Не указан',
                details: itemsStr || 'Корзина пуста',
                subtext: o.order_type === 'delivery' ? o.address : 'Подача в зале к прибытию',
                total: total,
                status: o.status || 'new',
                status_display: this.getStatusDisplay(o.status || 'new'),
                time_only: formatTimeOnly(o.ordered_at)
            });
        });
        
        this.managerReservations.forEach(r => {
            const dt = new Date(r.start_datetime);
            const yyyy = dt.getFullYear();
            const mm = String(dt.getMonth() + 1).padStart(2, '0');
            const dd = String(dt.getDate()).padStart(2, '0');
            const hh = String(dt.getHours()).padStart(2, '0');
            const min = String(dt.getMinutes()).padStart(2, '0');
            const dateStr = `${yyyy}-${mm}-${dd}`;
            const timeStr = `${hh}:${min}`;
            
            const tableStr = r.table_number ? `Стол ${r.table_number}` : `Стол №${r.food_table_id}`;
            const seatsStr = r.max_seats ? ` (на ${r.max_seats} гостей)` : '';
            
            list.push({
                unique_id: 'res_' + r.id,
                id: r.id,
                type: 'reservation',
                type_display: 'БРОНЬ СТОЛА',
                display_id: `RES-${8000 + r.id}`,
                clientName: r.user_name || `Клиент #${r.user_id}`,
                phone: 'Указан при регистрации',
                details: `Бронь стола: ${tableStr}${seatsStr}`,
                subtext: `Дата: ${dateStr} к ${timeStr}`,
                total: 0,
                status: this.reservationStatuses[r.id] || 'new',
                status_display: this.getStatusDisplay(this.reservationStatuses[r.id] || 'new'),
                time_only: formatTimeOnly(r.start_datetime)
            });
        });
        
        return list.sort((a, b) => b.id - a.id);
    },

    async fetchManagerData() {
        if (!this.currentUser) return;
        try {
            if (this.isAdmin) {
                this.managerManagedPlaceIds = this.foodPlaces.map(p => p.id);
            } else {
                const me = await this.apiRequest('/users/me');
                this.managerManagedPlaceIds = me.managed_place_ids || [];
            }
            if (this.managerCities().length > 0 && !this.managerSelectedCityId) {
                this.managerSelectedCityId = this.managerCities()[0].id;
            }
            const filtered = this.managerFilteredPlaceIds();
            if (filtered.length > 0 && !this.managerSelectedPlaceId) {
                this.managerSelectedPlaceId = filtered[0];
            }
            await this.refreshManagerData();
        } catch (e) {
            console.error("Manager data fetch error", e);
        }
    },

    async refreshManagerData() {
        try {
            this.managerOrders = await this.apiRequest('/food_baskets/orders');
            this.managerReservations = await this.apiRequest('/reservations/all');
            
            if (this.managerSelectedPlaceId) {
                const placeOrders = this.managerOrders.filter(o => o.food_place_id === this.managerSelectedPlaceId || !o.food_place_id);
                this.totalOrders = placeOrders.length;
            } else {
                this.totalOrders = this.managerOrders.length;
            }
            this.totalReservations = this.managerReservations.length;
            
            let revenueSum = 0;
            this.managerOrders.forEach(o => {
                if (o.status !== 'cancelled') {
                    o.basket_items.forEach(bi => {
                        revenueSum += (bi.menu_item?.price || 0) * bi.item_quantity;
                    });
                }
            });
            this.revenue = revenueSum;
        } catch (e) {
            console.error("Manager data fetch error", e);
            this.toastError(`Ошибка загрузки панели управления: ${e.message}`);
        }
    },
    
    async updateOrderStatus(orderId, newStatus) {
        try {
            await this.apiRequest(`/food_baskets/orders/${orderId}/status`, 'PATCH', { status: newStatus });
            await this.refreshManagerData();
            this.toastSuccess("Статус заказа обновлён");
        } catch (e) {
            this.toastError(`Ошибка: ${e.message}`);
        }
    },
    
    async updateReservationStatus(resId, newStatus) {
        if (newStatus === 'cancelled') {
            await this.deleteReservation(resId);
        } else {
            this.reservationStatuses[resId] = newStatus;
            await this.refreshManagerData();
            this.toastSuccess("Статус бронирования обновлён");
        }
    },
    
    async deleteReservation(resId) {
        if (!await showConfirm("Вы действительно хотите отменить это бронирование стола?")) return;
        try {
            await this.apiRequest(`/reservations/${resId}`, 'DELETE');
            await this.refreshManagerData();
            this.toastSuccess("Бронирование отменено");
        } catch (e) {
            this.toastError(`Ошибка: ${e.message}`);
        }
    },
    
    async handleImageUpload(event, type) {
        const file = event.target.files[0];
        if (!file) return;
        const formData = new FormData();
        formData.append('file', file);
        try {
            const headers = {};
            if (this.token) headers['Authorization'] = `Bearer ${this.token}`;
            const response = await fetch(`${API_BASE_URL}/media/upload`, { method: 'POST', headers, body: formData });
            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.detail || 'Failed to upload image');
            }
            const data = await response.json();
            if (type === 'menu') this.newMenuImagePath = data.image_path;
            else if (type === 'place') this.newPlaceImagePath = data.image_path;
            this.toastSuccess("Изображение загружено");
        } catch (e) {
            this.toastError(`Ошибка загрузки изображения: ${e.message}`);
        }
    },
    
    clearUploadedImage(type) {
        if (type === 'menu') this.newMenuImagePath = '';
        else if (type === 'place') this.newPlaceImagePath = '';
    },
    
    async addMenuItem() {
        if (!this.newMenuName.trim() || !this.newMenuPrice) {
            this.toastWarning("Заполните название и цену блюда.");
            return;
        }
        try {
            const body = {
                name: this.newMenuName, description: this.newMenuDesc,
                price: parseFloat(this.newMenuPrice), food_place_id: this.managerSelectedPlaceId,
                image_path: this.newMenuImagePath || null
            };
            await this.apiRequest('/menu_items', 'POST', body);
            this.newMenuName = ''; this.newMenuDesc = ''; this.newMenuPrice = ''; this.newMenuImagePath = '';
            await this.fetchMenuItems(this.managerSelectedPlaceId);
            this.toastSuccess("Блюдо добавлено в меню!");
        } catch (e) {
            this.toastError(`Ошибка: ${e.message}`);
        }
    },

    async deleteMenuItem(itemId) {
        if (!await showConfirm("Удалить это блюдо из меню?")) return;
        try {
            await this.apiRequest(`/menu_items/${itemId}`, 'DELETE');
            await this.fetchMenuItems(this.managerSelectedPlaceId);
            this.toastSuccess("Блюдо удалено!");
        } catch (e) {
            this.toastError(`Ошибка: ${e.message}`);
        }
    },

    // ADMIN METHODS
    async fetchAdminData() {
        try {
            this.adminUsers = await this.apiRequest('/users');
            this.adminManagers = await this.apiRequest('/users/managers');
        } catch (e) {
            console.error("Admin data fetch error", e);
        }
    },

    async goToAdminPanel() {
        if (!this.isAdmin) return;
        this.currentView = 'admin';
        this.adminTab = 'users';
        await this.fetchAdminData();
        await this.fetchLocations();
        await this.fetchFoodPlaces();
    },

    async adminCreateUser() {
        if (!this.adminNewUserName.trim() || !this.adminNewUserPassword.trim()) {
            this.toastWarning("Заполните имя и пароль пользователя.");
            return;
        }
        try {
            await this.apiRequest('/users', 'POST', {
                name: this.adminNewUserName, password: this.adminNewUserPassword, role_name: this.adminNewUserRole
            });
            this.adminNewUserName = ''; this.adminNewUserPassword = ''; this.adminNewUserRole = 'client';
            await this.fetchAdminData();
            this.toastSuccess("Пользователь создан!");
        } catch (e) {
            this.toastError(`Ошибка: ${e.message}`);
        }
    },

    async adminStartEditUser(user) {
        this.adminEditUserId = user.id;
        this.adminEditUserName = user.name;
        this.adminEditUserRole = user.role?.name || 'client';
        this.adminEditUserActive = true;
    },

    async adminSaveEditUser() {
        try {
            await this.apiRequest(`/users/${this.adminEditUserId}`, 'PUT', {
                name: this.adminEditUserName, role_name: this.adminEditUserRole
            });
            this.adminEditUserId = null;
            await this.fetchAdminData();
            this.toastSuccess("Пользователь обновлён!");
        } catch (e) {
            this.toastError(`Ошибка: ${e.message}`);
        }
    },

    async adminDeleteUser(userId) {
        if (!await showConfirm("Удалить пользователя?")) return;
        try {
            await this.apiRequest(`/users/${userId}`, 'DELETE');
            await this.fetchAdminData();
            this.toastSuccess("Пользователь удалён!");
        } catch (e) {
            this.toastError(`Ошибка: ${e.message}`);
        }
    },

    async adminAddCity() {
        if (!this.adminNewCityName.trim()) {
            this.toastWarning("Введите название города.");
            return;
        }
        try {
            await this.apiRequest('/locations', 'POST', { name: this.adminNewCityName });
            this.adminNewCityName = '';
            await this.fetchLocations();
            this.toastSuccess("Город добавлен!");
        } catch (e) {
            this.toastError(`Ошибка: ${e.message}`);
        }
    },

    async adminAddPlace() {
        if (!this.adminNewPlaceLocationId || !this.adminNewPlaceName.trim() || !this.adminNewPlaceAddress.trim()) {
            this.toastWarning("Заполните город, название и адрес ресторана.");
            return;
        }
        try {
            await this.apiRequest('/food_places', 'POST', {
                location_id: parseInt(this.adminNewPlaceLocationId), name: this.adminNewPlaceName,
                address: this.adminNewPlaceAddress, description: this.adminNewPlaceDesc || 'Кухня',
                open_time: this.adminNewPlaceOpen || '12:00', close_time: this.adminNewPlaceClose || '23:00',
                image_path: this.adminNewPlaceImagePath || null
            });
            this.adminNewPlaceName = ''; this.adminNewPlaceAddress = ''; this.adminNewPlaceDesc = '';
            this.adminNewPlaceOpen = '12:00'; this.adminNewPlaceClose = '23:00'; this.adminNewPlaceImagePath = '';
            await this.fetchFoodPlaces();
            this.toastSuccess("Ресторан добавлен!");
        } catch (e) {
            this.toastError(`Ошибка: ${e.message}`);
        }
    },

    getManagerPlaceIds(manager) {
        return (manager.managed_place_ids || []).map(Number);
    },

    isManagerPlace(manager, placeId) {
        return this.getManagerPlaceIds(manager).includes(Number(placeId));
    },

    async toggleManagerPlace(manager, placeId) {
        const ids = this.getManagerPlaceIds(manager);
        let newIds;
        if (ids.includes(Number(placeId))) {
            newIds = ids.filter(id => id !== Number(placeId));
        } else {
            newIds = [...ids, Number(placeId)];
        }
        try {
            await this.apiRequest(`/users/${manager.id}/managed_places`, 'PUT', {
                food_place_ids: newIds
            });
            manager.managed_place_ids = newIds;
            this.toastSuccess("Рестораны обновлены!");
        } catch (e) {
            this.toastError(`Ошибка: ${e.message}`);
        }
    }
};
