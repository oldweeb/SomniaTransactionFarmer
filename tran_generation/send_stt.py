import random

from eth_account.signers.local import LocalAccount
from web3 import Web3

from logger.logger import logger
from utils.web3_utils import get_random_evm_address, get_txn_status_formatted

CHAIN_ID = 50312

def send_stt_multiple(account: LocalAccount, web3: Web3, tran_count: int, gas_price = None) -> None:
    nonce = web3.eth.get_transaction_count(account.address)
    gas_price = gas_price if gas_price else web3.eth.gas_price

    for i in range(tran_count):
        send_stt(account, web3, nonce, gas_price)
        nonce += 1

def send_stt(account: LocalAccount, web3: Web3, nonce: int, gas_price: int) -> None:
    amount = round(random.uniform(0.001, 0.02), 6)
    recipient_address = get_random_evm_address()

    gas_limit = web3.eth.estimate_gas({
        'from': account.address,
        'to': recipient_address,
        'value': web3.to_wei(amount, 'ether')
    })

    txn = {
        'to': recipient_address,
        'nonce': nonce,
        'chainId': CHAIN_ID,
        'value': web3.to_wei(amount, 'ether'),
        'gas': gas_limit,
        'gasPrice': gas_price
    }

    logger.info(f'Sending {amount} STT to {recipient_address}. Nonce: {txn["nonce"]}')
    logger.info(f'Estimated gas: {gas_limit}')

    signed_txn = account.sign_transaction(txn)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    logger.info(f'Transaction hash: 0x{tx_hash.hex()}')
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=15)
    logger.info(f'Transaction 0x{tx_hash.hex()} was {get_txn_status_formatted(receipt).value}')