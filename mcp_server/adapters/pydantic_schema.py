from __future__ import annotations
from enum import IntEnum, StrEnum
from decimal import Decimal
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class TimeFrame(IntEnum):
    TIME_FRAME_UNSPECIFIED = 0
    TIME_FRAME_M1 = 1
    TIME_FRAME_M5 = 5
    TIME_FRAME_M15 = 9
    TIME_FRAME_M30 = 11
    TIME_FRAME_H1 = 12
    TIME_FRAME_H2 = 13
    TIME_FRAME_H4 = 15
    TIME_FRAME_H8 = 17
    TIME_FRAME_D = 19
    TIME_FRAME_W = 20
    TIME_FRAME_MN = 21
    TIME_FRAME_QR = 22

class Interval(BaseModel):
    start_time: datetime = Field(..., description="Начало интервала ISO8601")
    end_time: datetime = Field(..., description="Окончание интервала ISO8601")

class Bar(BaseModel):
    timestamp: datetime = Field(..., description="Метка времени свечи ISO8601")
    open: Decimal = Field(..., description="Цена открытия")
    high: Decimal = Field(..., description="Максимальная цена")
    low: Decimal = Field(..., description="Минимальная цена")
    close: Decimal = Field(..., description="Цена закрытия")
    volume: Decimal = Field(..., description="Объём торгов за свечу в шт.")

class Interval(BaseModel):
    start_time: str = Field(..., description="Начало интервала ISO8601 c Z или offset")
    end_time: str = Field(..., description="Окончание интервала ISO8601 c Z или offset")

class BarsRequest(BaseModel):
    symbol: str
    timeframe: TimeFrame
    start: Optional[str] = Field(None, description="Начало периода ISO8601 c Z")
    end: Optional[str] = Field(None, description="Окончание периода ISO8601 c Z")

class BarsResponse(BaseModel):
    symbol: str = Field(..., description="Символ инструмента")
    bars: List[Bar] = Field(..., description="Список агрегированных свечей")

class QuoteOption(BaseModel):
    open_interest: Optional[Decimal] = Field(None, description="Открытый интерес")
    implied_volatility: Optional[Decimal] = Field(None, description="Подразумеваемая волатильность")
    theoretical_price: Optional[Decimal] = Field(None, description="Теоретическая цена")
    delta: Optional[Decimal] = Field(None, description="Delta")
    gamma: Optional[Decimal] = Field(None, description="Gamma")
    theta: Optional[Decimal] = Field(None, description="Theta")
    vega: Optional[Decimal] = Field(None, description="Vega")
    rho: Optional[Decimal] = Field(None, description="Rho")

class Quote(BaseModel):
    symbol: str = Field(..., description="Символ инструмента")
    timestamp: datetime = Field(..., description="Метка времени котировки ISO8601")
    ask: Optional[Decimal] = Field(None, description="Аск. 0 при отсутствии активного аска")
    ask_size: Optional[Decimal] = Field(None, description="Размер аска")
    bid: Optional[Decimal] = Field(None, description="Бид. 0 при отсутствии активного бида")
    bid_size: Optional[Decimal] = Field(None, description="Размер бида")
    last: Optional[Decimal] = Field(None, description="Цена последней сделки")
    last_size: Optional[Decimal] = Field(None, description="Размер последней сделки")
    volume: Optional[Decimal] = Field(None, description="Дневной объём сделок")
    turnover: Optional[Decimal] = Field(None, description="Дневной оборот сделок")
    open: Optional[Decimal] = Field(None, description="Дневная цена открытия")
    high: Optional[Decimal] = Field(None, description="Дневной максимум")
    low: Optional[Decimal] = Field(None, description="Дневной минимум")
    close: Optional[Decimal] = Field(None, description="Дневная цена закрытия")
    change: Optional[Decimal] = Field(None, description="Изменение цены (last − close)")
    option: Optional[QuoteOption] = Field(None, description="Опционные греческие и параметры")

class QuoteRequest(BaseModel):
    symbol: str = Field(..., description="Символ инструмента в формате ticker@mic")

class OrderBookAction(IntEnum):
    ACTION_UNSPECIFIED = 0
    ACTION_REMOVE = 1
    ACTION_ADD = 2
    ACTION_UPDATE = 3

class OrderBookRow(BaseModel):
    price: Decimal = Field(..., description="Цена уровня")
    sell_size: Decimal = Field(..., description="Размер на продажу")
    buy_size: Decimal = Field(..., description="Размер на покупку")
    action: OrderBookAction = Field(..., description="Действие уровня стакана")
    mpid: Optional[str] = Field(None, description="Идентификатор участника рынка")
    timestamp: datetime = Field(..., description="Метка времени уровня ISO8601")

