export const cartState = {
    // Basket & Checkout Parameters variables
    activeBasket: null,
    basketItems: [],
    orderPhone: '',
    orderType: 'dinein',
    orderAddress: '',
    orderNotes: '',

    // COMPUTED FOR CART
    basketTotal() {
        return this.basketItems.reduce((acc, item) => acc + (item.menu_item?.price || 0) * item.item_quantity, 0);
    },

    // DATA FETCHING FOR CART
    async fetchActiveBasket() {
        if (!this.currentUser || !this.selectedFoodPlaceId) return;
        try {
            const baskets = await this.apiRequest('/food_baskets');
            const active = baskets.find(b => b.food_place_id === this.selectedFoodPlaceId && !b.is_ordered);
            if (active) {
                this.activeBasket = active;
                await this.fetchBasketItems(active.id);
            } else {
                this.activeBasket = null;
                this.basketItems = [];
            }
        } catch (e) {
            console.error("Error loading active basket", e);
        }
    },
    
    async fetchBasketItems(basketId) {
        try {
            this.basketItems = await this.apiRequest(`/food_baskets/${basketId}/basket_items`);
        } catch (e) {
            console.error("Error loading basket items", e);
        }
    },

    // SHOPPING CART ACTIONS
    async addToBasket(item) {
        if (!this.currentUser) {
            this.openAuthModal('login');
            return;
        }
        try {
            const body = { menu_item_id: item.id };
            await this.apiRequest('/food_baskets', 'POST', body);
            await this.fetchActiveBasket();
            this.toastSuccess(`${item.name} добавлен в корзину`);
        } catch (e) {
            this.toastError(`Ошибка добавления в корзину: ${e.message}`);
        }
    },
    
    async increaseBasketItem(bitem) {
        try {
            const body = { menu_item_id: bitem.menu_item_id };
            await this.apiRequest('/food_baskets', 'POST', body);
            await this.fetchActiveBasket();
        } catch (e) {
            this.toastError(`Ошибка: ${e.message}`);
        }
    },
    
    async decreaseBasketItem(bitem) {
        try {
            await this.apiRequest(`/food_baskets/basket_items/${bitem.id}`, 'DELETE');
            await this.fetchActiveBasket();
        } catch (e) {
            this.toastError(`Ошибка: ${e.message}`);
        }
    },
    
    async submitOrder() {
        if (!this.activeBasket) return;
        if (!this.orderPhone.trim()) {
            this.toastWarning("Пожалуйста, укажите контактный номер телефона.");
            return;
        }
        if (this.orderType === 'delivery' && !this.orderAddress.trim()) {
            this.toastWarning("Пожалуйста, укажите адрес доставки.");
            return;
        }
        
        try {
            const body = {
                order_type: this.orderType,
                phone: this.orderPhone,
                address: this.orderType === 'delivery' ? this.orderAddress : null
            };
            await this.apiRequest(`/food_baskets/${this.activeBasket.id}`, 'POST', body);
            
            this.successTitle = "Заказ принят!";
            this.successMessage = this.orderType === 'delivery'
                ? `Ваш предзаказ успешно оформлен. Доставка по адресу: ${this.orderAddress}. Номер телефона: ${this.orderPhone}.`
                : `Ваш предзаказ успешно оформлен к вашему визиту. Менеджер свяжется с вами по номеру ${this.orderPhone}.`;
            
            this.showSuccessModal = true;
            this.activeBasket = null;
            this.basketItems = [];
            this.orderPhone = '';
            this.orderAddress = '';
        } catch (e) {
            this.toastError(`Ошибка оформления заказа: ${e.message}`);
        }
    }
};
