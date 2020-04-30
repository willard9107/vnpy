
DROP TABLE IF EXISTS `trading_date`;
CREATE TABLE `trading_date` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `t_date` date DEFAULT NULL,
  `is_open` tinyint(1) DEFAULT 0 COMMENT '是否开市 0:不开  1:开',
  `create_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_t_date` (`t_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交易日期表';

DROP TABLE IF EXISTS `instrument`;
CREATE TABLE `instrument` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `order_book_id` varchar(16) not null COMMENT '合约id',
  `order_book_symbol` varchar(8) not null COMMENT '合约标的名称',
  `symbol` varchar(32) not null COMMENT '合约名称',
  `listed_date` date not null COMMENT '上市时间',
  `de_listed_date` date not null COMMENT '退市时间',
  `maturity_date` date not null COMMENT '交割时间',
  `exchange` varchar(8) not null COMMENT '交易所',
  `margin_rate` varchar(8) not null COMMENT '保证金比例',
  `contract_multiplier` int not null COMMENT '合约乘数',
  `trading_hours` varchar(128)  COMMENT '日内交易时间',
  `create_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  unique key `idx_order_book_id` (`order_book_id`),
  index `idx_listed_date_de` (`listed_date`,`de_listed_date`),
  index `idx_order_book_symbol` (`order_book_symbol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='合约表';







