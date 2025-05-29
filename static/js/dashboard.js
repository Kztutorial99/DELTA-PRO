// Dashboard specific functionality
class Dashboard {
    constructor() {
        this.charts = {};
        this.updateInterval = null;
        this.init();
    }

    init() {
        this.initCharts();
        this.startRealTimeUpdates();
        this.bindEvents();
    }

    initCharts() {
        this.createPerformanceChart();
    }

    createPerformanceChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;

        this.charts.performance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['No data available'],
                datasets: [{
                    label: 'CPU %',
                    data: [0],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Memory %',
                    data: [0],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Disk %',
                    data: [0],
                    borderColor: 'rgb(255, 206, 86)',
                    backgroundColor: 'rgba(255, 206, 86, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Usage %'
                        },
                        min: 0,
                        max: 100
                    }
                }
            }
        });
    }

    updateSystemStats() {
        // In a real application, this would fetch from the API
        // For now, we'll show that the system is ready to receive data
        const elements = {
            'cpu-usage': '0.0%',
            'memory-usage': '0.0%',
            'disk-usage': '0.0%',
            'uptime': 'System Ready'
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });

        // Update progress bars
        const progressElements = {
            'cpu-progress': 0,
            'memory-progress': 0,
            'disk-progress': 0
        };

        Object.entries(progressElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.style.width = value + '%';
            }
        });
    }

    updatePerformanceChart(timerange = '1h') {
        // In a real application, this would fetch data from the API
        // For now, we'll show an empty state
        if (this.charts.performance) {
            this.charts.performance.data.labels = ['Waiting for data...'];
            this.charts.performance.data.datasets.forEach(dataset => {
                dataset.data = [0];
            });
            this.charts.performance.update();
        }
    }

    updateAlerts() {
        // In a real application, this would fetch from the API
        const alertCount = document.getElementById('alert-count');
        const alertList = document.getElementById('alert-list');
        
        if (alertCount) {
            alertCount.textContent = '0';
        }
        
        if (alertList && !alertList.querySelector('.text-center')) {
            alertList.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-check-circle text-success fa-2x mb-2"></i>
                    <p class="text-muted mb-0">No active alerts</p>
                    <small class="text-muted">All systems operating normally</small>
                </div>
            `;
        }
    }

    startRealTimeUpdates() {
        // Update immediately
        this.updateSystemStats();
        this.updateAlerts();
        
        // Then update every 5 seconds
        this.updateInterval = setInterval(() => {
            this.updateSystemStats();
            this.updateAlerts();
        }, 5000);
    }

    bindEvents() {
        // Time range selector for performance chart
        const timeRangeButtons = document.querySelectorAll('input[name="timerange"]');
        timeRangeButtons.forEach(button => {
            button.addEventListener('change', (e) => {
                this.updatePerformanceChart(e.target.value);
            });
        });

        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                if (this.updateInterval) {
                    clearInterval(this.updateInterval);
                }
            } else {
                this.startRealTimeUpdates();
            }
        });
    }

    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.destroy();
            }
        });
    }
}

// Global functions for template usage
function acknowledgeAlert(alertId) {
    // In a real application, this would call the API
    console.log(`Acknowledging alert ${alertId}`);
    
    // Show success message
    const alertElement = document.querySelector(`[data-alert-id="${alertId}"]`);
    if (alertElement) {
        alertElement.classList.add('alert-acknowledged');
        
        // Remove after animation
        setTimeout(() => {
            alertElement.remove();
            
            // Update alert count
            const alertCount = document.getElementById('alert-count');
            if (alertCount) {
                const currentCount = parseInt(alertCount.textContent) || 0;
                alertCount.textContent = Math.max(0, currentCount - 1);
            }
        }, 1000);
    }
}

// Initialize dashboard when DOM is loaded
let dashboardInstance;
document.addEventListener('DOMContentLoaded', function() {
    dashboardInstance = new Dashboard();
});

// Cleanup when page is unloaded
window.addEventListener('beforeunload', function() {
    if (dashboardInstance) {
        dashboardInstance.destroy();
    }
});
