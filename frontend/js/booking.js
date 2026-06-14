export const bookingState = {
    // Reservation Parameters variables
    resDate: '',
    resTime: '',
    resGuests: 2,
    resComments: '',
    resPhone: '',

    // DATA FETCHING FOR BOOKING
    async fetchTables(placeId) {
        try {
            this.foodTables = await this.apiRequest(`/food_tables?food_place_id=${placeId}`);
        } catch (e) {
            console.error("Error loading tables", e);
        }
    },
    
    async fetchOccupiedTables() {
        if (!this.selectedFoodPlaceId || !this.resDate || !this.resTime) return;
        try {
            const url = `/reservations/occupied?food_place_id=${this.selectedFoodPlaceId}&date=${this.resDate}&start_time=${this.resTime}`;
            this.occupiedTableIds = await this.apiRequest(url);
        } catch (e) {
            console.error("Error loading occupied tables", e);
        }
    },

    // ACTIONS FOR BOOKING
    onReservationParamChange() {
        this.selectedTableId = null;
        this.selectedTable = null;
        this.fetchOccupiedTables();
    },
    
    selectTable(table) {
        if (this.occupiedTableIds.includes(table.id)) {
            this.toastWarning("Этот столик уже забронирован на выбранное время. Пожалуйста, укажите другое время или выберите другой стол.");
            return;
        }
        if (table.max_seats < this.resGuests) {
            this.toastWarning(`Этот столик рассчитан максимум на ${table.max_seats} человек. Выберите стол побольше или уменьшите количество гостей.`);
            return;
        }
        if (this.selectedTableId === table.id) {
            this.selectedTableId = null;
            this.selectedTable = null;
        } else {
            this.selectedTableId = table.id;
            this.selectedTable = table;
        }
    },
    
    // RESERVATION ACTION
    async submitReservation() {
        if (!this.currentUser) {
            this.openAuthModal('login');
            return;
        }
        if (!this.selectedTableId || !this.resDate || !this.resTime) {
            this.toastWarning("Пожалуйста, заполните параметры бронирования и выберите столик.");
            return;
        }
        if (!this.resPhone.trim()) {
            this.toastWarning("Пожалуйста, укажите номер телефона.");
            return;
        }
        
        try {
            const body = {
                date: this.resDate,
                start_time: this.resTime,
                duration_in_minutes: 120,
                food_table_id: this.selectedTableId,
                phone: this.resPhone,
                comments: this.resComments || null
            };
            await this.apiRequest('/reservations/date_and_time', 'POST', body);
            
            this.successTitle = "Бронь оформлена!";
            this.successMessage = `Стол №${this.selectedTable.table_number} успешно забронирован на ${this.resDate} к ${this.resTime}. Ждем вас!`;
            this.showSuccessModal = true;
            
            this.selectedTableId = null;
            this.selectedTable = null;
            await this.fetchOccupiedTables();
        } catch (e) {
            this.toastError(`Ошибка бронирования: ${e.message}`);
        }
    }
};
