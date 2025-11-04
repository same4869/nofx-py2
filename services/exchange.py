"""
交易所API客户端

使用ccxt库封装Gate.io API
支持测试网和正式网切换
提供完整的期货交易接口

参考TypeScript版本：src/services/gateClient.ts
"""

import asyncio
from typing import List, Dict, Optional, Any, Tuple
from decimal import Decimal
import ccxt.async_support as ccxt
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from config.settings import settings
from config.risk_params import RISK_PARAMS
from core.logger import logger


class ExchangeClient:
    """
    Gate.io交易所API客户端
    
    特性：
    - 使用ccxt统一接口
    - 自动重试机制
    - 测试网/正式网切换
    - 异步操作
    - 完整的期货交易支持
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: Optional[bool] = None
    ):
        """
        初始化交易所客户端
        
        Args:
            api_key: API密钥（如果为None，从配置读取）
            api_secret: API密钥（如果为None，从配置读取）
            testnet: 是否使用测试网（如果为None，从配置读取）
        """
        self.api_key = api_key or settings.GATE_API_KEY
        self.api_secret = api_secret or settings.GATE_API_SECRET
        self.testnet = testnet if testnet is not None else settings.GATE_USE_TESTNET
        
        # 创建ccxt交易所实例
        self.exchange = ccxt.gateio({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,  # 启用速率限制
            'options': {
                'defaultType': 'swap',  # 默认使用永续合约
                'defaultSettle': 'usdt',  # USDT结算
            },
        })
        
        # 设置测试网
        if self.testnet:
            self.exchange.set_sandbox_mode(True)
            logger.info("🧪 使用Gate.io测试网")
        else:
            logger.info("📈 使用Gate.io正式网")
        
        # 结算货币
        self.settle = 'USDT'
        
        logger.info(f"✅ Gate.io API客户端初始化完成")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()
    
    async def close(self):
        """关闭交易所连接"""
        if self.exchange:
            await self.exchange.close()
            logger.debug("交易所连接已关闭")
    
    def _symbol_to_ccxt(self, symbol: str) -> str:
        """
        转换币种符号为ccxt格式
        
        Args:
            symbol: 币种符号，例如 'BTC' 或 'BTC_USDT'
            
        Returns:
            ccxt格式的交易对，例如 'BTC/USDT:USDT'
        """
        # 如果已经是完整的ccxt格式，直接返回
        if ':' in symbol:
            return symbol
        
        # 处理不同格式的输入
        if '/' in symbol:
            # 已经包含'/'，只需添加settle后缀
            pass
        elif '_' in symbol:
            # 下划线格式，转换为斜杠
            symbol = symbol.replace('_', '/')
        else:
            # 只有币种名称，添加/USDT
            symbol = f"{symbol}/USDT"
        
        # 永续合约格式：BTC/USDT:USDT
        return f"{symbol}:{self.settle}"
    
    def _symbol_from_ccxt(self, ccxt_symbol: str) -> str:
        """
        从ccxt格式转换为标准币种符号
        
        Args:
            ccxt_symbol: ccxt格式，例如 'BTC/USDT:USDT'
            
        Returns:
            标准格式，例如 'BTC'
        """
        # BTC/USDT:USDT -> BTC
        if ':' in ccxt_symbol:
            ccxt_symbol = ccxt_symbol.split(':')[0]
        if '/' in ccxt_symbol:
            return ccxt_symbol.split('/')[0]
        return ccxt_symbol
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ccxt.NetworkError, ccxt.ExchangeNotAvailable)),
        reraise=True
    )
    async def get_futures_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        获取合约ticker价格（带重试机制）
        
        Args:
            symbol: 币种符号，例如 'BTC' 或 'BTC_USDT'
            
        Returns:
            ticker数据字典
            
        对应TypeScript: gateClient.getFuturesTicker()
        """
        try:
            ccxt_symbol = self._symbol_to_ccxt(symbol)
            ticker = await self.exchange.fetch_ticker(ccxt_symbol)
            
            logger.debug(f"获取 {symbol} ticker成功: 价格={ticker.get('last', 0)}")
            
            # 转换为与TypeScript版本兼容的格式
            return {
                'contract': symbol if '_' in symbol else f"{symbol}_USDT",
                'last': str(ticker.get('last', 0)),
                'markPrice': str(ticker.get('info', {}).get('mark_price', ticker.get('last', 0))),
                'change_percentage': str(ticker.get('percentage', 0)),
                'volume_24h': str(ticker.get('baseVolume', 0)),
                'high_24h': str(ticker.get('high', 0)),
                'low_24h': str(ticker.get('low', 0)),
                'funding_rate': ticker.get('info', {}).get('funding_rate', '0'),
            }
        except Exception as e:
            logger.error(f"获取 {symbol} ticker失败: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ccxt.NetworkError, ccxt.ExchangeNotAvailable)),
        reraise=True
    )
    async def get_futures_candles(
        self,
        symbol: str,
        timeframe: str = '5m',
        limit: int = 100
    ) -> List[List]:
        """
        获取合约K线数据（带重试机制）
        
        Args:
            symbol: 币种符号
            timeframe: 时间周期，例如 '1m', '5m', '1h', '4h'
            limit: 返回数量
            
        Returns:
            K线数据列表，每个元素为 [timestamp, open, high, low, close, volume]
            
        对应TypeScript: gateClient.getFuturesCandles()
        """
        try:
            ccxt_symbol = self._symbol_to_ccxt(symbol)
            
            # ccxt使用标准时间周期格式
            ohlcv = await self.exchange.fetch_ohlcv(
                ccxt_symbol,
                timeframe=timeframe,
                limit=limit
            )
            
            logger.debug(f"获取 {symbol} K线成功: {len(ohlcv)}条数据")
            
            # 转换为与TypeScript版本兼容的格式
            # ccxt返回: [timestamp, open, high, low, close, volume]
            # 转换为对象格式以匹配TypeScript的FuturesCandlestick
            candles = []
            for candle in ohlcv:
                candles.append({
                    't': int(candle[0] / 1000),  # 毫秒转秒
                    'o': str(candle[1]),  # open
                    'h': str(candle[2]),  # high
                    'l': str(candle[3]),  # low
                    'c': str(candle[4]),  # close
                    'v': str(candle[5]),  # volume
                })
            
            return candles
            
        except Exception as e:
            logger.error(f"获取 {symbol} K线失败: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ccxt.NetworkError, ccxt.ExchangeNotAvailable)),
        reraise=True
    )
    async def get_account(self) -> Dict[str, Any]:
        """
        获取账户余额（带重试机制）
        
        Returns:
            账户信息字典
            
        对应TypeScript: gateClient.getFuturesAccount()
        """
        try:
            balance = await self.exchange.fetch_balance({'type': 'swap'})
            
            # 获取USDT余额信息
            usdt_info = balance.get('USDT', {})
            total = float(usdt_info.get('total', 0))
            free = float(usdt_info.get('free', 0))
            used = float(usdt_info.get('used', 0))
            
            # 获取未实现盈亏（从info中）
            unrealised_pnl = float(balance.get('info', {}).get('unrealisedPnl', 0))
            
            logger.debug(f"获取账户信息成功: 总资产={total} USDT")
            
            # 转换为与TypeScript版本兼容的格式
            return {
                'total': str(total),
                'available': str(free),
                'unrealisedPnl': str(unrealised_pnl),
                'currency': 'USDT',
            }
            
        except Exception as e:
            logger.error(f"获取账户信息失败: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ccxt.NetworkError, ccxt.ExchangeNotAvailable)),
        reraise=True
    )
    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        获取当前持仓（带重试机制）
        
        Returns:
            持仓列表，只返回允许的币种
            
        对应TypeScript: gateClient.getPositions()
        """
        try:
            # 获取所有持仓
            positions = await self.exchange.fetch_positions()
            
            # 过滤：只保留允许的币种
            allowed_symbols = RISK_PARAMS.TRADING_SYMBOLS
            filtered_positions = []
            
            for pos in positions:
                # 跳过空持仓
                contracts = float(pos.get('contracts', 0))
                if contracts == 0:
                    continue
                
                # 提取币种名称
                symbol = self._symbol_from_ccxt(pos['symbol'])
                
                # 只保留允许的币种
                if symbol not in allowed_symbols:
                    continue
                
                # 转换为与TypeScript版本兼容的格式
                filtered_positions.append({
                    'contract': f"{symbol}_USDT",
                    'size': str(int(contracts * (1 if pos['side'] == 'long' else -1))),
                    'leverage': str(pos.get('leverage', 1)),
                    'entryPrice': str(pos.get('entryPrice', 0)),
                    'markPrice': str(pos.get('markPrice', 0)),
                    'liqPrice': str(pos.get('liquidationPrice', 0)),
                    'unrealisedPnl': str(pos.get('unrealizedPnl', 0)),
                    'margin': str(pos.get('initialMargin', 0)),
                })
            
            logger.debug(f"获取持仓成功: {len(filtered_positions)}个活跃持仓")
            
            return filtered_positions
            
        except Exception as e:
            logger.error(f"获取持仓失败: {e}")
            raise
    
    async def place_order(
        self,
        symbol: str,
        side: str,
        size: float,
        price: Optional[float] = None,
        reduce_only: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        下单 - 开仓或平仓
        
        Args:
            symbol: 币种符号
            side: 'buy' 或 'sell'
            size: 数量（正数）
            price: 价格（None表示市价单）
            reduce_only: 是否只减仓
            **kwargs: 其他参数（止损、止盈等）
            
        Returns:
            订单信息
            
        对应TypeScript: gateClient.placeOrder()
        """
        try:
            ccxt_symbol = self._symbol_to_ccxt(symbol)
            
            # 确定订单类型
            order_type = 'market' if price is None else 'limit'
            
            # 构建订单参数
            params = {}
            
            if reduce_only:
                params['reduceOnly'] = True
            
            # 下单
            order = await self.exchange.create_order(
                symbol=ccxt_symbol,
                type=order_type,
                side=side,
                amount=size,
                price=price,
                params=params
            )
            
            logger.info(
                f"下单成功: {symbol} {side} {size}张 "
                f"{'市价' if order_type == 'market' else f'限价{price}'}"
            )
            
            # 转换为与TypeScript版本兼容的格式
            return {
                'id': str(order['id']),
                'contract': f"{symbol}_USDT" if '_' not in symbol else symbol,
                'size': str(size if side == 'buy' else -size),
                'price': str(order.get('price', price or 0)),
                'fill_price': str(order.get('average', 0)),
                'status': order['status'],
                'create_time': order.get('timestamp', 0),
            }
            
        except ccxt.InsufficientFunds as e:
            logger.error(f"资金不足: {e}")
            raise ValueError(f"资金不足，无法开仓 {symbol}")
        except Exception as e:
            logger.error(f"下单失败: {e}")
            raise
    
    async def set_leverage(self, symbol: str, leverage: int) -> Optional[Dict]:
        """
        设置仓位杠杆
        
        Args:
            symbol: 币种符号
            leverage: 杠杆倍数
            
        Returns:
            设置结果（如果失败返回None）
            
        对应TypeScript: gateClient.setLeverage()
        """
        try:
            ccxt_symbol = self._symbol_to_ccxt(symbol)
            
            logger.info(f"设置 {symbol} 杠杆为 {leverage}x")
            
            result = await self.exchange.set_leverage(
                leverage,
                ccxt_symbol
            )
            
            logger.info(f"✅ {symbol} 杠杆设置成功: {leverage}x")
            return result
            
        except Exception as e:
            # 如果已有持仓，某些交易所不允许修改杠杆
            logger.warning(f"设置 {symbol} 杠杆失败（可能已有持仓）: {e}")
            return None
    
    async def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        取消订单
        
        Args:
            order_id: 订单ID
            symbol: 币种符号
            
        Returns:
            取消结果
            
        对应TypeScript: gateClient.cancelOrder()
        """
        try:
            ccxt_symbol = self._symbol_to_ccxt(symbol)
            
            result = await self.exchange.cancel_order(
                order_id,
                ccxt_symbol
            )
            
            logger.info(f"取消订单成功: {order_id}")
            return result
            
        except Exception as e:
            logger.error(f"取消订单 {order_id} 失败: {e}")
            raise
    
    async def get_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        获取订单详情
        
        Args:
            order_id: 订单ID
            symbol: 币种符号
            
        Returns:
            订单详情
            
        对应TypeScript: gateClient.getOrder()
        """
        try:
            ccxt_symbol = self._symbol_to_ccxt(symbol)
            
            order = await self.exchange.fetch_order(
                order_id,
                ccxt_symbol
            )
            
            # 转换为与TypeScript版本兼容的格式
            return {
                'id': str(order['id']),
                'status': order['status'],
                'price': str(order.get('price', 0)),
                'fill_price': str(order.get('average', 0)),
                'size': str(order.get('amount', 0)),
                'filled': str(order.get('filled', 0)),
            }
            
        except Exception as e:
            logger.error(f"获取订单 {order_id} 详情失败: {e}")
            raise
    
    async def get_funding_rate(self, symbol: str) -> Dict[str, Any]:
        """
        获取资金费率
        
        Args:
            symbol: 币种符号
            
        Returns:
            资金费率信息
            
        对应TypeScript: gateClient.getFundingRate()
        """
        try:
            ccxt_symbol = self._symbol_to_ccxt(symbol)
            
            # 获取资金费率历史（最新1条）
            funding_history = await self.exchange.fetch_funding_rate_history(
                ccxt_symbol,
                limit=1
            )
            
            if funding_history:
                latest = funding_history[0]
                return {
                    't': latest.get('timestamp', 0),
                    'r': str(latest.get('fundingRate', 0)),
                }
            else:
                return {'t': 0, 'r': '0'}
                
        except Exception as e:
            logger.error(f"获取 {symbol} 资金费率失败: {e}")
            raise
    
    async def get_contract_info(self, symbol: str) -> Dict[str, Any]:
        """
        获取合约信息
        
        Args:
            symbol: 币种符号
            
        Returns:
            合约信息
            
        对应TypeScript: gateClient.getContractInfo()
        """
        try:
            # 加载市场信息
            if not self.exchange.markets:
                await self.exchange.load_markets()
            
            ccxt_symbol = self._symbol_to_ccxt(symbol)
            market = self.exchange.market(ccxt_symbol)
            
            return {
                'symbol': market['symbol'],
                'contractSize': market.get('contractSize', 1),
                'minAmount': market['limits']['amount']['min'],
                'maxAmount': market['limits']['amount']['max'],
                'pricePrecision': market['precision']['price'],
                'amountPrecision': market['precision']['amount'],
                # 使用驼峰命名以匹配TypeScript版本
                'orderSizeMin': market['limits']['amount']['min'],
                'orderSizeMax': market['limits']['amount']['max'],
            }
            
        except Exception as e:
            logger.error(f"获取 {symbol} 合约信息失败: {e}")
            raise


