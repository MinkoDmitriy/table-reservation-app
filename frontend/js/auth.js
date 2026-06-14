function decodeTokenPayload(token) {
    if (!token) return null;
    try {
        const parts = token.split('.');
        if (parts.length === 3) {
            return JSON.parse(atob(parts[1]));
        }
    } catch (e) { console.error("Token decoding error", e); }
    return null;
}

export function isTokenExpired(token) {
    const payload = decodeTokenPayload(token);
    if (!payload || !payload.exp) return true;
    return Date.now() >= payload.exp * 1000;
}

export const authState = {
    showAuthModal: false,
    authMode: 'login',
    loginUsername: '',
    loginPassword: '',
    regUsername: '',
    regPassword: '',
    currentUser: null,
    token: null,
    authError: '',
    isClient: false,
    isManager: false,
    isAdmin: false,

    recalcRoles() {
        if (!this.token || isTokenExpired(this.token)) {
            this.isAdmin = false;
            this.isManager = false;
            this.isClient = false;
            return;
        }
        const payload = decodeTokenPayload(this.token);
        const scopes = payload?.scopes || [];
        this.isAdmin = scopes.includes('admin:all');
        this.isManager = scopes.includes('orders:read') && !scopes.includes('admin:all');
        this.isClient = scopes.includes('orders:create') && !scopes.includes('orders:read') && !scopes.includes('admin:all');
    },

    openAuthModal(mode) {
        this.authMode = mode;
        this.showAuthModal = true;
        this.loginUsername = '';
        this.loginPassword = '';
        this.regUsername = '';
        this.regPassword = '';
        this.authError = '';
    },

    switchAuthMode(mode) {
        this.authMode = mode;
        this.authError = '';
    },
    
    async submitLogin() {
        try {
            this.authError = '';
            const body = { username: this.loginUsername, password: this.loginPassword };
            const data = await this.apiRequest('/auth/login', 'POST', body);
            
            this.token = data.access_token;
            this.currentUser = { id: data.user.id, username: data.user.username };
            
            localStorage.setItem('token', this.token);
            localStorage.setItem('user', JSON.stringify(this.currentUser));
            this.showAuthModal = false;
            this.recalcRoles();

            if (this.isAdmin) {
                await this.fetchAdminData();
            } else if (this.isManager) {
                await this.fetchManagerData();
            } else if (this.selectedFoodPlaceId) {
                await this.fetchActiveBasket();
            }
        } catch (e) {
            this.authError = `Ошибка входа: ${e.message}`;
        }
    },
    
    async submitRegister() {
        try {
            this.authError = '';
            const body = { username: this.regUsername, password: this.regPassword };
            const data = await this.apiRequest('/auth/register', 'POST', body);
            
            this.token = data.access_token;
            this.currentUser = { id: data.user.id, username: data.user.username };
            
            localStorage.setItem('token', this.token);
            localStorage.setItem('user', JSON.stringify(this.currentUser));
            this.showAuthModal = false;
            this.recalcRoles();
            
            if (this.selectedFoodPlaceId) {
                await this.fetchActiveBasket();
            }
        } catch (e) {
            this.authError = `Ошибка регистрации: ${e.message}`;
        }
    },
    
    logout() {
        this.token = null;
        this.currentUser = null;
        this.isClient = false;
        this.isManager = false;
        this.isAdmin = false;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('currentView');
        this.activeBasket = null;
        this.basketItems = [];
        this.currentView = 'cities';
    }
};
