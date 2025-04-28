import json
import random
from typing import Any

from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.types import TxReceipt

from logger.logger import logger
from settings.settings import QuickSwapDexSettings
from utils.web3_utils import get_erc20_token_contract, get_erc20_token_balance, get_txn_status_formatted

ERC20_ABI = json.loads('''
[
    {"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},
    {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},
    {"constant":false,"inputs":[],"name":"deposit","outputs":[],"type":"function"},
    {"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"type":"function"},
    {"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"type":"function"}
]
''')
FALLBACK_GAS = 250000

class QuickSwap:
    def __init__(self, web3: Web3, account: LocalAccount, settings: QuickSwapDexSettings):
        self.web3 = web3
        self.account = account
        self.router = self.web3.eth.contract(
            address=self.web3.to_checksum_address(settings.router_contract),
            abi=settings.router_abi
        )

        self.stt = self.web3.to_checksum_address('0x0000000000000000000000000000000000000000')
        self.wstt = self.web3.to_checksum_address(settings.wstt_contract)
        self.usdc = self.web3.to_checksum_address(settings.usdc_contract)

    def wrap(self, amount: int):
        wstt_contract = get_erc20_token_contract(self.web3, self.wstt, ERC20_ABI)
        wrap_function = wstt_contract.functions.deposit
        tx = wrap_function().build_transaction(self.__build_tx_params__(tx_function=wrap_function, value=amount))
        return self.__send_tx__(tx)

    def unwrap(self, amount: int):
        wstt_contract = get_erc20_token_contract(self.web3, self.wstt, ERC20_ABI)
        unwrap_function = wstt_contract.functions.withdraw
        tx = unwrap_function(amount).build_transaction(self.__build_tx_params__(tx_function=unwrap_function))
        return self.__send_tx__(tx)

    def approve(self, token: str, spender: str, amount: int):
        token_contract = get_erc20_token_contract(self.web3, token, ERC20_ABI)
        approve_function = token_contract.functions.approve
        tx = approve_function(spender, amount).build_transaction(self.__build_tx_params__(tx_function=approve_function))
        return self.__send_tx__(tx)

    def swap(self, source: str, target: str, amount_in: int) -> TxReceipt:
        source = source.lower()
        target = target.lower()

        if source == 'stt' and target == 'wstt':
            return self.wrap(amount_in)

        if source == 'wstt' and target == 'stt':
            return self.unwrap(amount_in)

        token_map = {
            'stt': self.stt,
            'wstt': self.wstt,
            'usdc': self.usdc,
        }

        token_in = token_map[source] if source != 'stt' else self.wstt
        token_out = token_map[target]

        if source != 'stt':
            self.approve(token_in, self.router.address, amount_in)

        if target == 'stt':
            call1 = self.__swap_call_data__(token_in, self.wstt, '0x0000000000000000000000000000000000000000', amount_in)
            call2 = self.__unwrap_call_data__(0)
            multicall_function = self.router.functions.multicall
            tx = multicall_function([call1, call2]).build_transaction(self.__build_tx_params__(tx_function=multicall_function))
            return self.__send_tx__(tx)

        params = {
            'tokenIn': token_in,
            'tokenOut': token_out,
            'deployer': self.stt,
            'recipient': self.account.address,
            'deadline': self.__get_deadline__(),
            'amountIn': amount_in,
            'amountOutMinimum': 0,
            'limitSqrtPrice': 0
        }

        swap_function = self.router.functions.exactInputSingle
        tx = swap_function(params).build_transaction(self.__build_tx_params__(tx_function=swap_function, value=amount_in))
        return self.__send_tx__(tx)

    def __build_tx_params__(self, tx_function = None, value: int = 0):
        base_tx = {
            'from': self.account.address,
            'nonce': self.web3.eth.get_transaction_count(self.account.address),
            'gasPrice': self.web3.eth.gas_price,
            'value': value
        }

        if tx_function:
            try:
                estimated_gas = tx_function.estimate_gas(base_tx)
                base_tx['gas'] = estimated_gas
            except Exception:
                base_tx['gas'] = FALLBACK_GAS
        else:
            base_tx['gas'] = FALLBACK_GAS

        return base_tx

    def __send_tx__(self, tx: Any):
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def __swap_call_data__(self, token_in: str, token_out: str, recipient: str, amount_in: int):
        params = {
            'tokenIn': token_in,
            'tokenOut': token_out,
            'deployer': self.stt,
            'recipient': recipient,
            'deadline': self.__get_deadline__(),
            'amountIn': amount_in,
            'amountOutMinimum': 0,
            'limitSqrtPrice': 0
        }
        return self.router.encode_abi('exactInputSingle', args=[params])

    def __unwrap_call_data__(self, amount_minimum: int):
        return self.router.encode_abi('unwrapWNativeToken', args=[amount_minimum, self.account.address])

    def __get_deadline__(self):
        return self.web3.eth.get_block('latest')['timestamp'] + 1200

def quick_swap(account: LocalAccount, web3: Web3, settings: QuickSwapDexSettings, repeat: int):
    dex = QuickSwap(web3, account, settings)
    pairs = [
        { 'source': 'STT', 'target': 'WSTT', 'balance_percentage': 50 },
        { 'source': 'WSTT', 'target': 'STT', 'balance_percentage': 90 },
        { 'source': 'STT', 'target': 'USDC', 'balance_percentage': 5 },
        { 'source': 'USDC', 'target': 'STT', 'balance_percentage': 90 },
    ]

    token_map = {
        'STT': dex.stt,
        'WSTT': dex.wstt,
        'USDC': dex.usdc,
    }

    for i in range(repeat):
        pair = random.choice(pairs)
        source_token = web3.eth.contract(address=token_map[pair['source']], abi=ERC20_ABI)

        balance, decimals = (web3.eth.get_balance(account.address), 18) if pair['source'] == 'STT' else get_erc20_token_balance(account, source_token)
        if balance == 0:
            logger.warning(f'0 {pair['source']} balance, skipping...')
            continue

        max_swap = (balance * (pair['balance_percentage'] / 100)) / (10 ** decimals)

        amount_to_swap = random.uniform(0, max_swap)
        logger.info(f'Swapping {amount_to_swap:.3f} {pair['source']} to {pair['target']}')
        tx_receipt: TxReceipt = dex.swap(pair['source'], pair['target'], int(amount_to_swap * (10 ** decimals)))
        logger.info(f'Tx hash: {tx_receipt['transactionHash'].to_0x_hex()} - status: {get_txn_status_formatted(tx_receipt)})')