class QuoteResponse(BaseModel):
    symbol: str = Field(..., description="Символ инструмента")
    quote: Quote = Field(..., description="Котировка")

class TradeSide(StrEnum):
    BUY = "buy"
    SELL = "sell"

class LatestTradesRequest(BaseModel):
    symbol: str = Field(..., description="Символ инструмента в формате ticker@mic")

class LatestTradesResponse(BaseModel):
    symbol: str = Field(..., description="Символ инструмента")
    trades: List[Trade] = Field(..., description="Список последних сделок")

class OrderBook(BaseModel):
    rows: List[OrderBookRow] = Field(..., description="Уровни стакана")

class OrderBookRequest(BaseModel):
    symbol: str = Field(..., description="Символ инструмента в формате ticker@mic")

class OrderBookResponse(BaseModel):
    symbol: str = Field(..., description="Символ инструмента")
    orderbook: OrderBook = Field(..., description="Текущий стакан")

class GetQuoteArgs(BaseModel):
    symbol: str = Field(..., description="Символ в формате ticker@mic, например SBER@MISX")

# class Quote(BaseModel):
#     symbol: str = Field(..., description="Символ инструмента")
#     price: float = Field(..., description="Последняя цена сделки/котировка")
#     timestamp: str = Field(..., description="Время котировки ISO8601")

class GetOrderbookArgs(BaseModel):
    symbol: str = Field(..., description="ticker@mic")
    depth: int = Field(10, ge=1, le=50, description="Количество уровней по лучшим bid/ask")

class OrderbookLevel(BaseModel):
    price: float = Field(..., description="Цена уровня")
    quantity: float = Field(..., description="Объем на уровне, в штуках/лотах")

class Orderbook(BaseModel):
    bids: List[OrderbookLevel] = Field(..., description="Уровни спроса (bid), по убыванию цены")
    asks: List[OrderbookLevel] = Field(..., description="Уровни предложения (ask), по возрастанию цены")
    timestamp: str = Field(..., description="Метка времени ISO8601")

class GetCandlesArgs(BaseModel):
    symbol: str = Field(..., description="ticker@mic")
    timeframe: str = Field("D", description="Таймфрейм: 1m,5m,15m,1h,4h,D,W,M")
    start: Optional[str] = Field(None, description="Начало интервала, ISO8601 или epoch")
    end: Optional[str] = Field(None, description="Конец интервала, ISO8601 или epoch")

class Candle(BaseModel):
    t: str = Field(..., description="Время барра ISO8601")
    o: float = Field(..., description="Открытие")
    h: float = Field(..., description="Максимум")
    l: float = Field(..., description="Минимум")
    c: float = Field(..., description="Закрытие")
    v: float = Field(..., description="Объем")

class Candles(BaseModel):
    symbol: str = Field(..., description="Символ инструмента")
    timeframe: str = Field(..., description="Использованный таймфрейм")
    candles: List[Candle] = Field(..., description="Список OHLCV баров")

class GetAccountArgs(BaseModel):
    account_id: str = Field(..., description="Идентификатор счета")

class Money(BaseModel):
    currency: str = Field(..., description="Код валюты ISO 4217, например RUB")
    amount: float = Field(..., description="Сумма в валюте")

class Position(BaseModel):
    symbol: str = Field(..., description="ticker@mic позиции")
    quantity: float = Field(..., description="Количество (знак определяет long/short)")
    average_price: Optional[float] = Field(None, description="Средняя цена")
    current_price: Optional[float] = Field(None, description="Текущая цена")
    maintenance_margin: Optional[float] = Field(None, description="Поддерживающая маржа для FORTS")
    daily_pnl: Optional[float] = Field(None, description="PnL за текущий день")
    unrealized_pnl: Optional[float] = Field(None, description="Нереализованный PnL")

class Account(BaseModel):
    account_id: str = Field(..., description="ID счета")
    type: Optional[str] = Field(None, description="Тип счета")
    status: Optional[str] = Field(None, description="Статус счета")
    equity: Optional[float] = Field(None, description="Средства + стоимость позиций")
    unrealized_profit: Optional[float] = Field(None, description="Нереализованная прибыль")
    positions: List[Position] = Field(default_factory=list, description="Открытые и теоретические позиции")
    cash: List[Money] = Field(default_factory=list, description="Денежные средства по валютам")

class GetOrdersArgs(BaseModel):
    account_id: str = Field(..., description="ID счета")

class GetOrderArgs(BaseModel):
    account_id: str = Field(..., description="ID счета")
    order_id: str = Field(..., description="ID ордера")

class OrderLeg(BaseModel):
    symbol: str = Field(..., description="ticker@mic")
    quantity: float = Field(..., description="Количество")
    price: Optional[float] = Field(None, description="Лимитная цена, если применимо")
    side: str = Field(..., description="Направление: BUY или SELL")

