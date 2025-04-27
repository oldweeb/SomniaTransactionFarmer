from typing import Any

from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3.contract import Contract
from enum import Enum

from web3.types import TxReceipt

class TxStatusFormatted(Enum):
    Successful = 'successful',
    Failed = 'failed',

def get_random_evm_address():
    account = Account.create()
    return account.address

def get_erc20_token_contract(web3: Web3, token_address: str, erc20_abi: Any) -> Contract:
    return web3.eth.contract(address=web3.to_checksum_address(token_address), abi=erc20_abi)

def get_erc20_token_balance(account: LocalAccount, token: Contract) -> (int, int):
    token_balance = token.functions.balanceOf(account.address).call()
    token_decimals = token.functions.decimals().call()
    return token_balance, token_decimals

def get_txn_status_formatted(receipt: TxReceipt) -> TxStatusFormatted:
    return TxStatusFormatted.Successful if receipt['status'] else TxStatusFormatted.Failed