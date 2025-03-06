CREATE DATABASE IF NOT EXISTS sales_db;

USE sales_db;

CREATE TABLE IF NOT EXISTS operators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'operator'
);

CREATE TABLE IF NOT EXISTS sales_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    商品条码 VARCHAR(50) NOT NULL,
    商品名称 VARCHAR(255),
    销售数量 INT NOT NULL,
    销售单价 DECIMAL(10,2) NOT NULL,
    销售金额 DECIMAL(10,2) NOT NULL,
    扣点比例 DECIMAL(5,4) NOT NULL,
    扣点金额 DECIMAL(10,2) NOT NULL,
    结算金额 DECIMAL(10,2) NOT NULL,
    年月 DATE NOT NULL,
    导入时间 DATETIME NOT NULL,
    客户名称 VARCHAR(100) NOT NULL,
    业务员 VARCHAR(50) NOT NULL,
    操作员 VARCHAR(50) NOT NULL
);

INSERT INTO operators (username, password, role) 
VALUES ('admin', 'admin123', 'admin');