class Order(BaseModel):
    order_id: str = Field(..., description="ID ордера")
    status: str = Field(..., description="Статус ордера")
    created_at: str = Field(..., description="Время создания ISO8601")
    legs: List[OrderLeg] = Field(default_factory=list, description="Ноги ордера")

class CreateOrderArgs(BaseModel):
    account_id: str = Field(..., description="ID счета")
    legs: List[OrderLeg] = Field(..., description="Состав ордера")
    tif: Optional[str] = Field(None, description="Time-in-force, например DAY/IOC/FOK")
    client_order_id: Optional[str] = Field(None, description="Клиентский ID")

class CancelOrderArgs(BaseModel):
    account_id: str = Field(..., description="ID счета")
    order_id: str = Field(..., description="ID ордера")

class TradesArgs(BaseModel):
    account_id: str = Field(..., description="ID счета")
    start: Optional[str] = Field(None, description="Начало периода, ISO8601 или epoch")
    end: Optional[str] = Field(None, description="Конец периода, ISO8601 или epoch")
    limit: Optional[int] = Field(None, ge=1, le=5000, description="Лимит записей")

class Trade(BaseModel):
    trade_id: str
    mpid: Optional[str] = None
    timestamp: datetime
    price: Decimal
    size: Decimal
    side: TradeSide

class TransactionsArgs(BaseModel):
    account_id: str = Field(..., description="ID счета")
    start: Optional[str] = Field(None, description="Начало периода, ISO8601 или epoch")
    end: Optional[str] = Field(None, description="Конец периода, ISO8601 или epoch")
    limit: Optional[int] = Field(None, ge=1, le=5000, description="Лимит записей")

class Transaction(BaseModel):
    id: str = Field(..., description="ID транзакции")
    category: str = Field(..., description="Категория из справочника API")
    timestamp: str = Field(..., description="Время ISO8601")
    symbol: Optional[str] = Field(None, description="ticker@mic, если есть")
    change: Optional[Money] = Field(None, description="Изменение денежных средств")
    transaction_name: Optional[str] = Field(None, description="Название транзакции")

class PositionsArgs(BaseModel):
    account_id: str = Field(..., description="ID счета")

class SessionCreateArgs(BaseModel):
    secret: Optional[str] = Field(None, description="API токен для получения JWT")
    readonly: Optional[bool] = Field(None, description="Пометить сессию readonly")

class SessionToken(BaseModel):
    token: str = Field(..., description="JWT-токен сессии")

class SessionDetails(BaseModel):
    created_at: str = Field(..., description="Время создания ISO8601")
    expires_at: str = Field(..., description="Время истечения ISO8601")
    account_ids: List[str] = Field(default_factory=list, description="Доступные ID счетов")
    readonly: bool = Field(..., description="Флаг только для чтения")

class Exchange(BaseModel):
    mic: str
    name: str

class Exchanges(BaseModel):
    exchanges: List[Exchange]


class SearchAssetsArgs(BaseModel):
    ticker: Optional[str] = Field(None, description="Фильтр по тикеру")
    isin: Optional[str] = Field(None, description="Фильтр по ISIN")
    mic: Optional[str] = Field(None, description="Фильтр по mic")
    type: Optional[str] = Field(None, description="Фильтр по типу инструмента")
    limit: Optional[int] = Field(None, ge=1, le=1000, description="Лимит записей")

class Asset(BaseModel):
    symbol: str = Field(..., description="ticker@mic")
    id: str = Field(..., description="ID инструмента")
    ticker: str = Field(..., description="Тикер")
    mic: str = Field(..., description="mic биржи")
    isin: Optional[str] = Field(None, description="ISIN")
    type: Optional[str] = Field(None, description="Тип инструмента")
    name: Optional[str] = Field(None, description="Наименование")

class Assets(BaseModel):
    assets: List[Asset] = Field(..., description="Список инструментов")

class GetAssetArgs(BaseModel):
    symbol: str = Field(..., description="ticker@mic")
    account_id: Optional[str] = Field(None, description="ID счета для специфики параметров, если нужен")

class AssetParamsArgs(BaseModel):
    symbol: str = Field(..., description="ticker@mic")
    account_id: str = Field(..., description="ID счета для параметров торговли")

class AssetParams(BaseModel):
    decimals: Optional[int] = Field(None, description="Число знаков после запятой")
    min_step: Optional[float] = Field(None, description="Минимальный шаг цены")
    lot_size: Optional[int] = Field(None, description="Размер лота")
    quote_currency: Optional[str] = Field(None, description="Валюта котировки")
    board: Optional[str] = Field(None, description="Режим торгов (board)")

