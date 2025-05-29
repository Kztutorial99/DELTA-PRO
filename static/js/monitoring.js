// Global monitoring functionality
class MonitoringSystem {
    constructor() {
        this.isOnline = true;
        this.lastUpdate = new Date();
        this.init();
    }

    init() {
        this.updateLastUpdateTime();
        this.startHeartbeat();
        this.bindGlobalEvents();
    }

    updateLastUpdateTime() {
        const lastUpdateElement = document.getElementById('last-update');
        if (lastUpdateElement) {
            const now = new Date();
            lastUpdateElement.textContent = now.toLocaleString();
            this.lastUpdate = now;
        }
    }

    startHeartbeat() {
        setInterval(() => {
            this.updateLastUpdateTime();
        }, 1000);
    }

    bindGlobalEvents() {
        // Handle connection status
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.showConnectionStatus('online');
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showConnectionStatus('offline');
        });

        // Handle errors globally
        window.addEventListener('error', (e) => {
            console.error('Global error:', e.error);
            this.showNotification('An error occurred', 'error');
        });

        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
            this.showNotification('Connection error', 'warning');
        });
    }

    showConnectionStatus(status) {
        const statusElement = document.querySelector('.navbar-text');
        if (statusElement) {
            const icon = statusElement.querySelector('i');
            const text = statusElement.childNodes[2]; // Text node after icon and space
            
            if (status === 'online') {
                icon.className = 'fas fa-circle text-success me-1';
                if (text) text.textContent = 'System Online';
            } else {
                icon.className = 'fas fa-circle text-danger me-1';
                if (text) text.textContent = 'System Offline';
            }
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 80px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;
        
        notification.innerHTML = `
            <i class="fas fa-${this.getIconForType(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    getIconForType(type) {
        const icons = {
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'danger': 'times-circle',
            'error': 'times-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Utility method for making API calls with error handling
    async apiCall(endpoint, options = {}) {
        try {
            const response = await fetch(endpoint, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API call failed for ${endpoint}:`, error);
            this.showNotification(`Failed to load data: ${error.message}`, 'error');
            throw error;
        }
    }

    // Format bytes to human readable format
    formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // Format uptime to human readable format
    formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        let result = '';
        if (days > 0) result += `${days} day${days !== 1 ? 's' : ''}, `;
        if (hours > 0) result += `${hours} hour${hours !== 1 ? 's' : ''}, `;
        result += `${minutes} minute${minutes !== 1 ? 's' : ''}`;
        
        return result;
    }

    // Get status color based on value and thresholds
    getStatusColor(value, warningThreshold = 70, criticalThreshold = 90) {
        if (value >= criticalThreshold) return 'danger';
        if (value >= warningThreshold) return 'warning';
        return 'success';
    }

    // Animate counter from current value to new value
    animateCounter(element, targetValue, duration = 1000) {
        if (!element) return;
        
        const startValue = parseFloat(element.textContent) || 0;
        const increment = (targetValue - startValue) / (duration / 16);
        let currentValue = startValue;
        
        const timer = setInterval(() => {
            currentValue += increment;
            
            if ((increment > 0 && currentValue >= targetValue) || 
                (increment < 0 && currentValue <= targetValue)) {
                currentValue = targetValue;
                clearInterval(timer);
            }
            
            element.textContent = currentValue.toFixed(1);
        }, 16);
    }
}

// Initialize monitoring system
let monitoringSystem;
document.addEventListener('DOMContentLoaded', function() {
    monitoringSystem = new MonitoringSystem();
});

// Utility functions available globally
function refreshPage() {
    window.location.reload();
}

function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleString();
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        if (monitoringSystem) {
            monitoringSystem.showNotification('Copied to clipboard', 'success');
        }
    }).catch(() => {
        if (monitoringSystem) {
            monitoringSystem.showNotification('Failed to copy to clipboard', 'error');
        }
    });
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { MonitoringSystem };
}
