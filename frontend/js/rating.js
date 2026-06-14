export const ratingState = {
    placeRatingStats: {},
    userRatings: {},
    canRateFlags: {},
    hoveredStar: 0,
    selectedStar: 0,

    async fetchPlaceRatingStats(placeId) {
        try {
            const data = await this.apiRequest(`/ratings/food_place/${placeId}`);
            this.placeRatingStats = { ...this.placeRatingStats, [placeId]: data };
        } catch (e) {
            console.error("Error loading rating stats", e);
        }
    },

    async fetchUserRating(placeId) {
        if (!this.currentUser) return;
        try {
            const data = await this.apiRequest(`/ratings/user/${placeId}`);
            this.userRatings = { ...this.userRatings, [placeId]: data };
            this.selectedStar = data?.score || 0;
        } catch (e) {
            console.error("Error loading user rating", e);
        }
    },

    async fetchCanRate(placeId) {
        if (!this.currentUser) {
            this.canRateFlags = { ...this.canRateFlags, [placeId]: false };
            return;
        }
        try {
            const data = await this.apiRequest(`/ratings/user/${placeId}/can_rate`);
            this.canRateFlags = { ...this.canRateFlags, [placeId]: data.can_rate };
        } catch (e) {
            this.canRateFlags = { ...this.canRateFlags, [placeId]: false };
        }
    },

    getRatingDisplay(placeId) {
        const stats = this.placeRatingStats[placeId];
        if (!stats || stats.ratings_count < 20) return null;
        return stats;
    },

    getRatingText(placeId) {
        const stats = this.placeRatingStats[placeId];
        if (!stats) return '';
        if (stats.ratings_count < 20) {
            return `(${stats.ratings_count} оценок)`;
        }
        return `${stats.avg_rating} (${stats.ratings_count} оценок)`;
    },

    async submitRating(placeId, score) {
        if (!this.currentUser) {
            this.openAuthModal('login');
            return;
        }
        try {
            const data = await this.apiRequest('/ratings', 'POST', { food_place_id: placeId, score });
            if (data.deleted) {
                this.selectedStar = 0;
            } else {
                this.selectedStar = data.score;
            }
            await this.fetchPlaceRatingStats(placeId);
            await this.fetchUserRating(placeId);
        } catch (e) {
            const msg = e.message || '';
            if (msg.includes('403') || msg.includes('оценить только те заведения')) {
                this.toastWarning("Вы можете оценить только те заведения, в которых заказывали или бронировали столик.");
            } else {
                console.error("Error submitting rating", e);
            }
        }
    },

    initPlaceRating(placeId) {
        this.fetchPlaceRatingStats(placeId);
        this.fetchUserRating(placeId);
        this.fetchCanRate(placeId);
        this.hoveredStar = 0;
    }
};