class AssetScheduleArgs(BaseModel):
    symbol: str = Field(..., description="ticker@mic")

class TradingSession(BaseModel):
    date: str = Field(..., description="Дата торгового дня YYYY-MM-DD")
    open_time: Optional[str] = Field(None, description="Время открытия ISO8601")
    close_time: Optional[str] = Field(None, description="Время закрытия ISO8601")
    status: Optional[str] = Field(None, description="Статус сессии")

class AssetSchedule(BaseModel):
    symbol: str = Field(..., description="ticker@mic")
    sessions: List[TradingSession] = Field(..., description="Список торговых сессий")

class AssetOptionsArgs(BaseModel):
    symbol: str = Field(..., description="ticker@mic")

class OptionSeries(BaseModel):
    symbol: str = Field(..., description="Символ серии опциона")
    expiration_date: Optional[str] = Field(None, description="Дата экспирации YYYY-MM-DD")
    strike: Optional[float] = Field(None, description="Страйк")
    option_type: Optional[str] = Field(None, description="CALL или PUT")

class AssetOptions(BaseModel):
    symbol: str = Field(..., description="ticker@mic")
    series: List[OptionSeries] = Field(..., description="Опционные серии")

class InstrTradesLatestArgs(BaseModel):
    symbol: str = Field(..., description="ticker@mic")
    limit: Optional[int] = Field(None, ge=1, le=5000, description="Максимум последних принтов")

class PrintTrade(BaseModel):
    timestamp: str = Field(..., description="Время сделки ISO8601")
    price: float = Field(..., description="Цена")
    quantity: float = Field(..., description="Количество")
    side: Optional[str] = Field(None, description="BUY/SELL, если доступно")

class InstrTradesLatest(BaseModel):
    symbol: str = Field(..., description="ticker@mic")
    trades: List[PrintTrade] = Field(..., description="Последние сделки")

class ClockResponse(BaseModel):
    timestamp: str

class OrderSide(StrEnum):
    LONG = "long"
    SHORT = "short"

class OrderType(StrEnum):
    MARKET = "ORDER_TYPE_MARKET"
    LIMIT = "ORDER_TYPE_LIMIT"
    STOP = "ORDER_TYPE_STOP"
    STOP_LIMIT = "ORDER_TYPE_STOP_LIMIT"

class TimeInForce(StrEnum):
    DAY = "TIF_DAY"
    IOC = "TIF_IOC"
    FOK = "TIF_FOK"
    GTC = "TIF_GTC"

class StopCondition(StrEnum):
    GREATER_OR_EQUAL = "STOP_CONDITION_GREATER_OR_EQUAL"
    LESS_OR_EQUAL = "STOP_CONDITION_LESS_OR_EQUAL"

class Leg(BaseModel):
    symbol: str = Field(..., description="Символ инструмента в формате ticker@mic")
    quantity: str = Field(..., description="Количество в шт.")
    side: OrderSide = Field(..., description="Сторона заявки: long или short")
    type: OrderType = Field(..., description="Тип заявки")
    time_in_force: Optional[TimeInForce] = Field(None, description="Срок действия заявки")
    limit_price: Optional[str] = Field(None, description="Цена для лимитной/стоп-лимитной")
    stop_price: Optional[str] = Field(None, description="Цена триггера для стоп-заявок")
    stop_condition: Optional[StopCondition] = Field(None, description="Условие для стоп-заявок")
    comment: Optional[str] = Field(None, max_length=128, description="Метка заявки")

class ValidBefore(BaseModel):
    timestamp: str = Field(..., description="Срок действия условной заявки ISO8601")

class PlaceOrderArgs(BaseModel):
    account_id: str = Field(..., description="Идентификатор аккаунта")
    symbol: Optional[str] = Field(None, description="Символ инструмента для одноногой заявки")
    quantity: Optional[str] = Field(None, description="Количество в шт. для одноногой заявки")
    side: Optional[OrderSide] = Field(None, description="Сторона: long или short")
    type: Optional[OrderType] = Field(None, description="Тип заявки")
    time_in_force: Optional[TimeInForce] = Field(None, description="Срок действия заявки")
    limit_price: Optional[str] = Field(None, description="Цена для лимитной/стоп-лимитной")
    stop_price: Optional[str] = Field(None, description="Цена триггера для стоп-заявок")
    stop_condition: Optional[StopCondition] = Field(None, description="Условие для стоп-заявок")
    legs: Optional[List[Leg]] = Field(None, description="Ноги для мульти-лег заявки")
    client_order_id: Optional[str] = Field(None, max_length=20, description="Уникальный клиентский ID")
    valid_before: Optional[ValidBefore] = Field(None, description="Время истечения условной заявки")
    comment: Optional[str] = Field(None, max_length=128, description="Метка заявки")