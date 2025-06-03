/**
 * Twitter Analiz Platformu - Ana JavaScript Dosyası
 * ================================================
 */

// Global değişkenler
window.TwitterAnaliz = {
    config: {
        apiBase: '/api',
        analysisBase: '/analiz',
        refreshInterval: 5000
    },
    state: {
        currentAnalysis: null,
        selectedFiles: new Set(),
        theme: localStorage.getItem('theme') || 'auto',
        language: document.documentElement.lang || 'tr'
    }
};

// DOM hazır olduğunda çalışacak fonksiyonlar
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    initializeLanguage();
    initializeGlobalEventListeners();
    checkSystemHealth();
});

/**
 * Tema Yönetimi
 */
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'auto';
    setTheme(savedTheme);
}

function setTheme(theme) {
    const htmlElement = document.documentElement;
    
    if (theme === 'auto') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        htmlElement.setAttribute('data-bs-theme', prefersDark ? 'dark' : 'light');
    } else {
        htmlElement.setAttribute('data-bs-theme', theme);
    }
    
    localStorage.setItem('theme', theme);
    TwitterAnaliz.state.theme = theme;
}

// Sistem tema değişikliklerini dinle
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
    if (TwitterAnaliz.state.theme === 'auto') {
        setTheme('auto');
    }
});

/**
 * Dil Yönetimi
 */
function initializeLanguage() {
    TwitterAnaliz.state.language = document.documentElement.lang || 'tr';
}

function setLanguage(languageCode) {
    // API üzerinden dil değişikliği yap
    fetch('/language/api/set-language', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language: languageCode })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Sayfa yeniden yükle
            window.location.reload();
        } else {
            console.error('Language change error:', data.message);
            showAlert('danger', 'Language change failed!');
        }
    })
    .catch(error => {
        console.error('Language change request error:', error);
        showAlert('danger', 'Language change failed!');
    });
}

/**
 * Global Event Listeners
 */
function initializeGlobalEventListeners() {
    // Escape tuşu ile modal'ları kapat
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            });
        }
    });
    
    // Form submission'larını engellemek için
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
        });
    });
}

/**
 * Sistem Sağlık Kontrolü
 */
function checkSystemHealth() {
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateSystemStatus('online');
            } else {
                updateSystemStatus('warning');
            }
        })
        .catch(error => {
            console.error('System health check error:', error);
            updateSystemStatus('offline');
        });
}

function updateSystemStatus(status) {
    const statusElement = document.getElementById('systemStatus');
    if (statusElement) {
        statusElement.className = 'badge';
        
        // Get text content based on status and current language
        let text = '';
        const currentLang = document.documentElement.lang || 'tr';
        
        if (currentLang === 'en') {
            switch (status) {
                case 'online':
                    text = 'Online';
                    break;
                case 'warning':
                    text = 'Warning';
                    break;
                case 'offline':
                    text = 'Offline';
                    break;
            }
        } else {
            switch (status) {
                case 'online':
                    text = 'Çevrimiçi';
                    break;
                case 'warning':
                    text = 'Uyarı';
                    break;
                case 'offline':
                    text = 'Çevrimdışı';
                    break;
            }
        }
        
        switch (status) {
            case 'online':
                statusElement.classList.add('bg-success');
                statusElement.innerHTML = '<i class="bi bi-check-circle"></i> ' + text;
                break;
            case 'warning':
                statusElement.classList.add('bg-warning');
                statusElement.innerHTML = '<i class="bi bi-exclamation-triangle"></i> ' + text;
                break;
            case 'offline':
                statusElement.classList.add('bg-danger');
                statusElement.innerHTML = '<i class="bi bi-x-circle"></i> ' + text;
                break;
        }
    }
}

/**
 * API Yardımcı Fonksiyonları
 */
