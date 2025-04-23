// 配置
const CONFIG = {
    // 低余额警告阈值（度）
    LOW_BALANCE_THRESHOLD: 50,
    // 中等余额警告阈值（度）
    MEDIUM_BALANCE_THRESHOLD: 100,
    // 数据文件路径
    DATA_URL: 'data.json',
    // 刷新间隔（毫秒）- 每小时刷新一次
    REFRESH_INTERVAL: 60 * 60 * 1000,
    // 图表颜色
    CHART_COLORS: {
        balance: 'rgba(74, 111, 165, 0.7)',
        usage: 'rgba(76, 181, 245, 0.7)',
        borderBalance: 'rgba(74, 111, 165, 1)',
        borderUsage: 'rgba(76, 181, 245, 1)',
    }
};

// 全局变量
let balanceChart = null;
let usageChart = null;
let meterData = null;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    fetchData();
    
    // 设置定时刷新
    setInterval(fetchData, CONFIG.REFRESH_INTERVAL);
});

// 获取数据
async function fetchData() {
    try {
        const response = await fetch(CONFIG.DATA_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        meterData = await response.json();
        
        // 更新UI
        updateDashboard();
        updateCharts();
        updateTable();
        updateLastUpdated();
        
    } catch (error) {
        console.error('获取数据失败:', error);
        document.getElementById('last-updated').textContent = '获取数据失败，请稍后再试';
    }
}

// 更新仪表盘
function updateDashboard() {
    if (!meterData || !meterData.daily_data || meterData.daily_data.length === 0) {
        return;
    }
    
    // 获取最新数据
    const latestData = meterData.daily_data[meterData.daily_data.length - 1];
    const currentBalance = latestData.balance;
    
    // 计算昨日用电量
    let yesterdayUsage = 0;
    if (meterData.daily_data.length >= 2) {
        const yesterday = meterData.daily_data[meterData.daily_data.length - 2];
        const today = meterData.daily_data[meterData.daily_data.length - 1];
        yesterdayUsage = yesterday.balance - today.balance;
        // 如果有充值，可能会是负数，这种情况下显示为0
        yesterdayUsage = Math.max(0, yesterdayUsage);
    }
    
    // 计算7日平均用电量
    let avgUsage = 0;
    if (meterData.daily_data.length >= 2) {
        const recentData = meterData.daily_data.slice(-8); // 获取最近8天数据
        let totalUsage = 0;
        let days = 0;
        
        for (let i = 0; i < recentData.length - 1; i++) {
            const usage = recentData[i].balance - recentData[i + 1].balance;
            if (usage > 0) { // 只计算正的用电量（排除充值的情况）
                totalUsage += usage;
                days++;
            }
        }
        
        avgUsage = days > 0 ? (totalUsage / days) : 0;
    }
    
    // 预计可用天数
    const estimatedDays = avgUsage > 0 ? Math.floor(currentBalance / avgUsage) : '∞';
    
    // 更新UI
    const currentBalanceElement = document.getElementById('current-balance');
    currentBalanceElement.textContent = currentBalance.toFixed(2);
    
    // 根据余额设置颜色
    if (currentBalance <= CONFIG.LOW_BALANCE_THRESHOLD) {
        currentBalanceElement.classList.add('low-balance');
    } else if (currentBalance <= CONFIG.MEDIUM_BALANCE_THRESHOLD) {
        currentBalanceElement.classList.add('medium-balance');
    }
    
    document.getElementById('yesterday-usage').textContent = yesterdayUsage.toFixed(2);
    document.getElementById('avg-usage').textContent = avgUsage.toFixed(2);
    document.getElementById('estimated-days').textContent = estimatedDays.toString();
}

// 更新图表
function updateCharts() {
    if (!meterData || !meterData.daily_data || meterData.daily_data.length === 0) {
        return;
    }
    
    // 准备数据
    const dates = [];
    const balances = [];
    const usages = [];
    
    // 按日期排序
    const sortedData = [...meterData.daily_data].sort((a, b) => new Date(a.date) - new Date(b.date));
    
    // 只取最近7天的数据
    const recentData = sortedData.slice(-7);
    
    for (let i = 0; i < recentData.length; i++) {
        const data = recentData[i];
        const date = new Date(data.date);
        const formattedDate = `${date.getMonth() + 1}/${date.getDate()}`;
        
        dates.push(formattedDate);
        balances.push(data.balance);
        
        // 计算用电量（当天与前一天的差值）
        if (i > 0) {
            const usage = Math.max(0, recentData[i-1].balance - data.balance);
            usages.push(usage);
        } else if (i === 0 && recentData.length > 1) {
            // 对于第一天，我们没有前一天的数据，所以用第二天的数据来估算
            const usage = Math.max(0, data.balance - recentData[i+1].balance);
            usages.push(usage);
        } else {
            usages.push(0);
        }
    }
    
    // 更新用电量图表
    updateUsageChart(dates, usages);
    
    // 更新余额图表
    updateBalanceChart(dates, balances);
}

// 更新用电量图表
function updateUsageChart(labels, data) {
    const ctx = document.getElementById('usageChart').getContext('2d');
    
    if (usageChart) {
        usageChart.destroy();
    }
    
    usageChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '日用电量 (度)',
                data: data,
                backgroundColor: CONFIG.CHART_COLORS.usage,
                borderColor: CONFIG.CHART_COLORS.borderUsage,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '用电量 (度)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '日期'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `用电量: ${context.raw.toFixed(2)} 度`;
                        }
                    }
                }
            }
        }
    });
}

