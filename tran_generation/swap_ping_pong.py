import random
import json

from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.contract import Contract

from logger.logger import logger
from settings.settings import PingPongSettings
from utils.web3_utils import get_erc20_token_balance, get_erc20_token_contract, get_txn_status_formatted, \
    get_erc20_token_balance_readable

CHAIN_ID = 50312

ERC20_ABI = json.loads('''
[
    {"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},
    {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}
]
''')

SWAP_FEES = 500

def swap_ping_pong_multiple(account: LocalAccount, web3: Web3, settings: PingPongSettings, repeat: int) -> None:
    for i in range(repeat):
        swap_ping_pong(account, web3, settings)

def swap_ping_pong(account: LocalAccount, web3: Web3, settings: PingPongSettings) -> None:
    router: Contract = web3.eth.contract(
        address=web3.to_checksum_address(settings.router_contract),
        abi=json.loads(settings.router_abi)
    )

    ping_token = get_erc20_token_contract(web3, settings.ping_contract, ERC20_ABI)
    pong_token = get_erc20_token_contract(web3, settings.pong_contract, ERC20_ABI)

    ping_balance, ping_decimals = get_erc20_token_balance(account, ping_token)
    pong_balance, pong_decimals = get_erc20_token_balance(account, pong_token)

    ping_human = get_erc20_token_balance_readable(account, ping_token)
    pong_human = get_erc20_token_balance_readable(account, pong_token)

    logger.info(f'Ping balance: {ping_human:.6f} | Pong balance: {pong_human:.6f}')

    swap_ping_to_pong = random.choice([True, False])

    token_in = settings.ping_contract if swap_ping_to_pong else settings.pong_contract
    token_out = settings.pong_contract if swap_ping_to_pong else settings.ping_contract
    decimals = ping_decimals if swap_ping_to_pong else pong_decimals
    balance = ping_human if swap_ping_to_pong else pong_human

    # Swap half of balance, randomly from 1 to half
    max_swap_human = int(balance // 2)
    if max_swap_human == 0:
        logger.warning("Not enough balance to swap.")
        return

    amount_in_human = random.randint(1, max_swap_human)
    amount_in = amount_in_human * 10 ** decimals

    logger.info(f'Swapping {amount_in_human} {'PING' if swap_ping_to_pong else 'PONG'}')

    # Define swap parameters
    params = {
        'tokenIn': token_in,
        'tokenOut': token_out,
        'fee': SWAP_FEES,
        'recipient': account.address,
        'amountIn': amount_in,
        'amountOutMinimum': 0,  # You could calculate better for real swaps
        'sqrtPriceLimitX96': 0
    }

    # Build transaction
    base_tx = {
        'from': account.address,
        'value': 0,
        'nonce': web3.eth.get_transaction_count(account.address),
        'chainId': CHAIN_ID,
        'gasPrice': web3.eth.gas_price
    }

    # Estimate gas dynamically
    estimated_gas = router.functions.exactInputSingle(params).estimate_gas(base_tx)
    logger.info(f"Estimated gas: {estimated_gas}")

    tx = {**base_tx, 'gas': int(estimated_gas * 1.2)}

    # Build and send transaction
    swap_txn = router.functions.exactInputSingle(params).build_transaction(tx)

    signed_txn = account.sign_transaction(swap_txn)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

    logger.info(f"Swap transaction sent. Tx Hash: 0x{tx_hash.hex()}")
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    logger.info(f'Transaction was {get_txn_status_formatted(receipt)}')
