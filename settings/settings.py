from dataclasses import dataclass
from typing import Optional


@dataclass
class ApiSettings:
    rpc_url: str
    proxy: Optional[str] = None
    gas_price: Optional[int] = None

@dataclass
class AccountSettings:
    private_key: str
    tran_count: int

@dataclass
class FarmSettings:
    stt_send: bool
    ping_pong_swap: bool
    quick_swap: bool

@dataclass
class PingPongSettings:
    router_contract: str
    ping_contract: str
    pong_contract: str
    router_abi: str

@dataclass
class QuickSwapDexSettings:
    router_contract: str
    router_abi: str
    usdc_contract: str
    wstt_contract: str

@dataclass
class Settings:
    api: ApiSettings
    account: AccountSettings
    farm: FarmSettings
    ping_pong: Optional[PingPongSettings] = None
    quick_swap: Optional[QuickSwapDexSettings] = None