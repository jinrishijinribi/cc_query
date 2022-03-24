# import sqlite3
from web3.auto import Web3 as Web3_auto
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
from db import *
import requests

with open('cc_token.abi', 'r') as fi:
    cc_abi = json.load(fi)

with open('cow_park_swap.abi', 'r') as fi:
    cc_swap_abi = json.load(fi)

w3_auto = Web3_auto(Web3_auto.HTTPProvider('https://bsc-dataseed.binance.org/'))
# conn = sqlite3.connect('cc_action.db', check_same_thread=False)
w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
cc_contract = w3.eth.contract(Web3.toChecksumAddress('0x982de39fb553c7b4399940a811c6078a87d4efba'), abi=cc_abi)
cc_swap = w3.eth.contract(Web3.toChecksumAddress('0xaF345d7e61257Ab4682dd7371f4B2711f1B3a945'), abi=cc_swap_abi)
busd_swap = w3.eth.contract(Web3.toChecksumAddress('0x58f876857a02d6762e0101bb5c46a8c1ed44dc16'), abi=cc_swap_abi)


def decode_address(address):
    return address.replace("0x000000000000000000000000", "0x")


def encode_address(address):
    return address.replace("0x", "0x000000000000000000000000")


def sync_cc_holder(last_update):
    query_pay_load = {'query': 'query {cowCoinHolders(first: 1000,where: {lastUpdateAt_gte: '
                               + last_update
                               + ' }, orderBy: lastUpdateAt, orderDirection: asc){id, balance, lastUpdateAt}}'}
    response_query = requests.post('https://api.thegraph.com/subgraphs/name/kiedethohngoesoo6ber/cow-park-bsc',
                                   data=json.dumps(query_pay_load)).json()
    data = response_query['data']['cowCoinHolders']
    print(data)
    for item in data:
        save_cc_holder(item['id'], item['balance'], item['lastUpdateAt'])
        last_update = item['lastUpdateAt']
    return last_update


def sync_db_by_contract():
    contracts = get_contract()
    latest_block = w3.eth.get_block('latest')
    for contract in contracts:
        if contract['status'] != 'enable':
            continue
        tag = contract['tag']
        if tag == 'pre_sale':
            sync_pre_sale(contract, int(contract['latest_block']) + 1, latest_block['number'], 1000)
        if tag == 'pancake':
            sync_cc_pancake(contract, int(contract['latest_block']) + 1, latest_block['number'], 1000)
        if tag == 'bind_box':
            sync_bind_box(contract, int(contract['latest_block']) + 1, latest_block['number'], 1000)
        if tag == 'recycle':
            sync_cc_recycle(contract, int(contract['latest_block']) + 1, latest_block['number'], 1000)
        # if tag == 'random_cow':
        #     sync_random_cow(contract, int(contract['latest_block']) + 1, latest_block['number'], 1000)
        if tag == 'transfer':
            transfer(contract, int(contract['latest_block']) + 1, latest_block['number'], 1000)
        if tag == 'random_cow':
            sync_random_cow2(contract, int(contract['latest_block']) + 1, latest_block['number'], 1000)


def sync_db_by_wallet():
    wallet = get_w_address()
    print(wallet)
    sync_w_address(wallet)


def sync_pre_sale(address, start, end, step):
    # pre_sale 的 topic 0x86137a9de2426639b92798b8d88fdffba9ec25ced6206a4de472ab77cc931ad5
    # 预售合约PreSale 事件
    print(address['tag'], start, end)
    while start < end:
        f = w3_auto.eth.filter(
            {
                "address": Web3.toChecksumAddress(address['address']),
                "fromBlock": start,
                "toBlock": start + step,
                "topics": ["0x86137a9de2426639b92798b8d88fdffba9ec25ced6206a4de472ab77cc931ad5"]
            }
        )
        logs = f.get_all_entries()
        # print(logs)
        for log in logs:
            # print(log)
            data = log['data'][2:]
            tx = Web3.toHex(log['transactionHash'])
            to_address = Web3.toChecksumAddress(decode_address(w3.toHex(log['topics'][2])))
            eth = int(data[32:64], 16)
            cc = int(data[96:128], 16)
            # print(log['blockNumber'], to_address, eth, cc)
            save_cc_logs(log['blockNumber'], tx, log['logIndex'], cc, 0, 0, eth, to_address, address['address'], address['tag'])
            update_contract_block(address['id'], log['blockNumber'])
        # update_contract_block(address['id'], start)
        start += step
        update_contract_block(address['id'], start)
    # print('sale')
    update_contract_block(address['id'], end)


