CREATE DATABASE IF NOT EXISTS sales_db;

USE sales_db;

CREATE TABLE IF NOT EXISTS operators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'operator'
);

CREATE TABLE IF NOT EXISTS sales_data (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    product_barcode VARCHAR(50) NOT NULL COMMENT '商品条码',
    product_name VARCHAR(255) NOT NULL COMMENT '商品名称',
    sales_quantity INT NOT NULL COMMENT '销售数量',
    sales_price DECIMAL(10, 2) NOT NULL COMMENT '销售单价',
    sales_amount DECIMAL(10, 2) NOT NULL COMMENT '销售金额',
    deduction_rate DECIMAL(5, 2) NOT NULL COMMENT '扣点比例',
    deduction_amount DECIMAL(10, 2) NOT NULL COMMENT '扣点金额',
    settlement_amount DECIMAL(10, 2) NOT NULL COMMENT '结算金额',
    YEAR_MONTH  VARCHAR(7) NOT NULL COMMENT '年和月',
    import_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '导入时间',
    customer_name VARCHAR(255) NOT NULL COMMENT '客户名称',
    salesperson VARCHAR(100) NOT NULL COMMENT '业务员',
    operator VARCHAR(100) NOT NULL COMMENT '操作员'
) COMMENT '销售数据记录表';

INSERT INTO operators (username, password, role) 
VALUES ('admin', 'admin123', 'admin');
