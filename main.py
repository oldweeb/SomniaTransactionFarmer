import argparse
import logging

import requests
import toml

from eth_account.signers.local import LocalAccount
from web3 import Web3

from logger.logger import logger
from settings.settings import Settings, ApiSettings, AccountSettings, FarmSettings, PingPongSettings
from tran_generation.send_stt import send_stt_multiple
from tran_generation.swap_ping_pong import swap_ping_pong_multiple

BALANCE_THRESHOLD = 0.3


def start() -> None:
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Somnia Testnet Transaction Bot')
    parser.add_argument('-c', '--config', type=str, required=True, help='Path to toml config file')
    args = parser.parse_args()

    config_file = toml.load(args.config)
    settings = Settings(
        api=ApiSettings(**config_file['api']),
        account=AccountSettings(**config_file['account']),
        farm=FarmSettings(**config_file['farm']),
    )

    session = requests.Session()
    session.proxies = {
        'http': settings.api.proxy,
        'https': settings.api.proxy
    } if settings.api.proxy else None

    web3 = Web3(Web3.HTTPProvider(settings.api.rpc_url, session=session))
    logger.info(f'Connected to RPC: {web3.is_connected()}')

    account: LocalAccount = web3.eth.account.from_key(settings.account.private_key)
    logger.info(f"Account address: {account.address}")

    balance = web3.from_wei(web3.eth.get_balance(account.address), 'ether')
    logger.info(f'Balance: {balance} STT')
    if balance < BALANCE_THRESHOLD:
        logger.error(f'Balance is too low, required at least {BALANCE_THRESHOLD} STT')
        return

    if settings.farm.stt_send:
        send_stt_multiple(account, web3, settings.account.tran_count, settings.api.gas_price)

    if settings.farm.ping_pong_swap:
        settings.ping_pong = PingPongSettings(**config_file['ping_pong'])
        swap_ping_pong_multiple(account, web3, settings.ping_pong, settings.account.tran_count)


if __name__ == '__main__':
    start()
