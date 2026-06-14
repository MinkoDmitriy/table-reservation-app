export const toastState = {
    toasts: [],
    _counter: 0,

    showToast(message, type = 'info', duration = 4000) {
        const id = ++this._counter;
        this.toasts.push({ id, message, type });
        if (duration > 0) {
            setTimeout(() => this.removeToast(id), duration);
        }
    },

    removeToast(id) {
        this.toasts = this.toasts.filter(t => t.id !== id);
    },

    toastSuccess(message) {
        this.showToast(message, 'success', 4000);
    },

    toastError(message) {
        this.showToast(message, 'error', 6000);
    },

    toastWarning(message) {
        this.showToast(message, 'warning', 5000);
    },

    toastInfo(message) {
        this.showToast(message, 'info', 4000);
    }
};

export function showConfirm(message) {
    return new Promise((resolve) => {
        const modal = document.getElementById('confirmModal');
        const msgEl = document.getElementById('confirmMessage');
        const okBtn = document.getElementById('confirmOkBtn');
        const cancelBtn = document.getElementById('confirmCancelBtn');
        msgEl.textContent = message;
        modal.classList.add('active');
        const cleanup = (result) => {
            modal.classList.remove('active');
            okBtn.removeEventListener('click', onOk);
            cancelBtn.removeEventListener('click', onCancel);
            resolve(result);
        };
        const onOk = () => cleanup(true);
        const onCancel = () => cleanup(false);
        okBtn.addEventListener('click', onOk);
        cancelBtn.addEventListener('click', onCancel);
    });
}
