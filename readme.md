### 根据监听到的日志事件，找方法

pancake 合约 上面的按照swap日志计算成本

预售就按照 preSale合约 的 PreSale日志的

盲盒的bindBoxCow 的Transfer日志

盲盒回收合约的

#### cc币转移的方式
1. 开盲盒 随机盲盒
2. 预售
3. pancake
4. 回收
5. 普通转账




DROP TABLE c_address;
CREATE TABLE c_address (
'id'	integer PRIMARY KEY AUTOINCREMENT,
'name' char,
'address' char,
'tag' char,
'latest_block' number
);
CREATE INDEX tag on c_address (tag);

DROP TABLE cc_logs;
CREATE TABLE cc_logs (
	'id' integer PRIMARY KEY AUTOINCREMENT,
	'block_number' bigint,
	'tx_hash' char,
	'log_index' bigint,
	'cc_in' text,
	'cc_out' text,
	'bnb_in' text,
	'bnb_out' text,
	'user_address' char,
	'contract_address' char,
	'tag' char
);
CREATE INDEX block_number_contract_address on cc_logs (block_number, contract_address);
CREATE INDEX tx_hash_log_index on cc_logs (tx_hash, log_index);

DROP TABLE w_address;
CREATE TABLE w_address (
'id'	integer PRIMARY KEY AUTOINCREMENT,
'address' char,
'name' char,
'bnb' text,
'cc' text
);

DROP TABLE cc_manual_logs;
CREATE TABLE cc_manual_logs(
	'id' integer PRIMARY KEY AUTOINCREMENT,
	'create_time' text,
	'bnb_in' text,
	'bnb_out' text,
	'cc_in' text,
	'cc_out' text,
	'note' text
);

CREATE TABLE config(
	'key' text,
	'value' text
)