def sync_bind_box(address, start, end, step):
    # 盲盒合约的 BindboxCow 事件, 再从所有日志中获取第一个Transfer事件
    print(address['tag'], start, end)
    while start < end:
        f = w3_auto.eth.filter(
            {
                "address": Web3.toChecksumAddress(address['address']),
                "fromBlock": start,
                "toBlock": start + step,
                "topics": ["0xdefd096ca1e084f503c409dc67d184746cd252fab73841d4da0044c88e143067"]
            }
        )
        logs = f.get_all_entries()
        # print(logs)
        for log in logs:
            tx = Web3.toHex(log['transactionHash'])
            to_address = decode_address(w3.toHex(log['topics'][2]))
            tx_content = w3.eth.get_transaction(tx)
            tx_logs = w3.eth.get_transaction_receipt(Web3.toHex(tx_content['hash']))
            # print(tx_logs['logs'][0]['data'])
            # 开盲盒的第一条日志是cc币的转移
            logs_data = tx_logs['logs'][0]['data']
            cc = int(logs_data[2:][32:64], 16)
            save_cc_logs(log['blockNumber'], tx, log['logIndex'], 0, cc, 0, 0, to_address, address['address'], address['tag'])
            print(tx, to_address, cc)
        start += step
        update_contract_block(address['id'], start)
    update_contract_block(address['id'], end)


def sync_random_cow2(address, start, end, step):
    # 盲盒合约的 BindboxCow 事件, 新的盲盒时间，在日志里面有价格
    print(address['tag'], start, end)
    while start < end:
        f = w3_auto.eth.filter(
            {
                "address": Web3.toChecksumAddress(address['address']),
                "fromBlock": start,
                "toBlock": start + step,
                "topics": ["0x2eca55fc458a776333d44665209aae2631006db9797f3af6c8d52958f2558a16"]
            }
        )
        logs = f.get_all_entries()
        for log in logs:
            tx = Web3.toHex(log['transactionHash'])
            to_address = decode_address(w3.toHex(log['topics'][2]))
            logs_data = log['data']
            cc = int(logs_data[2:][64:128], 16)
            save_cc_logs(log['blockNumber'], tx, log['logIndex'], 0, cc, 0, 0, to_address, address['address'], address['tag'])
        start += step
        update_contract_block(address['id'], start)
    update_contract_block(address['id'], end)


def sync_random_cow(address, start, end, step):
    # 盲盒合约的 BindboxCow 事件, 再从所有日志中获取第一个Transfer事件
    print(address['tag'], start, end)
    while start < end:
        f = w3_auto.eth.filter(
            {
                "address": Web3.toChecksumAddress(address['address']),
                "fromBlock": start,
                "toBlock": start + step,
                "topics": ["0xccd3c67bea89a236bd78c7cb8268163bb2deff876e4fc3e1a8cde18e2fe78783"]
            }
        )
        logs = f.get_all_entries()
        # print(logs)
        for log in logs:
            tx = Web3.toHex(log['transactionHash'])
            to_address = decode_address(w3.toHex(log['topics'][2]))
            tx_content = w3.eth.get_transaction(tx)
            tx_logs = w3.eth.get_transaction_receipt(Web3.toHex(tx_content['hash']))
            # print(tx_logs['logs'][0]['data'])
            # 开盲盒的第一条日志是cc币的转移
            logs_data = tx_logs['logs'][0]['data']
            cc = int(logs_data[2:][32:64], 16)
            save_cc_logs(log['blockNumber'], tx, log['logIndex'], 0, cc, 0, 0, to_address, address['address'], address['tag'])
            print(tx, to_address, cc)
        start += step
        update_contract_block(address['id'], start)
    update_contract_block(address['id'], end)