// 更新余额图表
function updateBalanceChart(labels, data) {
    const ctx = document.getElementById('balanceChart').getContext('2d');
    
    if (balanceChart) {
        balanceChart.destroy();
    }
    
    balanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '电表余额 (度)',
                data: data,
                backgroundColor: CONFIG.CHART_COLORS.balance,
                borderColor: CONFIG.CHART_COLORS.borderBalance,
                borderWidth: 2,
                tension: 0.1,
                fill: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    title: {
                        display: true,
                        text: '余额 (度)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '日期'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `余额: ${context.raw.toFixed(2)} 度`;
                        }
                    }
                }
            }
        }
    });
}

// 更新数据表格
function updateTable() {
    if (!meterData || !meterData.daily_data || meterData.daily_data.length === 0) {
        return;
    }
    
    const tableBody = document.getElementById('data-table-body');
    tableBody.innerHTML = '';
    
    // 按日期排序（最新的在前面）
    const sortedData = [...meterData.daily_data].sort((a, b) => new Date(b.date) - new Date(a.date));
    
    for (let i = 0; i < sortedData.length; i++) {
        const data = sortedData[i];
        const date = new Date(data.date);
        const formattedDate = date.toLocaleDateString('zh-CN');
        
        // 计算用电量
        let usage = 0;
        if (i < sortedData.length - 1) {
            usage = Math.max(0, data.balance - sortedData[i + 1].balance);
        }
        
        const row = document.createElement('tr');
        
        const dateCell = document.createElement('td');
        dateCell.textContent = formattedDate;
        
        const balanceCell = document.createElement('td');
        balanceCell.textContent = data.balance.toFixed(2);
        
        const usageCell = document.createElement('td');
        usageCell.textContent = i < sortedData.length - 1 ? usage.toFixed(2) : '-';
        
        row.appendChild(dateCell);
        row.appendChild(balanceCell);
        row.appendChild(usageCell);
        
        tableBody.appendChild(row);
    }
}

// 更新最后更新时间
function updateLastUpdated() {
    if (meterData && meterData.last_updated) {
        // 使用数据中的最后更新时间
        const lastUpdated = new Date(meterData.last_updated);
        const formattedDate = lastUpdated.toLocaleDateString('zh-CN');
        const formattedTime = lastUpdated.toLocaleTimeString('zh-CN');
        document.getElementById('last-updated').textContent = `${formattedDate} ${formattedTime}`;
    } else {
        // 如果没有最后更新时间，显示"未知"
        document.getElementById('last-updated').textContent = "未知";
    }
}