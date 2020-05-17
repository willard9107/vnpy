DROP TABLE IF EXISTS `trading_date`;
CREATE TABLE `trading_date`
(
    `id`          bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增id',
    `t_date`      date                         DEFAULT NULL,
    `is_open`     tinyint(1)                   DEFAULT 0 COMMENT '是否开市 0:不开  1:开',
    `create_time` timestamp(3)        NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_t_date` (`t_date`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='交易日期表';

DROP TABLE IF EXISTS `instrument`;
CREATE TABLE `instrument`
(
    `id`                  bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增id',
    `order_book_id`       varchar(16)         not null COMMENT '合约id',
    `order_book_symbol`   varchar(8)          not null COMMENT '合约标的名称',
    `symbol`              varchar(32)         not null COMMENT '合约名称',
    `listed_date`         date                not null COMMENT '上市时间',
    `de_listed_date`      date                not null COMMENT '退市时间',
    `maturity_date`       date                not null COMMENT '交割时间',
    `exchange`            varchar(8)          not null COMMENT '交易所',
    `margin_rate`         varchar(8)          not null COMMENT '保证金比例',
    `contract_multiplier` int                 not null COMMENT '合约乘数',
    `trading_hours`       varchar(128) COMMENT '日内交易时间',
    `create_time`         timestamp(3)        NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    PRIMARY KEY (`id`),
    unique key `idx_order_book_id` (`order_book_id`),
    index `idx_listed_date_de` (`listed_date`, `de_listed_date`),
    index `idx_order_book_symbol` (`order_book_symbol`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='合约表';

DROP TABLE IF EXISTS `daily_bar`;
CREATE TABLE `daily_bar`
(
    `id`            bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增id',
    `order_book_id` varchar(16)         not null COMMENT '合约id',
    `date_time`     date                not null COMMENT '当前交易日期',
    `volume`        int                 not null COMMENT '成交量',
    `open_interest` int                 not null COMMENT '持仓量',
    `open_price`    float               not null COMMENT '开盘价',
    `close_price`   float               not null COMMENT '收盘价',
    `high_price`    float               not null COMMENT '最高价',
    `low_price`     float               not null COMMENT '最低价',
    `settle_price`  float               not null COMMENT '结算价',
    `create_time`   timestamp(3)        NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_book_id_date_time` (`order_book_id`, `date_time`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='日K线表';

DROP TABLE IF EXISTS `open_interest_holding`;
CREATE TABLE `open_interest_holding`
(
    `id`            bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增id',
    `order_book_id` varchar(16)         not null COMMENT '合约id',
    `date_time`     date                not null COMMENT '当前交易日期',
    `broker`        varchar(32)         not null COMMENT '期货公司',
    `data_type`     tinyint(1)          not null COMMENT '数据类型, 0 成交量；1 多单手数；2 空单手数',
    `volume`        int                 not null COMMENT '数量，具体含义取决于数据类型',
    `volume_change` int                 not null COMMENT '数量较上一天的增减',
    `rank`          int                 not null COMMENT '排名',
    `create_time`   timestamp(3)        NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    PRIMARY KEY (`id`),
    index `idx_book_id_date_time_type` (`order_book_id`, `date_time`, `data_type`),
    UNIQUE KEY `idx_book_id_date_time_type_broker` (`order_book_id`, `date_time`, `data_type`, `broker`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='持仓龙虎榜';

create table tick_a1601
(
    datetime      bigint not null
        primary key,
    volume        float  not null,
    open_interest float  not null,
    last_price    float  not null,
    last_volume   float  not null,
    high_price    float  not null,
    low_price     float  not null,
    bid_price_1   float  not null,
    bid_price_2   float  null,
    bid_price_3   float  null,
    bid_price_4   float  null,
    bid_price_5   float  null,
    ask_price_1   float  not null,
    ask_price_2   float  null,
    ask_price_3   float  null,
    ask_price_4   float  null,
    ask_price_5   float  null,
    bid_volume_1  float  not null,
    bid_volume_2  float  null,
    bid_volume_3  float  null,
    bid_volume_4  float  null,
    bid_volume_5  float  null,
    ask_volume_1  float  not null,
    ask_volume_2  float  null,
    ask_volume_3  float  null,
    ask_volume_4  float  null,
    ask_volume_5  float  null
) charset = utf8mb4;