def sync_cc_pancake(address, start, end, step):
    # address是cc的swap合约
    # cc swap合约的swap事件, 与 pancake swap 合约的交互
    # swap 日志的 的topic code
    print(address['address'], start, end)
    while start < end:
        # pancake 的 cc 的swap
        f = w3_auto.eth.filter(
            {
                # 合约的address
                "address": Web3.toChecksumAddress(address['address']),
                "fromBlock": start,
                "toBlock": start + step,
                "topics": [
                    "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822",
                    encode_address(Web3.toChecksumAddress("0x10ED43C718714eb63d5aA57B78B54704E256024E"))
                ]
            }
        )
        logs = f.get_all_entries()
        print(logs)
        for log in logs:
            change_address = Web3.toChecksumAddress(decode_address(Web3.toHex(log['topics'][2])))
            # block_number = log['blockNumber']
            data = log['data'][2:]
            tx = Web3.toHex(log['transactionHash'])
            amount0in = int(data[32:64], 16)
            amount1in = int(data[96:128], 16)
            amount0out = int(data[160:192], 16)
            amount1out = int(data[224:256], 16)
            # 如果是卖cc的单子，就查一下tx, 后来发现不用查cc，swap对于cc来说是单向变动。
            if amount0in > 0 and amount1out > 0:
                tx_content = w3.eth.get_transaction(tx)
                change_address = tx_content['from']
            # save_swap_log(block_number, tx, amount0in, amount0out, amount1in, amount1out, change_address)
            # 这边的in,out 是对于合约而言的，对于用户而言是相反的
            print(amount0in, amount0out, amount1in, amount1out)
            save_cc_logs(log['blockNumber'], tx, log['logIndex'], amount0out, amount0in, amount1out, amount1in,
                         change_address, address['address'],
                         address['tag'])
        start += step
        update_contract_block(address['id'], start)
    update_contract_block(address['id'], end)


def sync_cc_recycle(address, start, end, step):
    print(address['tag'], start, end)
    while start < end:
        f = w3_auto.eth.filter(
            {
                "address": Web3.toChecksumAddress(address['address']),
                "fromBlock": start,
                "toBlock": start + step,
                "topics": ["0x9d34ba625fd37a3ecdb9356d6cb304f867f08ca6200d6202bc56a9d2627e3216"]
                # "topics": ["0x59b221be37f9d90e279ee07ea76d7521f95e6bdb8e6b6ccbc07e905f95331fdd"]
            }
        )
        logs = f.get_all_entries()
        # print(logs)
        for log in logs:
            tx = Web3.toHex(log['transactionHash'])
            log_data = log['data']
            to_address = Web3.toChecksumAddress(decode_address(log_data[0:66]))
            cc = int(log_data[2:][96:128], 16)
            save_cc_logs(log['blockNumber'], tx, log['logIndex'], cc, 0, 0, 0, to_address, address['address'],
                         address['tag'])
        start += step
        update_contract_block(address['id'], start)
    update_contract_block(address['id'], end)


def transfer(address, start, end, step):
    print(address['tag'], address['address'], start, end)
    while start < end:
        print(start)
        f = w3_auto.eth.filter(
            {
                "address": Web3.toChecksumAddress(address['address']),
                "fromBlock": start,
                "toBlock": start + step,
                "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]
            }
        )
        logs = f.get_all_entries()
        # print(logs)
        for log in logs:
            tx = Web3.toHex(log['transactionHash'])
            # print(log)
            tx_logs = w3.eth.get_transaction_receipt(tx)
            # print(tx, tx_logs, len(tx_logs['logs']))
            if len(tx_logs['logs']) == 1:
                # 只有一条日志的是简单的transfer
                log_data = log['data']
                print(log_data, log)
                from_address = decode_address(Web3.toHex(log['topics'][1]))
                to_address = decode_address(Web3.toHex(log['topics'][2]))
                cc = int(log_data[2:][32:64], 16)
                save_cc_logs(log['blockNumber'], tx, log['logIndex'], cc, 0, 0, 0, to_address, address['address'],
                             address['tag'])
                save_cc_logs(log['blockNumber'], tx, log['logIndex'], 0, cc, 0, 0, from_address, address['address'],
                             address['tag'])
                print(tx, from_address, to_address, cc)
                # save_cc_logs(log['blockNumber'], tx, log['logIndex'], cc, 0, 0, 0, to_address, address['address'],
                #              address['tag'])
        start += step
        update_contract_block(address['id'], start)
    update_contract_block(address['id'], end)


def sync_w_address(address):
    for i in address:
        cc = cc_contract.functions.balanceOf(Web3.toChecksumAddress(i['address'])).call()
        bnb = w3.eth.get_balance(Web3.toChecksumAddress(i['address']))
        update_w_address(i['address'], bnb, cc)

