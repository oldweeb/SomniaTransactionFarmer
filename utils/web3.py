from eth_account import Account

def get_random_evm_address():
    account = Account.create()
    return account.address