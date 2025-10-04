"""
Клиент для работы с Finam TradeAPI
https://tradeapi.finam.ru/
"""

import os
from typing import Any

import requests
from mcp.server.fastmcp import FastMCP
from .pydantic_schema import (
    GetQuoteArgs, GetOrderbookArgs, GetCandlesArgs, GetAccountArgs, GetOrdersArgs, SessionCreateArgs, TransactionsArgs,
    SessionToken, InstrTradesLatestArgs, InstrTradesLatest, AssetOptions, AssetOptionsArgs, AssetSchedule,
    AssetScheduleArgs, AssetParamsArgs, AssetParams, GetAssetArgs, Asset, SearchAssetsArgs, Assets, Exchanges,
    SessionDetails, Account, PositionsArgs, TradesArgs, CancelOrderArgs, CreateOrderArgs, Order, GetOrderArgs, Candles,
    Candle, Orderbook, OrderbookLevel, Quote

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
            description="GET /v1/instruments/{symbol}/quotes/latest",
            structured_output=False,
        )
        def _get_quote(args: GetQuoteArgs) -> Quote:
            d = self.get_quote(args.symbol)
            return Quote(
                symbol=args.symbol,
                price=float(d["price"]),
                timestamp=str(d["timestamp"]),
            )

        @mcp.tool(
            name="get_orderbook",
            title="Стакан",
            description="GET /v1/instruments/{symbol}/orderbook",
            structured_output=False,
        )
        def _get_orderbook(args: GetOrderbookArgs) -> Orderbook:
            d = self.get_orderbook(args.symbol, args.depth)
            bids_src = d.get("bids") or []
            asks_src = d.get("asks") or []
            bids = [OrderbookLevel(price=float(x["price"]), quantity=float(x.get("qty", x.get("quantity", 0)))) for x in
                    bids_src]
            asks = [OrderbookLevel(price=float(x["price"]), quantity=float(x.get("qty", x.get("quantity", 0)))) for x in
                    asks_src]
            ts = str(d.get("timestamp") or d.get("ts") or d.get("time") or "")
            return Orderbook(bids=bids, asks=asks, timestamp=ts)

        @mcp.tool(
            name="get_candles",
            title="Свечи",
            description="GET /v1/instruments/{symbol}/bars",
            structured_output=False,
        )
        def _get_candles(args: GetCandlesArgs) -> Candles:
            d = self.get_candles(args.symbol, args.timeframe, args.start, args.end)
            bars = d.get("bars") or d.get("candles") or []
            candles = []
            for b in bars:
                t = str(b.get("t") or b.get("time") or b.get("timestamp"))
                o = float(b.get("o") if b.get("o") is not None else b.get("open"))
                h = float(b.get("h") if b.get("h") is not None else b.get("high"))
                l = float(b.get("l") if b.get("l") is not None else b.get("low"))
                c = float(b.get("c") if b.get("c") is not None else b.get("close"))
                v = float(b.get("v") if b.get("v") is not None else b.get("volume", 0))
                candles.append(Candle(t=t, o=o, h=h, l=l, c=c, v=v))
            return Candles(symbol=args.symbol, timeframe=args.timeframe, candles=candles)

        @mcp.tool(
            name="get_account",
            title="Счёт",
            description="GET /v1/accounts/{account_id}",
            structured_output=False,
        )
        def _get_account(args: GetAccountArgs) -> Account:
            d = self.get_account(args.account_id)
            return Account.model_validate(d)

        @mcp.tool(
            name="get_orders",
            title="Ордеры",
            description="GET /v1/accounts/{account_id}/orders",
        )
        def _get_orders(args: GetOrdersArgs) -> dict:
            d = self.get_orders(args.account_id)
            return d

        @mcp.tool(
            name="get_order",
            title="Ордер",
            description="GET /v1/accounts/{account_id}/orders/{order_id}",
            structured_output=False,
        )
        def _get_order(args: GetOrderArgs) -> Order:
            d = self.get_order(args.account_id, args.order_id)
            return Order.model_validate(d)

        @mcp.tool(
            name="create_order",
            title="Создать ордер",
            description="POST /v1/accounts/{account_id}/orders",
            structured_output=False,
        )
        def _create_order(args: CreateOrderArgs) -> Order:
            payload = {
                "legs": [leg.model_dump() for leg in args.legs],
            }
            if args.tif is not None:
                payload["tif"] = args.tif
            if args.client_order_id is not None:
                payload["client_order_id"] = args.client_order_id
            d = self.create_order(args.account_id, payload)
            return Order.model_validate(d)

        @mcp.tool(
            name="cancel_order",
            title="Отменить ордер",
            description="DELETE /v1/accounts/{account_id}/orders/{order_id}",
        )
        def _cancel_order(args: CancelOrderArgs) -> dict:
            d = self.cancel_order(args.account_id, args.order_id)
            return d

        @mcp.tool(
            name="get_trades",
            title="Сделки",
            description="GET /v1/accounts/{account_id}/trades",
        )
        def _get_trades(args: TradesArgs) -> dict:
            d = self.get_trades(args.account_id, args.start, args.end)
            return d

        @mcp.tool(
            name="get_positions",
            title="Позиции",
            description="GET /v1/accounts/{account_id}",
            structured_output=False,
        )
        def _get_positions(args: PositionsArgs) -> Account:
            d = self.get_positions(args.account_id)
            return Account.model_validate(d)

        @mcp.tool(
            name="get_session_details",
            title="Сессия",
            description="POST /v1/sessions/details",
            structured_output=False,
        )
        def _get_session_details() -> SessionDetails:
            d = self.get_session_details()
            return SessionDetails.model_validate(d)

        @mcp.tool(
            name="get_exchanges",
            title="Биржи",
            description="GET /v1/exchanges",
            structured_output=False,
        )
        def _get_exchanges() -> Exchanges:
            d = self.get_exchanges()
            return Exchanges.model_validate(d)

        @mcp.tool(
            name="search_assets",
            title="Поиск инструментов",
            description="GET /v1/assets",
            structured_output=False,
        )
        def _search_assets(args: SearchAssetsArgs) -> Assets:
            params = {k: v for k, v in args.model_dump().items() if v is not None}
            d = self.search_assets(**params)
            return Assets.model_validate(d)

        @mcp.tool(
            name="get_asset",
            title="Инструмент",
            description="GET /v1/assets/{symbol}",
            structured_output=False,
        )
        def _get_asset(args: GetAssetArgs) -> Asset:
            d = self.get_asset(args.symbol)
            return Asset.model_validate(d)

        @mcp.tool(
            name="get_asset_params",
            title="Параметры инструмента",
            description="GET /v1/assets/{symbol}/params",
            structured_output=False,
        )
        def _get_asset_params(args: AssetParamsArgs) -> AssetParams:
            d = self.get_asset_params(args.symbol, args.account_id)
            return AssetParams.model_validate(d)

        @mcp.tool(
            name="get_asset_schedule",
            title="Календарь инструмента",
            description="GET /v1/assets/{symbol}/schedule",
            structured_output=False,
        )
        def _get_asset_schedule(args: AssetScheduleArgs) -> AssetSchedule:
            d = self.get_asset_schedule(args.symbol)
            return AssetSchedule.model_validate(d)

        @mcp.tool(
            name="get_asset_options",
            title="Опционы",
            description="GET /v1/assets/{symbol}/options",
            structured_output=False,
        )
        def _get_asset_options(args: AssetOptionsArgs) -> AssetOptions:
            d = self.get_asset_options(args.symbol)
            return AssetOptions.model_validate(d)

        @mcp.tool(
            name="get_instrument_trades_latest",
            title="Последние сделки",
            description="GET /v1/instruments/{symbol}/trades/latest",
            structured_output=False,
        )
        def _get_instrument_trades_latest(args: InstrTradesLatestArgs) -> InstrTradesLatest:
            d = self.get_instrument_trades_latest(args.symbol, args.limit)
            if "symbol" not in d:
                d = {"symbol": args.symbol, **d}
            return InstrTradesLatest.model_validate(d)

        @mcp.tool(
            name="get_transactions",
            title="Транзакции",
            description="GET /v1/accounts/{account_id}/transactions",
        )
        def _get_transactions(args: TransactionsArgs) -> dict:
            d = self.get_transactions(args.account_id, args.start, args.end)
            return d

        @mcp.tool(
            name="create_session",
            title="Создать сессию",
            description="POST /v1/sessions",
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

    def get_orderbook(self, symbol: str, depth: int = 10) -> dict[str, Any]:
        """Получить биржевой стакан"""
        return self.execute_request("GET", f"/v1/instruments/{symbol}/orderbook", params={"depth": depth})

    def get_candles(
        self, symbol: str, timeframe: str = "D", start: str | None = None, end: str | None = None
    ) -> dict[str, Any]:
        """Получить исторические свечи"""
        params = {"timeframe": timeframe}
        if start:
            params["interval.start_time"] = start
        if end:
            params["interval.end_time"] = end
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

    def create_order(self, account_id: str, order_data: dict[str, Any]) -> dict[str, Any]:
        """Создать новый ордер"""
        return self.execute_request("POST", f"/v1/accounts/{account_id}/orders", json=order_data)

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

    def get_positions(self, account_id: str) -> dict[str, Any]:
        """Получить открытые позиции"""
        return self.execute_request("GET", f"/v1/accounts/{account_id}")

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

    def get_instrument_trades_latest(self, symbol: str, limit: int | None = None) -> dict[str, Any]:
        """Лента последних сделок по инструменту."""
        params = {"limit": limit} if limit is not None else None
        return self.execute_request("GET", f"/v1/instruments/{symbol}/trades/latest", params=params)

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
