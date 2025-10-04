"""
Клиент для работы с Finam TradeAPI
https://tradeapi.finam.ru/
"""

import os
from datetime import datetime
from decimal import Decimal
from typing import Any

import requests
from mcp.server.fastmcp import FastMCP
from .pydantic_schema import (
    GetAccountArgs, GetOrdersArgs, SessionCreateArgs, TransactionsArgs,
    SessionToken, AssetOptions, AssetOptionsArgs, AssetSchedule,
    AssetScheduleArgs, AssetParamsArgs, AssetParams, GetAssetArgs, Asset, SearchAssetsArgs, Assets, Exchanges,
    SessionDetails, Account, TradesArgs, CancelOrderArgs, CreateOrderArgs, Order, GetOrderArgs, Quote,
    PlaceOrderArgs, BarsResponse, BarsRequest, OrderBookRequest,
    OrderBookResponse, OrderBookRow, OrderBookAction, OrderBook, QuoteResponse, QuoteRequest, LatestTradesRequest,
    LatestTradesResponse, Trade, TimeFrame, QuoteOption, Bar, TradeSide

)

class FinamAPIClient:
    """
    Клиент для взаимодействия с Finam TradeAPI

    Документация: https://tradeapi.finam.ru/
    """

    def __init__(self, access_token: str | None = None, base_url: str | None = None) -> None:
        """
        Инициализация клиента

        Args:
            access_token: Токен доступа к API (из переменной окружения FINAM_ACCESS_TOKEN)
            base_url: Базовый URL API (по умолчанию из документации)
        """
        self.access_token = access_token or os.getenv("FINAM_ACCESS_TOKEN", "")
        self.base_url = base_url or os.getenv("FINAM_API_BASE_URL", "https://api.finam.ru")
        self.session = requests.Session()

        if self.access_token:
            self.session.headers.update({
                "Authorization": f"{self.access_token}",
                "Content-Type": "application/json",
            })

    def register_tools(self, mcp: FastMCP):
        @mcp.tool(
            name="get_quote",
            title="Котировка",
            description="получает последнюю котировку по инструменту (а именно: Символ инструмента, Цена последней сделки (то есть: Символ инструмента, Метка времени, Аск. 0 при отсутствии активного аска, Размер аска, Бид. 0 при отсутствии активного бида, Размер бида, Цена последней сделки, Размер последней сделки, Дневной объем и оборот сделок, Максимальная и минимальная дневная цена, Дневная цена закрытия, Изменение цены, Информация об опционе))",
            structured_output=False)
        def _get_quote(args: QuoteRequest) -> QuoteResponse:
            d = self.execute_request("GET", f"/v1/instruments/{args.symbol}/quotes/latest")
            q = d.get("quote", d)
            opt = q.get("option")
            return QuoteResponse(
                symbol=d.get("symbol", args.symbol),
                quote=Quote(
                    symbol=q.get("symbol", args.symbol),
                    timestamp=datetime.fromisoformat(q["timestamp"]),
                    ask=Decimal(q["ask"]) if q.get("ask") is not None else None,
                    ask_size=Decimal(q["ask_size"]) if q.get("ask_size") is not None else None,
                    bid=Decimal(q["bid"]) if q.get("bid") is not None else None,
                    bid_size=Decimal(q["bid_size"]) if q.get("bid_size") is not None else None,
                    last=Decimal(q["last"]) if q.get("last") is not None else None,
                    last_size=Decimal(q["last_size"]) if q.get("last_size") is not None else None,
                    volume=Decimal(q["volume"]) if q.get("volume") is not None else None,
                    turnover=Decimal(q["turnover"]) if q.get("turnover") is not None else None,
                    open=Decimal(q["open"]) if q.get("open") is not None else None,
                    high=Decimal(q["high"]) if q.get("high") is not None else None,
                    low=Decimal(q["low"]) if q.get("low") is not None else None,
                    close=Decimal(q["close"]) if q.get("close") is not None else None,
                    change=Decimal(q["change"]) if q.get("change") is not None else None,
                    option=QuoteOption(
                        **{k: (Decimal(v) if v is not None else None) for k, v in opt.items()}) if opt else None,
                ),
            )

        @mcp.tool(
            name="get_orderbook",
            title="Стакан",
            description="получает текущий стакан по инструменту (а именно: Символ инструмента, Стакан (то есть Уровни стакана))",
            structured_output=False)
        def _get_orderbook(args: OrderBookRequest) -> OrderBookResponse:
            d = self.execute_request("GET", f"/v1/instruments/{args.symbol}/orderbook")
            rows = []
            for r in d.get("orderbook", {}).get("rows", d.get("rows", [])):
                rows.append(OrderBookRow(
                    price=Decimal(r["price"]),
                    sell_size=Decimal(r["sell_size"]),
                    buy_size=Decimal(r["buy_size"]),
                    action=OrderBookAction(int(r["action"])) if not isinstance(r["action"], int) else OrderBookAction(
                        r["action"]),
                    mpid=r.get("mpid"),
                    timestamp=datetime.fromisoformat(r["timestamp"]),
                ))
            ob = OrderBook(rows=rows)
            return OrderBookResponse(symbol=d.get("symbol", args.symbol), orderbook=ob)

        @mcp.tool(
            name="get_candles",
            title="Свечи",
            description="получает исторические данные по инструменту (а именно: Символ инструмента, Агрегированная свеча (то есть: Метка времени, Цена открытия свечи, Максимальная цена свечи, Минимальная цена свечи, Цена закрытия свечи, Объём торгов за свечу в шт.))",
            structured_output=False,
        )
        def _get_candles(args: BarsRequest) -> BarsResponse:
            params = {"timeframe": args.timeframe.value}
            if args.start: params["interval.start_time"] = args.start.isoformat()
            if args.end: params["interval.end_time"] = args.end.isoformat()
            d = self.execute_request("GET", f"/v1/instruments/{args.symbol}/bars", params=params)
            bars = []
            for b in d.get("bars", []):
                bars.append(Bar(
                    timestamp=datetime.fromisoformat(b["timestamp"]),
                    open=Decimal(b["open"]),
                    high=Decimal(b["high"]),
                    low=Decimal(b["low"]),
                    close=Decimal(b["close"]),
                    volume=Decimal(b["volume"]),
                ))
            return BarsResponse(symbol=d.get("symbol", args.symbol), bars=bars)

        @mcp.tool(
            name="get_account",
            title="Счёт",
            description="получает информацию по конкретному аккаунту (а именно: Идентификатор аккаунта, Тип аккаунта, Статус аккаунта, Доступные средства плюс стоимость открытых позиций, Нереализованная прибыль, Позиции (для каждой отдельной позиции: Символ инструмента, Количество в шт, Средняя цена, Текущая цена, Поддерживающее гарантийное обеспечение, Прибыль или убыток за текущий день, Суммарная нереализованная прибыль или убыток (PnL) текущей позиции), Сумма собственных денежных средств на счете, доступная для торговли, Начальная маржа, Минимальная маржа, Тип портфеля для счетов на американских рынках, Тип портфеля для торговли на срочном рынке Московской Биржи)",
            structured_output=False,
        )
        def _get_account(args: GetAccountArgs) -> Account:
            d = self.get_account(args.account_id)
            return Account.model_validate(d)

        @mcp.tool(
            name="get_orders",
            title="Ордеры",
            description="получает список заявок для аккаунта (а именно: список заявок)",
        )
        def _get_orders(args: GetOrdersArgs) -> dict:
            d = self.get_orders(args.account_id)
            return d

        @mcp.tool(
            name="get_order",
            title="Ордер",
            description="получает информацию о конкретном ордере (а именно: Идентификатор заявки, Идентификатор исполнения, Статус заявки)",
            structured_output=False,
        )
        def _get_order(args: GetOrderArgs) -> Order:
            d = self.get_order(args.account_id, args.order_id)
            return Order.model_validate(d)

        @mcp.tool(
            name="create_order",
            title="Создать ордер",
            description="выставляет биржевую заявку",
            structured_output=False,
        )
        def _create_order(args: PlaceOrderArgs) -> dict:
            return self.place_order(args)

        @mcp.tool(
            name="cancel_order",
            title="Отменить ордер",
            description="отменяет биржевую заявку",
        )
        def _cancel_order(args: CancelOrderArgs) -> dict:
            d = self.cancel_order(args.account_id, args.order_id)
            return d

        @mcp.tool(
            name="get_trades",
            title="Сделки",
            description="получает историю по сделкам аккаунта (для каждой отдельной сделки: Идентификатор сделки, отправленный биржей; Идентификатор участника рынка; Метка времени; Цена сделки; Размер сделки; Сторона сделки (buy или sell))",
        )
        def _get_trades(args: TradesArgs) -> dict:
            d = self.get_trades(args.account_id, args.start, args.end)
            return d


        @mcp.tool(
            name="get_session_details",
            title="Сессия",
            description="получает информацию о токене сессии (а именно: Дата и время создания, Дата и время создания, Идентификаторы аккаунтов, Информация о доступе к рыночным данным (а именно: Уровень котировок, Задержка в минутах, Идентификатор биржи mic, Страна, Континент, Весь мир))",
            structured_output=False,
        )
        def _get_session_details() -> SessionDetails:
            d = self.get_session_details()
            return SessionDetails.model_validate(d)

        @mcp.tool(
            name="get_exchanges",
            title="Биржи",
            description="получает список доступных бирж, названия и mic коды (для каждой отдельной биржи: Идентификатор биржи mic, Наименование биржи)",
            structured_output=False,
        )
        def _get_exchanges() -> Exchanges:
            d = self.get_exchanges()
            return Exchanges.model_validate(d)

        @mcp.tool(
            name="search_assets",
            title="Поиск инструментов",
            description="получает список доступных инструментов, их описание (для каждого отдельного инструмента: Символ инструмента ticker@mic, Идентификатор инструмента, Тикер инструмента, mic идентификатор биржи, Isin идентификатор инструмента, Тип инструмента, Наименование инструмента)",
            structured_output=False,
        )
        def _search_assets(args: SearchAssetsArgs) -> Assets:
            params = {k: v for k, v in args.model_dump().items() if v is not None}
            d = self.search_assets(**params)
            return Assets.model_validate(d)

        @mcp.tool(
            name="get_asset",
            title="Инструмент",
            description="получает информацию по конкретному инструменту (а именно: Код режима торгов, Идентификатор инструмента, Тикер инструмента, mic идентификатор биржи,  Isin идентификатор инструмента, Тип инструмента, Наименование инструмента, Кол-во десятичных знаков в цене, Минимальный шаг цены, Кол-во штук в лоте, Дата экспирации фьючерса, Валюта котировки)",
            structured_output=False,
        )
        def _get_asset(args: GetAssetArgs) -> Asset:
            d = self.get_asset(args.symbol)
            return Asset.model_validate(d)

        @mcp.tool(
            name="get_asset_params",
            title="Параметры инструмента",
            description="получает торговые параметры по инструменту (а именно: Символ инструмента, ID аккаунта для которого подбираются торговые параметры, Доступны ли торговые операции, Доступны ли операции в Лонг и Шорт (статус и сколько дней действует запрет),  Ставка риска для операций в Лонг и Шорт, Сумма обеспечения для поддержания позиций Лонг и Шорт, сколько на счету должно быть свободных денежных средств для открытия Лонг и Шорт позиций)",
            structured_output=False,
        )
        def _get_asset_params(args: AssetParamsArgs) -> AssetParams:
            d = self.get_asset_params(args.symbol, args.account_id)
            return AssetParams.model_validate(d)

        @mcp.tool(
            name="get_asset_schedule",
            title="Календарь инструмента",
            description="получает расписание торгов для инструмента (а именно: Символ инструмента, Сессии инструмента (для каждой отдельной сессии: Тип сессии, Интервал сессии))",
            structured_output=False,
        )
        def _get_asset_schedule(args: AssetScheduleArgs) -> AssetSchedule:
            d = self.get_asset_schedule(args.symbol)
            return AssetSchedule.model_validate(d)

        @mcp.tool(
            name="get_asset_options",
            title="Опционы",
            description="получает цепочку опционов для базового актива (а именно: Символ базового актива опциона, Информация об опционе (для каждого отдельного инструмента: Символ инструмента, Тип инструмента, Лот, количество базового актива в инструменте, Дата старта торговли, Дата окончания торговли, Цена исполнения опциона, Множитель опциона, Дата начала экспирации, Дата окончания экспирации)) ",
            structured_output=False,
        )
        def _get_asset_options(args: AssetOptionsArgs) -> AssetOptions:
            d = self.get_asset_options(args.symbol)
            return AssetOptions.model_validate(d)

        @mcp.tool(
            name="get_instrument_trades_latest",
            title="Последние сделки",
            description="получает список последних сделок по инструменту (а именно: Символ инструмента, Список последних сделок (для каждой отдельной сделки:  Идентификатор сделки, Идентификатор участника рынка, Метка времени, Цена сделки, Размер сделки, Сторона сделки (buy или sell)))",
            structured_output=False,
        )
        def _get_instrument_trades_latest(args: LatestTradesRequest) -> LatestTradesResponse:
            d = self.get_instrument_trades_latest(args.symbol)
            trades = []
            for t in d.get("trades", []):
                trades.append(Trade(
                    trade_id=t["trade_id"],
                    mpid=t.get("mpid"),
                    timestamp=datetime.fromisoformat(t["timestamp"]),
                    price=Decimal(t["price"]),
                    size=Decimal(t["size"]),
                    side=TradeSide(t["side"]),
                ))
            return LatestTradesResponse(symbol=d.get("symbol", args.symbol), trades=trades)

        @mcp.tool(
            name="get_transactions",
            title="Транзакции",
            description="получает список транзакций аккаунта (для каждой отдельной транзакции: Идентификатор транзакции, Тип транзакции из TransactionCategory, Метка времени, Символ инструмента, Изменение в деньгах, Информация о сделке, Наименование транзакции)",
        )
        def _get_transactions(args: TransactionsArgs) -> dict:
            d = self.get_transactions(args.account_id, args.start, args.end)
            return d

        @mcp.tool(
            name="create_session",
            title="Создать сессию",
            description="получает JWT токен из API токена",
            structured_output=False,
        )
        def _create_session(args: SessionCreateArgs) -> SessionToken:
            payload = {}
            if args.secret is not None:
                payload["secret"] = args.secret
            if args.readonly is not None:
                payload["readonly"] = args.readonly
            d = self.create_session(payload)
            return SessionToken.model_validate(d)

    def execute_request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:  # noqa: ANN401
        """
        Выполнить HTTP запрос к Finam TradeAPI

        Args:
            method: HTTP метод (GET, POST, DELETE и т.д.)
            path: Путь API (например, /v1/instruments/SBER@MISX/quotes/latest)
            **kwargs: Дополнительные параметры для requests

        Returns:
            Ответ API в виде словаря

        Raises:
            requests.HTTPError: Если запрос завершился с ошибкой
        """
        url = f"{self.base_url}{path}"

        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()

            # Если ответ пустой (например, для DELETE)
            if not response.content:
                return {"status": "success", "message": "Operation completed"}

            return response.json()

        except requests.exceptions.HTTPError as e:
            # Пытаемся извлечь детали ошибки из ответа
            error_detail = {"error": str(e), "status_code": e.response.status_code if e.response else None}

            try:
                if e.response and e.response.content:
                    error_detail["details"] = e.response.json()
            except Exception:
                error_detail["details"] = e.response.text if e.response else None

            return error_detail

        except Exception as e:
            return {"error": str(e), "type": type(e).__name__}

    # Удобные методы для частых операций

    def get_quote(self, symbol: str) -> dict[str, Any]:
        """Получить текущую котировку инструмента"""
        return self.execute_request("GET", f"/v1/instruments/{symbol}/quotes/latest")

    def get_orderbook(self, symbol: str) -> dict[str, Any]:
        """Получить биржевой стакан"""
        return self.execute_request("GET", f"/v1/instruments/{symbol}/orderbook")

    def get_candles(self, symbol: str, timeframe: TimeFrame, start: datetime | None = None,
                    end: datetime | None = None) -> dict:
        params = {"timeframe": timeframe.value}
        if start: params["interval.start_time"] = start.isoformat()
        if end: params["interval.end_time"] = end.isoformat()
        return self.execute_request("GET", f"/v1/instruments/{symbol}/bars", params=params)

    def get_account(self, account_id: str) -> dict[str, Any]:
        """Получить информацию о счете"""
        return self.execute_request("GET", f"/v1/accounts/{account_id}")

    def get_orders(self, account_id: str) -> dict[str, Any]:
        """Получить список ордеров"""
        return self.execute_request("GET", f"/v1/accounts/{account_id}/orders")

    def get_order(self, account_id: str, order_id: str) -> dict[str, Any]:
        """Получить информацию об ордере"""
        return self.execute_request("GET", f"/v1/accounts/{account_id}/orders/{order_id}")

    # def create_order(self, account_id: str, order_data: dict[str, Any]) -> dict[str, Any]:
    #     """Создать новый ордер"""
    #     return self.execute_request("POST", f"/v1/accounts/{account_id}/orders", json=order_data)

    def cancel_order(self, account_id: str, order_id: str) -> dict[str, Any]:
        """Отменить ордер"""
        return self.execute_request("DELETE", f"/v1/accounts/{account_id}/orders/{order_id}")

    def get_trades(self, account_id: str, start: str | None = None, end: str | None = None) -> dict[str, Any]:
        """Получить историю сделок"""
        params = {}
        if start:
            params["interval.start_time"] = start
        if end:
            params["interval.end_time"] = end
        return self.execute_request("GET", f"/v1/accounts/{account_id}/trades", params=params)

    def get_session_details(self) -> dict[str, Any]:
        """Получить детали текущей сессии"""
        return self.execute_request("POST", "/v1/sessions/details")

    def get_exchanges(self) -> dict[str, Any]:
        """Список бирж."""
        return self.execute_request("GET", "/v1/exchanges")

    def search_assets(self, **params: Any) -> dict[str, Any]:
        """Поиск инструментов."""
        return self.execute_request("GET", "/v1/assets", params=params or None)

    def get_asset(self, symbol: str) -> dict[str, Any]:
        """Информация об инструменте."""
        return self.execute_request("GET", f"/v1/assets/{symbol}")

    def get_asset_params(self, symbol: str, account_id: str) -> dict[str, Any]:
        """Параметры инструмента для указанного счёта."""
        return self.execute_request("GET", f"/v1/assets/{symbol}/params", params={"account_id": account_id})

    def get_asset_schedule(self, symbol: str) -> dict[str, Any]:
        """Расписание торгов по инструменту."""
        return self.execute_request("GET", f"/v1/assets/{symbol}/schedule")

    def get_asset_options(self, symbol: str) -> dict[str, Any]:
        """Опционы на базовый актив."""
        return self.execute_request("GET", f"/v1/assets/{symbol}/options")

    def get_instrument_trades_latest(self, symbol: str) -> dict[str, Any]:
        """Лента последних сделок по инструменту."""
        return self.execute_request("GET", f"/v1/instruments/{symbol}/trades/latest")

    def get_transactions(self, account_id: str, start: str | None = None, end: str | None = None) -> dict[str, Any]:
        """Транзакции по счёту."""
        params: dict[str, Any] = {}
        if start:
            params["interval.start_time"] = start
        if end:
            params["interval.end_time"] = end
        return self.execute_request("GET", f"/v1/accounts/{account_id}/transactions", params=params or None)

    def create_session(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Создать торговую сессию."""
        return self.execute_request("POST", "/v1/sessions", json=payload or {})

    def get_clock(self) -> dict[str, Any]:
        """Текущее время на сервере"""
        return self.execute_request("GET", "/v1/assets/clock")

    def place_order(self, args: PlaceOrderArgs) -> dict[str, Any]:
        """Размещение ордера на платформе"""
        payload: dict[str, Any] = {}
        if args.symbol is not None: payload["symbol"] = args.symbol
        if args.quantity is not None: payload["quantity"] = args.quantity
        if args.side is not None: payload["side"] = args.side.value
        if args.type is not None: payload["type"] = args.type.value
        if args.time_in_force is not None: payload["time_in_force"] = args.time_in_force.value
        if args.limit_price is not None: payload["limit_price"] = args.limit_price
        if args.stop_price is not None: payload["stop_price"] = args.stop_price
        if args.stop_condition is not None: payload["stop_condition"] = args.stop_condition.value
        if args.legs is not None:
            payload["legs"] = [
                {
                    "symbol": l.symbol,
                    "quantity": l.quantity,
                    "side": l.side.value,
                    "type": l.type.value,
                    **({"time_in_force": l.time_in_force.value} if l.time_in_force is not None else {}),
                    **({"limit_price": l.limit_price} if l.limit_price is not None else {}),
                    **({"stop_price": l.stop_price} if l.stop_price is not None else {}),
                    **({"stop_condition": l.stop_condition.value} if l.stop_condition is not None else {}),
                    **({"comment": l.comment} if l.comment is not None else {}),
                }
                for l in args.legs
            ]
        if args.client_order_id is not None: payload["client_order_id"] = args.client_order_id
        if args.valid_before is not None: payload["valid_before"] = args.valid_before.model_dump()
        if args.comment is not None: payload["comment"] = args.comment
        return self.execute_request("POST", f"/v1/accounts/{args.account_id}/orders", json=payload)