import decimal

from __init__ import route_bp
from flask import request
from sync_db import *
# from stat_db import *
from db import *
import json
import time
import datetime
import requests
# tag = False
# from models.model import *


# def obj_dict(obj):
#     return obj.__dict__


# @route_bp.route("/hello", methods=["GET"])
# def hello():
#     is_connected()
#     return "success"


# def get_block_by_ts(ts):
#     r = requests.get('https://api.bscscan.com/api?module=block&action=getblocknobytime&timestamp=' + str(
#         ts) + '&closest=before&apikey=27238ENGZWP4KGFUAE31KTJAZB5Y6HKPNV').json()
#     print('bs_result', ts, r)
#     block = r['result']
#     return block

class DecimalEncode(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        super(DecimalEncode, self).default(o)


def get_block_by_ts(ts):
    block = w3.eth.get_block("latest")
    return block['number'] + int((ts - block['timestamp']) / 3)


@route_bp.route("/sync/data", methods=['GET'])
def sync_data():
    config = get_config("contract.sync")
    contract_sync = int(config[0]['value'])
    print(contract_sync)
    if contract_sync > 0:
        print('sync_data')
        update_config("contract.sync", 0)
        sync_db_by_contract()
        update_config("contract.sync", 1)
        print('sync_data end')
    return "success"


@route_bp.route("/sync/graphql/test", methods=['GET'])
def sync_data_graphql():
    config = get_config("graphql.last.update")
    graphql_update = int(config[0]['value'])
    last_update = sync_cc_holder(str(graphql_update))
    update_config("graphql.last.update", last_update)
    return "success"


@route_bp.route("/sync/data/wallet", methods=['GET'])
def sync_data_wallet():
    config = get_config("wallet.sync")
    contract_sync = int(config[0]['value'])
    print(contract_sync)
    if contract_sync > 0:
        print('sync_data_wallet')
        update_config("wallet.sync", 0)
        sync_db_by_wallet()
        update_config("wallet.sync", 1)
        print('sync_data_wallet end')
    return "success"

# @route_bp.route("/sync/data/false", methods=['GET'])
# def sync_data_false():
#     tag = False
#     return json.dumps(tag)


# 钱包地址新建
@route_bp.route("/wallet/create", methods=['POST'])
def create_w_address():
    data = request.json
    name = data['name']
    address = data['address']
    save_w_address(address, name, 0, 0)
    return "success"


# 钱包地址列表
@route_bp.route("/wallet/list", methods=['GET'])
def list_w_address():
    data = get_w_address()
    return json.dumps({
        "data": get_w_address(),
        "count": len(data)
    })


# 钱包地址删除
@route_bp.route("/wallet/delete", methods=['POST'])
def delete_w_address():
    data = request.json
    print(data)
    c_id = data['id']
    del_w_address(c_id)
    return "success"


# 合约地址新建
@route_bp.route("/address/create", methods=['POST'])
def create_c_address():
    data = request.json
    name = data['name']
    address = data['address']
    tag = data['tag']
    latest_block = data['latest_block']
    save_c_address(address, name, tag, latest_block)
    return "success"


# 合约地址列表
@route_bp.route("/address/list", methods=['GET'])
def list_c_address():
    data = get_c_address()
    return json.dumps({
        "data": data,
        "count": len(data)
    })


# 合约地址删除
@route_bp.route("/address/delete", methods=['POST'])
def delete_c_address():
    data = request.json
    print(data)
    c_id = data['id']
    del_c_address(c_id)
    # delete_w_address(c_id)
    return "success"


# 钱包列表
# @app.route("/api/wallet/list", methods=['GET'])
# def list_w_address():
#     get_w_address()
#     return json.dumps(get_w_address())


# 充值释放bnb
@route_bp.route("/manual/charge", methods=['POST'])
def manual_charge():
    data = request.json
    print(data)
    bnb_in = data['bnb_in']
    bnb_out = data['bnb_out']
    cc_in = data['cc_in']
    cc_out = data['cc_out']
    create_time = data['create_time']
    note = data['note']
    save_cc_manual_logs(create_time, bnb_in, bnb_out, cc_in, cc_out, note)
    return "success"


# 充值/释放删除
@route_bp.route("/manual/charge/delete", methods=['POST'])
def manual_charge_delete():
    data = request.json
    print(data)
    c_id = data['id']
    del_cc_manual_logs(c_id)
    return "success"


# 充值/释放列表
@route_bp.route("/manual/charge/list/<tp>", methods=['GET'])
def manual_charge_list(tp):
    data = get_cc_manual_logs()
    filter_data = list(filter(lambda x: int(x[tp]) > 0, data))

    return json.dumps({
        "data": filter_data,
        "count": len(filter_data)
    })


# 首页统计
@route_bp.route("/index/stat", methods=['GET'])
def index_stat():

    block_now = get_block_by_ts(int(time.time()))
    block_24h = get_block_by_ts(int(time.time() - 3600 * 24))
    print(block_24h, block_now)
    manual_charge_result = get_charge_bnb_cc()[0]
    # 1
    charge_bnb = int(manual_charge_result['bnb_in'])
    release_cc = int(manual_charge_result['cc_out'])
    latest_time = manual_charge_result['latest_time']

    # my_bnb_cc = get_my_bnb_cc()[0]
    # my_bnb = my_bnb_cc()['bnb']
    # my_cc = my_bnb_cc['cc']

    my_wallet = get_w_address()
    my_wallet_address = list(map(lambda x: x['address'], my_wallet))
    # 2
    my_wallet_bnb = sum(list(map(lambda x: int((x['bnb'])), my_wallet)))
    # 3
    my_wallet_cc = sum(list(map(lambda x: int(x['cc']), my_wallet)))

    # cc_logs by address
    cc_logs = get_cc_logs_by_address(0, block_now)
    cc_logs_24h = get_cc_logs_by_address(0, block_24h)
    cc_logs_my = list(filter(lambda x: x['user_address'] in my_wallet_address, cc_logs))
    cc_logs_my_24h = list(filter(lambda x: x['user_address'] in my_wallet_address, cc_logs_24h))
    my_bnb_in = sum(list(map(lambda x: int(x['bnb_in']), cc_logs_my)))
    my_bnb_out = sum(list(map(lambda x: int(x['bnb_out']), cc_logs_my)))
    my_bnb_in_24 = sum(list(map(lambda x: int(x['bnb_in']), cc_logs_my_24h)))
    my_bnb_out_24 = sum(list(map(lambda x: int(x['bnb_out']), cc_logs_my_24h)))
    # 4
    my_bnb_24 = my_wallet_bnb - (my_bnb_in - my_bnb_in_24) + (my_bnb_out - my_bnb_out_24)
    my_cc_in = sum(list(map(lambda x: int(x['cc_in']), cc_logs_my)))
    my_cc_out = sum(list(map(lambda x: int(x['cc_out']), cc_logs_my)))
    my_cc_in_24 = sum(list(map(lambda x: int(x['cc_in']), cc_logs_my_24h)))
    my_cc_out_24 = sum(list(map(lambda x: int(x['cc_out']), cc_logs_my_24h)))
    # 5
    my_cc_24 = my_wallet_cc - my_cc_in + my_cc_out_24
    # 6
    cc_reserve = cc_swap.functions.getReserves().call()
    # print(cc_reserve)
    busd_reserve = busd_swap.functions.getReserves().call()

    bnb_all_in = sum(list(map(lambda x: int(x['bnb_in']), cc_logs)))
    bnb_all_out = sum(list(map(lambda x: int(x['bnb_out']), cc_logs)))
    cc_all_in = sum(list(map(lambda x: int(x['cc_in']), cc_logs)))
    cc_all_out = sum(list(map(lambda x: int(x['cc_out']), cc_logs)))
    # 9
    individual_bnb_in = bnb_all_in - my_bnb_in
    # 7
    individual_bnb_out = bnb_all_out - my_bnb_out

    bnb_all_in_24 = sum(list(map(lambda x: int(x['bnb_in']), cc_logs_24h)))
    bnb_all_out_24 = sum(list(map(lambda x: int(x['bnb_out']), cc_logs_24h)))
    cc_all_in_24 = sum(list(map(lambda x: int(x['cc_in']), cc_logs_24h)))
    cc_all_out_24 = sum(list(map(lambda x: int(x['cc_out']), cc_logs_24h)))
    # 10
    individual_bnb_in_24 = bnb_all_in_24 - my_bnb_in_24
    # 8
    individual_bnb_out_24 = bnb_all_out_24 - my_bnb_out_24

    individual_cc_in = cc_all_in - my_cc_in
    individual_cc_out = cc_all_out - my_cc_out
    individual_cc_in_24 = cc_all_in_24 - my_cc_in_24
    individual_cc_out_24 = cc_all_out_24 - my_cc_out_24

    individual_bnb_out_pure = individual_bnb_out - individual_bnb_in
    individual_cc_in_pure = individual_cc_in - individual_cc_out
    individual_bnb_out_pure_24 = individual_bnb_out_24 - individual_bnb_in_24
    individual_cc_in_pure_24 = individual_cc_in_24 - individual_cc_out_24

    my_wallet_count = len(my_wallet)
    # all_count = len(cc_logs)
    all_count = len(list(filter(lambda x: (x['cc_in'] - x['cc_out']) > 0, cc_logs)))
    # all_count_24 = len(cc_logs_24h)
    all_count_24 = len(list(filter(lambda x: (x['cc_in'] - x['cc_out']) > 0, cc_logs_24h)))
    individual_count = all_count - my_wallet_count
    individual_count_24 = all_count_24 - my_wallet_count
    my_cc_in_pure = my_cc_in - my_cc_out

    return json.dumps({
        "data": {
            "charge_bnb": charge_bnb,
            "charge_latest_time": latest_time,
            "my_bnb": my_wallet_bnb,
            "my_bnb_24": my_bnb_24,
            "my_cc": my_wallet_cc,
            "my_cc_24": my_cc_24,
            "cc_price": {"cc": cc_reserve[0], "bnb": cc_reserve[1]},
            "bnb_price": {"busd": busd_reserve[0], "bnb": busd_reserve[1]},
            # "cc_price_24": 0,
            "individual_bnb_in": individual_bnb_in,
            "individual_bnb_in_24h": individual_bnb_in_24,
            "individual_bnb_out": individual_bnb_out,
            "individual_bnb_out_24h": individual_bnb_out_24,
            "individual_cc_price": {
                "bnb": individual_bnb_out_pure,
                "cc": individual_cc_in_pure
            },
            "individual_cc_price_24h": {
                "bnb": individual_bnb_out_pure_24,
                "cc": individual_cc_in_pure_24
            },
            "individual_earn": {
                "bnb": -individual_bnb_out_pure,
                "count": individual_count
            },
            "individual_earn_24h": {
                "bnb": -individual_bnb_out_pure_24,
                "count": individual_count_24
            }
        },
        "graph_data": {
            "my_wallet_count": my_wallet_count,
            "individual_count": individual_count,
            "individual_cc_count": individual_cc_in_pure,
            "my_cc_count": my_wallet_cc,
            "release": release_cc,
        }
    })


# 首页图表
@route_bp.route("/index/list", methods=['GET'])
def index_list():
    result = []
    # today = datetime.date.today().strftime("%Y-%m-%d")
    print(int(time.time()))
    today_ts = int(time.time()) - int(time.time()) % (3600 * 24)
    # today_ts = int(datetime.datetime.strptime(today, "%Y-%m-%d").timestamp())
    print(today_ts)
    block_today = int(get_block_by_ts(today_ts))
    for i in range(0, 7):
        print(i)
        block_start = block_today - int(3600 * 24 / 3) * (i + 1)
        block_end = block_today - int(3600 * 24 / 3) * i
        # print(block_start, block_end)

        my_wallet = get_w_address()
        my_wallet_address = list(map(lambda x: x['address'], my_wallet))
        cc_logs = get_cc_logs_by_address(block_start, block_end)
        cc_logs_my = list(filter(lambda x: x['user_address'] in my_wallet_address, cc_logs))
        my_cc_in = sum(list(map(lambda x: int(x['cc_in']), cc_logs_my)))
        my_cc_out = sum(list(map(lambda x: int(x['cc_out']), cc_logs_my)))
        cc_all_in = sum(list(map(lambda x: int(x['cc_in']), cc_logs)))
        cc_all_out = sum(list(map(lambda x: int(x['cc_out']), cc_logs)))
        result.append({
            "date": (datetime.date.today() - datetime.timedelta(i + 1)).strftime("%Y-%m-%d"),
            "individual_in": cc_all_in - my_cc_in,
            "individual_out": cc_all_out - my_cc_out
        })

    return json.dumps({
        "data": result,
    })


# # 统计/散户cc币流入流出
# @app.route("/api/stat/individual/cc", methods=['GET'])
# def individual_cc():
#     result = []
#     data = request.data
#     print(result)
    # print()
    # today = datetime.date.today().strftime("%Y-%m-%d")
    # today_ts = int(datetime.datetime.strptime(today, "%Y-%m-%d").timestamp())
    # block_today = int(get_block_by_ts(today_ts))
    # for i in range(0, 7):
    #     print(i)
    #     block_start = block_today - int(3600 * 24 / 3) * (i + 1)
    #     block_end = block_today - int(3600 * 24 / 3) * i
    #     # print(block_start, block_end)
    #
    #     my_wallet = get_w_address()
    #     my_wallet_address = list(map(lambda x: x['address'], my_wallet))
    #     cc_logs = get_cc_logs_by_address(block_start, block_end)
    #     cc_logs_my = list(filter(lambda x: x['user_address'] in my_wallet_address, cc_logs))
    #     my_cc_in = sum(list(map(lambda x: int(x['cc_in']), cc_logs_my)))
    #     my_cc_out = sum(list(map(lambda x: int(x['cc_out']), cc_logs_my)))
    #     cc_all_in = sum(list(map(lambda x: int(x['cc_in']), cc_logs)))
    #     cc_all_out = sum(list(map(lambda x: int(x['cc_out']), cc_logs)))
    #     result.append({
    #         "date": (datetime.date.today() - datetime.timedelta(i + 1)).strftime("%Y-%m-%d"),
    #         "individual_in": cc_all_in - my_cc_in,
    #         "individual_out": cc_all_out - my_cc_out
    #     })
    #
    # return json.dumps({
    #     "data": result,
    # })


# 统计/用户cc币持仓成本
@route_bp.route("/stat/address/cc", methods=['POST'])
def address_cc():
    data = request.json
    page = data["page"]
    size = data["size"]
    address = data["address"]
    address_log = get_cc_logs_by_address(0, 9999999999999)
    if len(address) > 0:
        address_log = list(filter(lambda x: x["user_address"] in address, address_log))

    result = []
    address_log = sorted(address_log, key=lambda x: x['cc_in'] - x['cc_out'], reverse=True)

    for i in address_log[(page - 1) * size: (page - 1) * size + size]:
        # print(i)
        result.append({
            "user_address": i['user_address'],
            "cc_in": str(Web3.fromWei(int(i['cc_in']), "Ether")),
            "cc_out": str(Web3.fromWei(int(i['cc_out']), "Ether")),
            "bnb_in": str(Web3.fromWei(int(i['bnb_in']), "Ether")),
            "bnb_out": str(Web3.fromWei(int(i['bnb_out']), "Ether"))
        })

    return json.dumps({
        "data": result,
        "size": len(address_log),
        "reserve": cc_swap.functions.getReserves().call()[0:2]
    })


# 交易详情 trade_detail
@route_bp.route("/stat/trade/log", methods=['POST'])
def trade_log():
    data = request.json
    start = int(data['start'])
    end = int(data['end'])
    latest_block = w3.eth.get_block("latest")
    latest_block_ts = int(latest_block['timestamp'])
    latest_block_number = latest_block['number']
    if "page" not in data:
        data.update({"page": 1})
    if "size" not in data:
        data.update({"size": 10})
    page = data['page']
    size = data['size']
    print(end, latest_block_ts)
    end = min(end, latest_block_ts)

    start_block = int(get_block_by_ts(start))
    end_block = int(get_block_by_ts(end))
    print(start_block, end_block)

    swap_logs = get_cc_logs_by_block(start_block, end_block)
    in_address = data['in_address']
    not_address = data['not_address']
    address_type = data['address_type']

    result = []
    buy_list = []
    sell_list = []
    result_out = []
    buy_list_out = []
    sell_list_out = []
    buyer_cc_in = 0
    buyer_bnb_out = 0
    seller_cc_out = 0
    seller_bnb_in = 0
    if len(address_type) > 0:
        swap_logs = list(filter(lambda x: x['tag'] in address_type, swap_logs))
    for swap_log in swap_logs:
        in_flag = True
        if len(in_address) > 0:
            if swap_log['user_address'] in in_address:
                in_flag = True
            else:
                in_flag = False
        if len(not_address) > 0:
            if swap_log['user_address'] in not_address:
                in_flag = False
        if in_flag:
            result.append(swap_log)
            result_out.append(
                {'block': swap_log['block_number'],
                 'ts': latest_block_ts - (latest_block_number - swap_log['block_number']) * 3,
                 'tx': swap_log['tx_hash'],
                 'am0i': str(Web3.fromWei(int(swap_log['cc_in']), "Ether")),
                 'am0o': str(Web3.fromWei(int(swap_log['cc_out']), "Ether")),
                 'am1i': str(Web3.fromWei(int(swap_log['bnb_in']), "Ether")),
                 'am1o': str(Web3.fromWei(int(swap_log['bnb_out']), "Ether")),
                 "address_type": swap_log['tag'],
                 'address': swap_log['user_address']}
            )
            if int(swap_log['cc_in']) > 0:
                buy_list.append(swap_log)
                buy_list_out.append(
                    {'block': swap_log['block_number'],
                     'ts': latest_block_ts - (latest_block_number - swap_log['block_number']) * 3,
                     'tx': swap_log['tx_hash'],
                     'am0i': str(Web3.fromWei(int(swap_log['cc_in']), "Ether")),
                     'am0o': str(Web3.fromWei(int(swap_log['cc_out']), "Ether")),
                     'am1i': str(Web3.fromWei(int(swap_log['bnb_in']), "Ether")),
                     'am1o': str(Web3.fromWei(int(swap_log['bnb_out']), "Ether")),
                     "address_type": swap_log['tag'],
                     'address': swap_log['user_address']}
                )
            if int(swap_log['cc_out']) > 0:
                sell_list.append(swap_log)
                sell_list_out.append(
                    {'block': swap_log['block_number'],
                     'ts': latest_block_ts - (latest_block_number - swap_log['block_number']) * 3,
                     'tx': swap_log['tx_hash'],
                     'am0i': str(Web3.fromWei(int(swap_log['cc_in']), "Ether")),
                     'am0o': str(Web3.fromWei(int(swap_log['cc_out']), "Ether")),
                     'am1i': str(Web3.fromWei(int(swap_log['bnb_in']), "Ether")),
                     'am1o': str(Web3.fromWei(int(swap_log['bnb_out']), "Ether")),
                     "address_type": swap_log['tag'],
                     'address': swap_log['user_address']}
                )

    for i in buy_list:
        buyer_cc_in += int(i['cc_in'])
        buyer_bnb_out += int(i['bnb_out'])
    for i in sell_list:
        seller_bnb_in += int(i['bnb_in'])
        seller_cc_out += int(i['cc_out'])

    return json.dumps(
        {"result": result_out[(page - 1) * size: (page - 1) * size + size],
         "result_size": len(result_out),
         "buy_list": buy_list_out[(page - 1) * size: (page - 1) * size + size],
         "buy_list_size": len(buy_list),
         "sell_list": sell_list_out[(page - 1) * size: (page - 1) * size + size],
         "sell_list_size": len(sell_list),
         "buyer_cc_in": str(Web3.fromWei(buyer_cc_in, "Ether")),
         "buyer_bnb_out": str(Web3.fromWei(buyer_bnb_out, "Ether")),
         "seller_bnb_in": str(Web3.fromWei(seller_bnb_in, "Ether")),
         "seller_cc_out": str(Web3.fromWei(seller_cc_out, "Ether")),
         "latest_ts": latest_block_ts,
         "latest_number": latest_block_number
         }
    )


# 持有cc详情 tags: maker, lock, blind_box, recycle, presale,
@route_bp.route("/stat/cc/holder/detail", methods=['POST'])
def cc_holder_detail():
    data = request.json
    tags = data['tags']
    page = data["page"]
    size = data["size"]
    address_list = data['address_list']
    cc_holder = get_cc_holder()
    if len(tags) > 0:
        cc_holder = list(filter(lambda x: x['tag'] in tags, cc_holder))
    if len(address_list) > 0:
        address_list = list(map(lambda x: x.lower(), address_list))
        cc_holder = list(filter(lambda x: x['id'] in address_list, cc_holder))

    count = len(cc_holder)
    balance_sum = sum(list(map(lambda x: int(x['balance']), cc_holder)))
    result = cc_holder[(page - 1) * size: (page - 1) * size + size]

    return json.dumps({
        "result": json.loads(json.dumps(result, cls=DecimalEncode)),
        "size": count,
        "balance_sum": balance_sum,
    })


# 给持有cc的地址增加标签
@route_bp.route("/cc/holder/tag", methods=['POST'])
def cc_holder_tag():
    data = request.json
    address = data['address']
    tag = data['tag']
    add_cc_holder_tag(address.lower(), tag)
    return "success"


@route_bp.route("/cc/holder/tags", methods=['POST'])
def cc_holder_tags():
    data = request.json
    address_list = data['address_list']
    if len(address_list) > 0:
        address_list = list(map(lambda x: x.lower(), address_list))
    tag = data['tag']
    for address in address_list:
        add_cc_holder_tag(address, tag)
    return "success"


# maker, lock, blind_box, recycle, presale, operator
@route_bp.route("/stat/cc/holderbytag", methods=['GET'])
def stat_cc_holder_tags():
    result = get_cc_holder_group_by_tag()
    obj = {

    }
    for item in result:
        obj[item['tag']] = int(item['s'])
    return json.dumps(obj)
