import { apiState } from './api.js';
import { authState, isTokenExpired } from './auth.js';
import { bookingState } from './booking.js';
import { cartState } from './cart.js';
import { dashboardState } from './dashboard.js';
import { ratingState } from './rating.js';
import { historyState } from './history.js';
import { toastState } from './toast.js';

function app() {
    return {
        // Navigation & Views
        currentView: 'cities',
        currentTab: 'reservation',
        selectedCategory: 'all',
        
        // Hamburger menu
        showUserMenu: false,
        isLoading: true,

        // Profile state
        profileName: '',
        profilePhone: '',
        userPhone: '',
        
        // Success Modal State
        showSuccessModal: false,
        successTitle: '',
        successMessage: '',
        
        // Data lists
        locations: [],
        foodPlaces: [],
        foodTables: [],
        menuItems: [],
        occupiedTableIds: [],
        
        // Selections
        selectedLocationId: '',
        selectedLocationName: '',
        selectedFoodPlaceId: null,
        selectedFoodPlace: null,
        selectedTableId: null,
        selectedTable: null,

        // Spread state and methods from modules
        ...apiState,
        ...authState,
        ...bookingState,
        ...cartState,
        ...dashboardState,
        ...ratingState,
        ...historyState,
        ...toastState,

        // INITIALIZE
        init() {
            // Restore token session
            const storedToken = localStorage.getItem('token');
            const storedUser = localStorage.getItem('user');
            if (storedToken && storedUser) {
                if (!isTokenExpired(storedToken)) {
                    this.token = storedToken;
                    this.currentUser = JSON.parse(storedUser);
                    this.recalcRoles();
                } else {
                    localStorage.removeItem('token');
                    localStorage.removeItem('user');
                    localStorage.removeItem('currentView');
                }
            }
            
            // Restore current view
            const savedView = localStorage.getItem('currentView');
            if (savedView) {
                this.currentView = savedView;
            }

            // Restore current tab
            const savedTab = localStorage.getItem('currentTab');
            if (savedTab) {
                this.currentTab = savedTab;
            }

            // Restore selections
            const savedLocationId = localStorage.getItem('selectedLocationId');
            const savedLocationName = localStorage.getItem('selectedLocationName');
            if (savedLocationId) {
                this.selectedLocationId = parseInt(savedLocationId);
                this.selectedLocationName = savedLocationName || '';
            }

            const savedFoodPlaceId = localStorage.getItem('selectedFoodPlaceId');
            if (savedFoodPlaceId) {
                this.selectedFoodPlaceId = parseInt(savedFoodPlaceId);
            }
            
            // Set date to today
            const today = new Date().toISOString().split('T')[0];
            this.resDate = today;
            
            Promise.all([
                this.fetchLocations(),
                this.fetchFoodPlaces()
            ]).then(async () => {
                if (this.selectedFoodPlaceId) {
                    this.selectedFoodPlace = this.foodPlaces.find(p => p.id === this.selectedFoodPlaceId) || null;
                    if (this.selectedFoodPlace && this.currentView === 'detail') {
                        await Promise.all([
                            this.fetchTables(this.selectedFoodPlaceId),
                            this.fetchMenuItems(this.selectedFoodPlaceId),
                            this.fetchOccupiedTables(),
                            this.fetchActiveBasket(),
                            this.initPlaceRating(this.selectedFoodPlaceId)
                        ]);
                    }
                }
                if (this.currentView === 'admin' && this.isAdmin) {
                    await this.fetchAdminData();
                }
                if (this.currentView === 'manager' && (this.isAdmin || this.isManager)) {
                    await this.fetchLocations();
                    await this.fetchFoodPlaces();
                    await this.fetchManagerData();
                    if (this.managerCities().length > 0 && !this.managerSelectedCityId) {
                        this.managerSelectedCityId = this.managerCities()[0].id;
                    }
                    if (this.managerFilteredPlaceIds().length > 0 && !this.managerSelectedPlaceId) {
                        this.managerSelectedPlaceId = this.managerFilteredPlaceIds()[0];
                    }
                    await this.refreshManagerData();
                }
                this.isLoading = false;
            }).catch(() => {
                this.isLoading = false;
            });

            // Persist current view across reloads
            this.$watch('currentView', (val) => {
                localStorage.setItem('currentView', val);
                this.showUserMenu = false;
            });

            this.$watch('currentTab', (val) => {
                localStorage.setItem('currentTab', val);
            });

            // Load user phone from profile
            if (this.currentUser) {
                this.apiRequest('/users/me').then(data => {
                    if (data.phone) {
                        this.userPhone = data.phone;
                        this.orderPhone = data.phone;
                        this.resPhone = data.phone;
                    }
                }).catch(() => {});
            }

            this._initialized = true;
        },

        // Global Navigation Actions
        goToHome() {
            this.currentView = 'cities';
            localStorage.setItem('currentView', 'cities');
            this.selectedFoodPlaceId = null;
            this.selectedFoodPlace = null;
            this.selectedTableId = null;
            this.selectedTable = null;
            localStorage.removeItem('selectedFoodPlaceId');
        },

        // DATA FETCHING
        async fetchLocations() {
            try {
                this.locations = await this.apiRequest('/locations');
            } catch (e) {
                console.error("Error loading locations", e);
            }
        },
        
        async fetchFoodPlaces() {
            try {
                this.foodPlaces = await this.apiRequest('/food_places');
            } catch (e) {
                console.error("Error loading restaurants", e);
            }
        },

        async fetchMenuItems(placeId) {
            if (!placeId) {
                this.menuItems = [];
                return;
            }

            try {
                this.menuItems = await this.apiRequest(`/food_places/${placeId}/menu_items`);
            } catch (e) {
                console.error("Error loading menu items", e);
                this.menuItems = [];
            }
        },

        get filteredFoodPlaces() {
            if (!this.selectedLocationId) return [];
            return this.foodPlaces.filter(fp => fp.location_id === this.selectedLocationId);
        },
        
        get filteredMenuItems() {
            if (this.selectedCategory === 'all') return this.menuItems;
            return this.menuItems.filter(item => {
                const name = item.name.toLowerCase();
                if (this.selectedCategory === 'starters') {
                    return name.includes('пицца') || name.includes('ролл') || name.includes('блины') || name.includes('закуск');
                }
                if (this.selectedCategory === 'mains') {
                    return name.includes('паста') || name.includes('стейк') || name.includes('рамен') || name.includes('сет') || name.includes('бефстроганов');
                }
                if (this.selectedCategory === 'desserts') {
                    return name.includes('тирамису') || name.includes('моти') || name.includes('десерт');
                }
                if (this.selectedCategory === 'drinks') {
                    return name.includes('лимонад') || name.includes('чай') || name.includes('напит') || name.includes('сентя');
                }
                return true;
            });
        },

        selectCity(id, name) {
            this.selectedLocationId = id;
            this.selectedLocationName = name;
            this.currentView = 'restaurants';
            localStorage.setItem('selectedLocationId', id);
            localStorage.setItem('selectedLocationName', name);
        },
        
        async selectRestaurant(place) {
            this.selectedFoodPlaceId = place.id;
            this.selectedFoodPlace = place;
            this.currentView = 'detail';
            this.currentTab = 'reservation';
            this.selectedTableId = null;
            this.selectedTable = null;
            this.selectedCategory = 'all';
            localStorage.setItem('selectedFoodPlaceId', place.id);
            
            await Promise.all([
                this.fetchTables(place.id),
                this.fetchMenuItems(place.id),
                this.fetchOccupiedTables(),
                this.fetchActiveBasket(),
                this.initPlaceRating(place.id)
            ]);
        },
        
        onLocationChange() {
            if (!this._initialized) return;
            if (this.selectedLocationId) {
                const loc = this.locations.find(l => l.id === this.selectedLocationId);
                this.selectedLocationName = loc ? loc.name : '';
                this.currentView = 'restaurants';
            }
        },

        async selectRestaurantById(placeId) {
            const place = this.foodPlaces.find(fp => fp.id === placeId);
            if (place) {
                await this.selectRestaurant(place);
            }
        },

        async goToManagerPanel() {
            this.currentView = 'manager';
            localStorage.setItem('currentView', 'manager');
            this.managerTab = 'orders';
            await this.fetchLocations();
            await this.fetchFoodPlaces();
            await this.fetchManagerData();
            if (this.managerCities().length > 0 && !this.managerSelectedCityId) {
                this.managerSelectedCityId = this.managerCities()[0].id;
            }
            if (this.managerFilteredPlaceIds().length > 0 && !this.managerSelectedPlaceId) {
                this.managerSelectedPlaceId = this.managerFilteredPlaceIds()[0];
            }
            await this.refreshManagerData();
        },

        async goToAdminPanel() {
            this.currentView = 'admin';
            localStorage.setItem('currentView', 'admin');
            this.adminTab = 'users';
            await this.fetchAdminData();
            await this.fetchLocations();
            await this.fetchFoodPlaces();
        },

        getPlaceNameById(id) {
            const place = this.foodPlaces.find(p => p.id === id);
            return place ? place.name : `Ресторан #${id}`;
        },

        getLocationNameById(id) {
            const loc = this.locations.find(l => l.id === id);
            return loc ? loc.name : `Город #${id}`;
        },

        toggleUserMenu() {
            this.showUserMenu = !this.showUserMenu;
        },

        closeUserMenu() {
            this.showUserMenu = false;
        },

        async goToProfile() {
            this.currentView = 'profile';
            localStorage.setItem('currentView', 'profile');
            try {
                const me = await this.apiRequest('/users/me');
                this.profileName = me.name || this.currentUser?.username || '';
                this.profilePhone = me.phone || '';
            } catch (e) {
                this.toastError('Ошибка загрузки профиля: ' + e.message);
            }
        },

        async updateProfile() {
            if (!this.profileName.trim()) {
                this.toastWarning('Имя не может быть пустым');
                return;
            }
            try {
                const data = await this.apiRequest('/users/me', 'PUT', {
                    name: this.profileName,
                    phone: this.profilePhone || null
                });
                this.currentUser.username = data.name;
                localStorage.setItem('user', JSON.stringify(this.currentUser));
                if (data.phone) {
                    this.userPhone = data.phone;
                    this.orderPhone = data.phone;
                    this.resPhone = data.phone;
                }
                this.toastSuccess('Профиль обновлён');
            } catch (e) {
                this.toastError('Ошибка: ' + e.message);
            }
        }
    };
}

// Bind Alpine component
document.addEventListener('alpine:init', () => {
    Alpine.data('app', app);
});

// Dynamically load Alpine.js to ensure it runs after ES modules execute
const script = document.createElement('script');
script.src = "https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js";
script.defer = true;
document.head.appendChild(script);

export default app;
