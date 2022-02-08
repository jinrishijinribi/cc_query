import pymysql

# conn = pymysql.connect(
#     host="rm-6we8u0l05o7z6tf76jo.mysql.japan.rds.aliyuncs.com",
#     port=3306,
#     user="cc_query",
#     password="@tianli123456TL",
#     db="cc_query",
#     charset="utf8"
# )


def get_conn():
    return pymysql.connect(
        host="rm-6we8u0l05o7z6tf76jo.mysql.japan.rds.aliyuncs.com",
        port=3306,
        user="cc_query",
        password="@tianli123456TL",
        db="cc_query",
        charset="utf8"
    )


# def is_connected():
#     print(conn.ping())


# cursor = connection.cursor()
def save_w_address(address, name, bnb, cc):
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = f' INSERT INTO w_address (address, name, bnb, ' \
          f' cc ) VALUES ("{address}", "{name}", {bnb}, "{cc}")'
    print(txt)
    cur.execute(txt)
    conn.commit()
    cur.close()


def save_c_address(address, name, tag, latest_block):
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = f' INSERT INTO c_address (address, name, tag, latest_block ' \
          f' ) VALUES ("{address}", "{name}", "{tag}", {latest_block})'
    print(txt)
    cur.execute(txt)
    conn.commit()
    cur.close()


def del_c_address(w_id):
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = f'''delete from c_address where id = {w_id}'''
    print(txt)
    cur.execute(txt)
    conn.commit()
    cur.close()


def del_w_address(w_id):
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = f'''delete from w_address where id = {w_id}'''
    print(txt)
    cur.execute(txt)
    conn.commit()
    cur.close()


def save_cc_manual_logs(create_time, bnb_in, bnb_out, cc_in, cc_out, note):
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = f'''INSERT INTO cc_manual_logs (create_time, bnb_in, bnb_out, cc_in, cc_out, note) 
            VALUES ("{create_time}", "{bnb_in}", "{bnb_out}", "{cc_in}", "{cc_out}", "{note}")'''
    print(txt)
    cur.execute(txt)
    conn.commit()
    cur.close()


def del_cc_manual_logs(c_id):
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = f'''delete from cc_manual_logs where id = {c_id}'''
    print(txt)
    cur.execute(txt)
    conn.commit()
    cur.close()


def get_cc_manual_logs():
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = 'select * from cc_manual_logs'
    cur.execute(txt)
    return cur.fetchall()


def get_charge_bnb_cc():
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = 'select COALESCE(sum(bnb_in),0) as bnb_in, COALESCE(sum(cc_out),0) as cc_out from cc_manual_logs'
    cur.execute(txt)
    return cur.fetchall()


def get_my_bnb_cc():
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = 'select COALESCE(sum(bnb),0) as bnb, COALESCE(sum(cc),0) as cc from w_address'
    cur.execute(txt)
    return cur.fetchall()


def get_cc_logs_by_address(block_from, block_to):
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = f'''select user_address, sum(cc_in) as cc_in, sum(cc_out) as cc_out, sum(bnb_in) as bnb_in, sum(bnb_out) as bnb_out ''' \
          f''' from cc_logs where block_number >= {block_from} and block_number < {block_to} group by user_address  '''
    cur.execute(txt)
    return cur.fetchall()


def get_cc_logs_by_block(block_from, block_to):
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = f'select * from cc_logs where block_number >= {block_from} and block_number < {block_to}'
    cur.execute(txt)
    return cur.fetchall()


# def get_config(key):
#     cur = conn.cursor(pymysql.cursors.DictCursor)
#     txt = f'select * from config where key = "{key}"'
#     cur.execute(txt)
#     return cur.fetchall()
#
#
# def set_config(key, value):
#     cur = conn.cursor(pymysql.cursors.DictCursor)
#     txt = f'update config set value = "{value}" where key = "{key}"'
#     cur.execute(txt)
#     conn.commit()
#     cur.close()

def save_cc_logs(block_number, tx_hash, log_index, cc_in, cc_out, bnb_in, bnb_out, user_address, contract_address, tag):
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = f' INSERT INTO cc_logs (block_number, tx_hash, log_index, ' \
          f' cc_in, cc_out, bnb_in, bnb_out, user_address, contract_address, tag) VALUES ' \
          f' ({block_number}, "{tx_hash}", {log_index}, "{cc_in}", "{cc_out}", "{bnb_in}", "{bnb_out}", ' \
          f' "{user_address}", "{contract_address}", "{tag}")'
    print(txt)
    cur.execute(txt)
    conn.commit()
    cur.close()


def save_w_address(address, name, bnb, cc):
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = f' INSERT INTO w_address (address, name, bnb, ' \
          f' cc ) VALUES ({address}, "{name}", {bnb}, "{cc}")'
    print(txt)
    cur.execute(txt)
    conn.commit()
    cur.close()


def update_w_address(address, bnb, cc):
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = f' UPDATE w_address set bnb = "{bnb}", cc = "{cc}" where address = "{address}" '
    print(txt)
    cur.execute(txt)
    conn.commit()
    cur.close()


def get_cc_log():
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = 'select * from cc_logs'
    cur.execute(txt)
    return cur.fetchall()


def get_w_address():
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = 'select * from w_address'
    cur.execute(txt)
    return cur.fetchall()


def get_c_address():
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = 'select * from c_address'
    cur.execute(txt)
    return cur.fetchall()


def delete_w_address(c_id):
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = f'delete from w_address where id = {c_id}'
    cur.execute(txt)
    return cur.fetchall()


# tag : pre_sale, pancake, bind_box, recycle
def get_contract():
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = 'select * from c_address'
    cur.execute(txt)
    my_contracts = cur.fetchall()
    return my_contracts


def update_contract_block(address_id, latest_block):
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    txt = f'update c_address set latest_block = "{latest_block}" where id = {address_id}'
    cur.execute(txt)
    conn.commit()
    cur.close()
