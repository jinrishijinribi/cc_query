# from __init__ import db
# import json
# session = db.session
#
#
# def get_cc_logs_a():
#     return session.query(CAddress).all()
#
#
# class CAddress(db.Model):
#     __tablename__ = 'c_address'
#     id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(100))
#     address = db.Column(db.String(100))
#     tag = db.Column(db.String(100))
#     latest_block = db.Column(db.BigInteger)
#     __table_args__ = (
#         db.Index('tag_index', 'tag'),
#     )
#
#     def toJSON(self):
#         return json.dumps(self, default=lambda o: o.__dict__,
#                           sort_keys=True, indent=4)
#
#
# class CcLogs(db.Model):
#     __tablename__ = 'cc_logs'
#     id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
#     block_number = db.Column(db.BigInteger)
#     tx_hash = db.Column(db.String(100))
#     log_index = db.Column(db.BigInteger)
#     cc_in = db.Column(db.BigInteger)
#     cc_out = db.Column(db.BigInteger)
#     bnb_in = db.Column(db.BigInteger)
#     bnb_out = db.Column(db.BigInteger)
#     user_address = db.Column(db.String(100))
#     contract_address = db.Column(db.String(100))
#     tag = db.Column(db.String(100))
#     __table_args__ = (
#         db.Index('block_number_contract_address', 'block_number', 'contract_address'),
#         db.Index('tx_hash_log_index', 'tx_hash', 'log_index'),
#     )
#
#
# class CcManualLogs(db.Model):
#     __tablename__ = 'cc_manual_logs'
#     id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
#     create_time = db.Column(db.String(100))
#     cc_in = db.Column(db.BigInteger)
#     cc_out = db.Column(db.BigInteger)
#     bnb_in = db.Column(db.BigInteger)
#     bnb_out = db.Column(db.BigInteger)
#     note = db.Column(db.String(100))
#
#
# class WAddress(db.Model):
#     __tablename__ = 'w_address'
#     id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
#     address = db.Column(db.String(100))
#     name = db.Column(db.String(100))
#     cc = db.Column(db.BigInteger)
#     bnb = db.Column(db.BigInteger)