# 全局客户端实例（单例模式）
_exchange_client: Optional[ExchangeClient] = None


def create_exchange_client() -> ExchangeClient:
    """
    创建全局交易所客户端实例（单例模式）
    
    对应TypeScript: createGateClient()
    """
    global _exchange_client
    
    if _exchange_client is None:
        if not settings.GATE_API_KEY or not settings.GATE_API_SECRET:
            raise ValueError("GATE_API_KEY 和 GATE_API_SECRET 必须在环境变量中设置")
        
        _exchange_client = ExchangeClient()
    
    return _exchange_client


async def close_exchange_client():
    """关闭全局交易所客户端"""
    global _exchange_client
    
    if _exchange_client:
        await _exchange_client.close()
        _exchange_client = None


if __name__ == "__main__":
    # 测试交易所API
    async def test():
        print("\n" + "=" * 80)
        print("🧪 测试交易所API")
        print("=" * 80 + "\n")
        
        # 创建客户端
        client = create_exchange_client()
        
        try:
            # 测试1：获取BTC价格
            print("📍 测试1：获取BTC价格")
            ticker = await client.get_futures_ticker('BTC')
            print(f"   BTC价格: {ticker['last']}")
            print(f"   ✅ 测试通过\n")
            
            # 测试2：获取K线数据
            print("📍 测试2：获取BTC K线数据")
            candles = await client.get_futures_candles('BTC', '5m', 5)
            print(f"   获取到 {len(candles)} 条K线")
            print(f"   最新收盘价: {candles[-1]['c']}")
            print(f"   ✅ 测试通过\n")
            
            # 测试3：获取账户信息
            print("📍 测试3：获取账户信息")
            account = await client.get_account()
            print(f"   总资产: {account['total']} USDT")
            print(f"   可用余额: {account['available']} USDT")
            print(f"   ✅ 测试通过\n")
            
            # 测试4：获取持仓
            print("📍 测试4：获取持仓")
            positions = await client.get_positions()
            print(f"   当前持仓数: {len(positions)}")
            print(f"   ✅ 测试通过\n")
            
            # 测试5：获取资金费率
            print("📍 测试5：获取资金费率")
            funding = await client.get_funding_rate('BTC')
            print(f"   BTC资金费率: {funding['r']}")
            print(f"   ✅ 测试通过\n")
            
            print("=" * 80)
            print("🎉 所有测试通过！")
            print("=" * 80 + "\n")
            
        finally:
            await client.close()
    
    asyncio.run(test())