const API = {
    async get(endpoint) {
        try {
            const response = await fetch(TwitterAnaliz.config.apiBase + endpoint);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API GET error:', error);
            throw error;
        }
    },
    
    async post(endpoint, data) {
        try {
            const response = await fetch(TwitterAnaliz.config.apiBase + endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('API POST error:', error);
            throw error;
        }
    },
    
    async delete(endpoint) {
        try {
            const response = await fetch(TwitterAnaliz.config.apiBase + endpoint, {
                method: 'DELETE'
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API DELETE error:', error);
            throw error;
        }
    }
};

/**
 * Loading Modal Yönetimi
 */
function showLoading(message, progress = 0) {
    // Use default processing message if none provided
    if (!message) {
        const currentLang = document.documentElement.lang || 'tr';
        message = currentLang === 'en' ? 'Processing...' : 'İşlem yapılıyor...';
    }
    
    const modal = document.getElementById('loadingModal');
    const messageElement = document.getElementById('loadingMessage');
    const progressElement = document.getElementById('loadingProgress');
    
    if (messageElement) messageElement.textContent = message;
    if (progressElement) progressElement.style.width = progress + '%';
    
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

function updateLoading(message, progress) {
    const messageElement = document.getElementById('loadingMessage');
    const progressElement = document.getElementById('loadingProgress');
    
    if (messageElement) messageElement.textContent = message;
    if (progressElement) progressElement.style.width = progress + '%';
}

function hideLoading() {
    const modal = document.getElementById('loadingModal');
    const modalInstance = bootstrap.Modal.getInstance(modal);
    if (modalInstance) {
        modalInstance.hide();
    }
}

/**
 * Alert/Notification Sistemi
 */
function showAlert(type, message, duration = 5000) {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    const alertId = 'alert-' + Date.now();
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert" id="${alertId}">
            <i class="bi bi-${getAlertIcon(type)}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHTML);
    
    // Auto-dismiss
    if (duration > 0) {
        setTimeout(() => {
            const alertElement = document.getElementById(alertId);
            if (alertElement) {
                const alert = bootstrap.Alert.getOrCreateInstance(alertElement);
                alert.close();
            }
        }, duration);
    }
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle',
        'primary': 'info-circle',
        'secondary': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Dosya Boyutu Formatı
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Tarih Formatı
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('tr-TR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Sayı Formatı (Türkçe)
 */
function formatNumber(number) {
    return number.toLocaleString('tr-TR');
}

/**
 * Analiz Durumu İkonu
 */
function getStatusIcon(status) {
    const icons = {
        'beklemede': 'clock',
        'çalışıyor': 'gear-fill',
        'tamamlandı': 'check-circle-fill',
        'hata': 'x-circle-fill'
    };
    return icons[status] || 'question-circle';
}

function getStatusClass(status) {
    const classes = {
        'beklemede': 'text-warning',
        'çalışıyor': 'text-info',
        'tamamlandı': 'text-success',
        'hata': 'text-danger'
    };
    return classes[status] || 'text-muted';
}

/**
 * Local Storage Helpers
 */
const Storage = {
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('LocalStorage set error:', error);
        }
    },
    
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('LocalStorage get error:', error);
            return defaultValue;
        }
    },
    
    remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('LocalStorage remove error:', error);
        }
    }
};

/**
 * Clipboard Helpers
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showAlert('success', 'Panoya kopyalandı!', 2000);
    } catch (error) {
        console.error('Clipboard error:', error);
        showAlert('danger', 'Panoya kopyalama başarısız!');
    }
}

/**
 * Debounce Fonksiyonu
 */
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

/**
 * Throttle Fonksiyonu
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Analiz Progress Tracking
 */
function trackAnalysisProgress(analysisId) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`${TwitterAnaliz.config.analysisBase}/durum/${analysisId}`);
            const data = await response.json();
            
            if (data.success) {
                const status = data.data;
                updateLoading(
                    status.durum === 'çalışıyor' ? 'Analiz devam ediyor...' : status.durum,
                    status.ilerleme || 0
                );
                
                if (status.durum === 'tamamlandı' || status.durum === 'hata') {
                    clearInterval(interval);
                    hideLoading();
                    
                    if (status.durum === 'tamamlandı') {
                        showAlert('success', 'Analiz başarıyla tamamlandı!');
                        // Sonuçlar sayfasına yönlendir
                        setTimeout(() => {
                            window.location.href = `/sonuclar/${analysisId}`;
                        }, 1500);
                    } else {
                        showAlert('danger', 'Analiz sırasında hata oluştu: ' + status.hata);
                    }
                }
            }
        } catch (error) {
            console.error('Analiz durumu kontrolü hatası:', error);
            clearInterval(interval);
            hideLoading();
            showAlert('danger', 'Analiz durumu kontrol edilemedi.');
        }
    }, TwitterAnaliz.config.refreshInterval);
    
    return interval;
}

/**
 * Chart Helpers
 */
const ChartHelpers = {
    defaultColors: [
        '#007bff', '#28a745', '#ffc107', '#dc3545', '#6c757d',
        '#17a2b8', '#e83e8c', '#fd7e14', '#20c997', '#6f42c1'
    ],
    
    createPieChart(ctx, data, options = {}) {
        return new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: options.colors || this.defaultColors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.raw / total) * 100).toFixed(1);
                                return `${context.label}: ${context.raw} (${percentage}%)`;
                            }
                        }
                    }
                },
                ...options
            }
        });
    },
    
    createBarChart(ctx, data, options = {}) {
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: options.label || 'Veri',
                    data: data.values,
                    backgroundColor: options.colors || this.defaultColors[0],
                    borderColor: options.borderColors || this.defaultColors[0],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: !!options.label
                    }
                },
                ...options
            }
        });
    }
};

// Global scope'a bazı fonksiyonları ekle
window.setTheme = setTheme;
window.showAlert = showAlert;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.updateLoading = updateLoading;
window.API = API;
window.Storage = Storage;
window.copyToClipboard = copyToClipboard;
window.formatFileSize = formatFileSize;
window.formatDate = formatDate;
window.formatNumber = formatNumber;
window.ChartHelpers = ChartHelpers; 