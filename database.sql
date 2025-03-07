CREATE DATABASE IF NOT EXISTS sales_db;

USE sales_db;

CREATE TABLE IF NOT EXISTS operators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'operator'
);

CREATE TABLE IF NOT EXISTS sales (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
  barcode VARCHAR(50) NOT NULL COMMENT '商品条码',
  product_name VARCHAR(100) NOT NULL COMMENT '商品名称',
  sales_quantity INT NOT NULL COMMENT '销售数量',
  sales_price DECIMAL(10,2) NOT NULL COMMENT '销售单价',
  sales_amount DECIMAL(10,2) NOT NULL COMMENT '销售金额',
  deduction_rate DECIMAL(5,2) NOT NULL COMMENT '扣点比例',
  deduction_amount DECIMAL(10,2) NOT NULL COMMENT '扣点金额',
  settlement_amount DECIMAL(10,2) NOT NULL COMMENT '结算金额',
  years_month CHAR(7) NOT NULL COMMENT '年和月',
  import_time DATETIME NOT NULL COMMENT '导入时间',
  client_name VARCHAR(100) DEFAULT NULL COMMENT '客户名称',
  salesperson VARCHAR(50) DEFAULT NULL COMMENT '业务员',
  operator VARCHAR(50) DEFAULT NULL COMMENT '操作员',
  store_id INT DEFAULT NULL COMMENT '门店ID',
  KEY store_id (store_id) COMMENT '门店ID外键约束',
  CONSTRAINT sales_ibfk_1 FOREIGN KEY (store_id) REFERENCES stores (id)
)COMMENT '销售数据记录表';


INSERT INTO operators (username, password, role) 
VALUES ('admin', '1234', 'admin');
