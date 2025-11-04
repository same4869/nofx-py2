// Open NOF1.ai - 监控界面JavaScript

// 配置
const API_BASE = '';
const UPDATE_INTERVAL = 5000; // 5秒更新一次

// 工具函数
function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined || isNaN(num)) return '--';
    return Number(num).toFixed(decimals);
}

function formatTimestamp(timestamp) {
    if (!timestamp) return '--';
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
    });
}

function setValueWithClass(elementId, value, decimals = 2) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const numValue = Number(value);
    element.textContent = formatNumber(numValue, decimals);
    
    // 添加颜色类
    element.classList.remove('positive', 'negative');
    if (numValue > 0) {
        element.classList.add('positive');
    } else if (numValue < 0) {
        element.classList.add('negative');
    }
}

// 更新账户信息
async function updateAccount() {
    try {
        const response = await fetch(`${API_BASE}/api/account`);
        const data = await response.json();
        
        document.getElementById('totalBalance').textContent = formatNumber(data.totalBalance, 2);
        document.getElementById('availableBalance').textContent = formatNumber(data.availableBalance, 2);
        setValueWithClass('unrealisedPnl', data.unrealisedPnl, 2);
        setValueWithClass('returnPercent', data.returnPercent, 2);
        
        document.getElementById('lastUpdate').textContent = formatTimestamp(new Date());
    } catch (error) {
        console.error('获取账户信息失败:', error);
    }
}

// 更新交易统计
async function updateStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const data = await response.json();
        
        document.getElementById('totalTrades').textContent = data.totalTrades || 0;
        document.getElementById('winRate').textContent = formatNumber(data.winRate, 1);
        setValueWithClass('totalPnl', data.totalPnl, 2);
        setValueWithClass('maxWin', data.maxWin, 2);
    } catch (error) {
        console.error('获取统计数据失败:', error);
    }
}

// 更新持仓
async function updatePositions() {
    try {
        const response = await fetch(`${API_BASE}/api/positions`);
        const data = await response.json();
        
        const container = document.getElementById('positionsContainer');
        
        if (!data.positions || data.positions.length === 0) {
            container.innerHTML = '<p class="empty-state">暂无持仓</p>';
            return;
        }
        
        const html = `
            <table>
                <thead>
                    <tr>
                        <th>币种</th>
                        <th>方向</th>
                        <th>数量</th>
                        <th>开仓价</th>
                        <th>当前价</th>
                        <th>未实现盈亏</th>
                        <th>杠杆</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.positions.map(pos => `
                        <tr>
                            <td><strong>${pos.symbol}</strong></td>
                            <td><span class="badge badge-${pos.side}">${pos.side === 'long' ? '做多' : '做空'}</span></td>
                            <td>${formatNumber(pos.quantity, 0)}</td>
                            <td>$${formatNumber(pos.entryPrice, 2)}</td>
                            <td>$${formatNumber(pos.currentPrice, 2)}</td>
                            <td class="${pos.unrealizedPnl >= 0 ? 'positive' : 'negative'}">
                                ${formatNumber(pos.unrealizedPnl, 2)} USDT
                            </td>
                            <td>${pos.leverage}x</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        container.innerHTML = html;
    } catch (error) {
        console.error('获取持仓信息失败:', error);
        document.getElementById('positionsContainer').innerHTML = 
            '<p class="empty-state">加载失败</p>';
    }
}

// 更新最近交易
async function updateTrades() {
    try {
        const response = await fetch(`${API_BASE}/api/trades?limit=10`);
        const data = await response.json();
        
        const container = document.getElementById('tradesContainer');
        
        if (!data.trades || data.trades.length === 0) {
            container.innerHTML = '<p class="empty-state">暂无交易记录</p>';
            return;
        }
        
        const html = `
            <table>
                <thead>
                    <tr>
                        <th>时间</th>
                        <th>币种</th>
                        <th>方向</th>
                        <th>类型</th>
                        <th>价格</th>
                        <th>数量</th>
                        <th>盈亏</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.trades.map(trade => `
                        <tr>
                            <td>${formatTimestamp(trade.timestamp)}</td>
                            <td><strong>${trade.symbol}</strong></td>
                            <td><span class="badge badge-${trade.side}">${trade.side === 'long' ? '做多' : '做空'}</span></td>
                            <td><span class="badge badge-${trade.type}">${trade.type === 'open' ? '开仓' : '平仓'}</span></td>
                            <td>$${formatNumber(trade.price, 2)}</td>
                            <td>${formatNumber(trade.quantity, 0)}</td>
                            <td class="${trade.pnl && trade.pnl >= 0 ? 'positive' : 'negative'}">
                                ${trade.pnl !== null ? formatNumber(trade.pnl, 2) + ' USDT' : '--'}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        container.innerHTML = html;
    } catch (error) {
        console.error('获取交易记录失败:', error);
        document.getElementById('tradesContainer').innerHTML = 
            '<p class="empty-state">加载失败</p>';
    }
}

// 更新实时价格
async function updatePrices() {
    try {
        const response = await fetch(`${API_BASE}/api/prices?symbols=BTC,ETH,SOL,BNB`);
        const data = await response.json();
        
        const container = document.getElementById('pricesContainer');
        
        if (!data.prices || Object.keys(data.prices).length === 0) {
            container.innerHTML = '<p class="empty-state">无法获取价格</p>';
            return;
        }
        
        const html = `
            <div class="price-grid">
                ${Object.entries(data.prices).map(([symbol, price]) => `
                    <div class="price-card">
                        <div class="price-symbol">${symbol}/USDT</div>
                        <div class="price-value">$${formatNumber(price, 2)}</div>
                    </div>
                `).join('')}
            </div>
        `;
        
        container.innerHTML = html;
    } catch (error) {
        console.error('获取价格失败:', error);
        document.getElementById('pricesContainer').innerHTML = 
            '<p class="empty-state">加载失败</p>';
    }
}

// 更新所有数据
async function updateAll() {
    await Promise.all([
        updateAccount(),
        updateStats(),
        updatePositions(),
        updateTrades(),
        updatePrices(),
    ]);
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 立即更新一次
    updateAll();
    
    // 定期更新
    setInterval(updateAll, UPDATE_INTERVAL);
});

