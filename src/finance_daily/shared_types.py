from dataclasses import dataclass
from typing import Dict, List


@dataclass(slots=True)
class Ticker:
    symbol: str
    name: str | None
    currency: str = "USD"


@dataclass
class ETLTickers:
    tickers_dict: Dict[str, List[Ticker]]

    def to_list(self) -> List[Ticker]:
        return [ticker for group in self.tickers_dict.values() for ticker in group]

    def to_symbols(self) -> List[str]:
        return [ticker.symbol for ticker in self.to_list()]

    def get_group(self, group_name: str) -> List[Ticker]:
        return self.tickers_dict.get(group_name, [])

    def get_group_symbols(self, group_name: str) -> List[str]:
        return [ticker.symbol for ticker in self.get_group(group_name)]

    def has_symbol(self, symbol: str) -> bool:
        return any(ticker.symbol == symbol for ticker in self.to_list())
