# import sqlite3
#
#
# conn = sqlite3.connect('cc_action.db', check_same_thread=False)
#
#
# def dict_factory(cursor, row):
#     d = {}
#     for idx, col in enumerate(cursor.description):
#         d[col[0]] = row[idx]
#     return d
#
#
# conn.row_factory = dict_factory
#
#
# def save_w_address(address, name, bnb, cc):
#     cur = conn.cursor()
#     txt = f' INSERT INTO w_address (address, name, bnb, ' \
#           f' cc ) VALUES ("{address}", "{name}", {bnb}, "{cc}")'
#     print(txt)
#     cur.execute(txt)
#     conn.commit()
#     cur.close()
#
#
# def save_c_address(address, name, tag, latest_block):
#     cur = conn.cursor()
#     txt = f' INSERT INTO c_address (address, name, tag, latest_block ' \
#           f' ) VALUES ("{address}", "{name}", "{tag}", {latest_block})'
#     print(txt)
#     cur.execute(txt)
#     conn.commit()
#     cur.close()
#
#
# def del_c_address(w_id):
#     cur = conn.cursor()
#     txt = f'''delete from c_address where id = {w_id}'''
#     print(txt)
#     cur.execute(txt)
#     conn.commit()
#     cur.close()
#
#
# def del_w_address(w_id):
#     cur = conn.cursor()
#     txt = f'''delete from w_address where id = {w_id}'''
#     print(txt)
#     cur.execute(txt)
#     conn.commit()
#     cur.close()
#
#
# def save_cc_manual_logs(create_time, bnb_in, bnb_out, cc_in, cc_out, note):
#     cur = conn.cursor()
#     txt = f'''INSERT INTO cc_manual_logs (create_time, bnb_in, bnb_out, cc_in, cc_out, note)
#             VALUES ("{create_time}", "{bnb_in}", "{bnb_out}", "{cc_in}", "{cc_out}", "{note}")'''
#     print(txt)
#     cur.execute(txt)
#     conn.commit()
#     cur.close()
#
#
# def del_cc_manual_logs(c_id):
#     cur = conn.cursor()
#     txt = f'''delete from cc_manual_logs where id = {c_id}'''
#     print(txt)
#     cur.execute(txt)
#     conn.commit()
#     cur.close()
#
#
# def get_cc_manual_logs():
#     cur = conn.cursor()
#     txt = 'select * from cc_manual_logs'
#     cur.execute(txt)
#     return cur.fetchall()
#
#
# def get_charge_bnb_cc():
#     cur = conn.cursor()
#     txt = 'select sum(bnb_in) as bnb_in, sum(cc_out) as cc_out from cc_manual_logs'
#     cur.execute(txt)
#     return cur.fetchall()
#
#
# def get_my_bnb_cc():
#     cur = conn.cursor()
#     txt = 'select sum(bnb) as bnb, sum(cc) as cc from w_address'
#     cur.execute(txt)
#     return cur.fetchall()
#
#
# def get_cc_logs_by_address(block_from, block_to):
#     cur = conn.cursor()
#     txt = f'''select user_address, sum(cc_in) as cc_in, sum(cc_out) as cc_out, sum(bnb_in) as bnb_in, sum(bnb_out) as bnb_out ''' \
#           f''' from cc_logs where block_number >= {block_from} and block_number < {block_to} group by user_address  '''
#     cur.execute(txt)
#     return cur.fetchall()
#
#
# def get_cc_logs_by_block(block_from, block_to):
#     cur = conn.cursor()
#     txt = f'select * from cc_logs where block_number >= {block_from} and block_number < {block_to}'
#     cur.execute(txt)
#     return cur.fetchall()
#
#
# def get_config(key):
#     cur = conn.cursor()
#     txt = f'select * from config where key = "{key}"'
#     cur.execute(txt)
#     return cur.fetchall()
#
#
# def set_config(key, value):
#     cur = conn.cursor()
#     txt = f'update config set value = "{value}" where key = "{key}"'
#     cur.execute(txt)
#     conn.commit()
#     cur.close()
