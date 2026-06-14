export const historyState = {
    userHistory: [],

    async fetchUserHistory() {
        if (!this.currentUser) return;
        try {
            this.userHistory = await this.apiRequest('/ratings/user/history');
        } catch (e) {
            console.error("Error loading history", e);
            this.userHistory = [];
        }
    },

    async goToHistory() {
        if (!this.currentUser) {
            this.openAuthModal('login');
            return;
        }
        await this.fetchUserHistory();
        this.currentView = 'history';
    },

    formatHistoryDate(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        const dd = String(d.getDate()).padStart(2, '0');
        const mm = String(d.getMonth() + 1).padStart(2, '0');
        const yyyy = d.getFullYear();
        const hh = String(d.getHours()).padStart(2, '0');
        const min = String(d.getMinutes()).padStart(2, '0');
        return `${dd}.${mm}.${yyyy} ${hh}:${min}`;
    },

    getHistoryStatusDisplay(status) {
        const map = {
            'new': 'Новый',
            'preparing': 'Готовится',
            'ready': 'Готов',
            'completed': 'Завершен',
            'cancelled': 'Отменен',
            'active': 'Активно'
        };
        return map[status] || status;
    }
};
