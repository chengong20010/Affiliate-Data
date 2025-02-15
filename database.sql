-- 创建名为 sales_data 的数据库，如果该数据库不存在的话
CREATE DATABASE IF NOT EXISTS sales_data;

-- 使用 sales_data 数据库
USE sales_data;

-- 用户表
-- 该表用于存储系统用户的相关信息
-- id: 用户的唯一标识，自增整数类型，作为主键
-- username: 用户名，长度不超过 50 个字符，必须唯一且不能为空
-- password_hash: 用户密码的哈希值，长度为 128 个字符，不能为空
-- is_admin: 是否为管理员，布尔类型，默认为 false
-- created_at: 用户创建时间，日期时间类型，默认为当前时间
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 门店表
-- 该表用于存储门店的相关信息
-- id: 门店的唯一标识，自增整数类型，作为主键
-- store_name: 门店名称，长度不超过 100 个字符，不能为空
-- deduction_rate: 扣点率，小数类型，精度为 5 位，小数位为 4 位，默认为 0.0000
-- contact_info: 门店联系信息，文本类型
-- created_at: 门店创建时间，日期时间类型，默认为当前时间
CREATE TABLE stores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    deduction_rate DECIMAL(5,4) NOT NULL DEFAULT 0.0000,
    contact_info TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 商品表 
-- 该表用于存储商品的相关信息
-- barcode: 商品条形码，长度不超过 20 个字符，作为主键
-- product_name: 商品名称，长度不超过 255 个字符，不能为空
-- created_at: 商品创建时间，日期时间类型，默认为当前时间
CREATE TABLE products (
    barcode VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 销售记录表
-- 该表用于记录商品的销售信息
-- id: 销售记录的唯一标识，自增整数类型，作为主键
-- barcode: 商品条形码，长度不超过 20 个字符，不能为空
-- product_name: 商品名称，长度不超过 255 个字符，不能为空
-- quantity: 销售数量，整数类型，不能为空
-- unit_price: 商品单价，小数类型，精度为 10 位，小数位为 2 位，不能为空
-- total_amount: 销售总金额，小数类型，精度为 10 位，小数位为 2 位，不能为空
-- deduction_rate: 扣点率，小数类型，精度为 5 位，小数位为 4 位，不能为空
-- deduction_amount: 扣点金额，小数类型，精度为 10 位，小数位为 2 位，不能为空
-- settlement_amount: 结算金额，小数类型，精度为 10 位，小数位为 2 位，不能为空
-- year_month: 销售年月，字符类型，长度为 7 个字符，不能为空
-- import_time: 导入时间，日期时间类型，不能为空
-- operator_id: 操作员 ID，整数类型，不能为空，关联 users 表的 id 字段
-- store_id: 门店 ID，整数类型，不能为空，关联 stores 表的 id 字段
CREATE TABLE sales_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    barcode VARCHAR(20) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    deduction_rate DECIMAL(5,4) NOT NULL,
    deduction_amount DECIMAL(10,2) NOT NULL,
    settlement_amount DECIMAL(10,2) NOT NULL,
    year_month CHAR(7) NOT NULL,
    import_time DATETIME NOT NULL,
    operator_id INT NOT NULL,
    store_id INT NOT NULL,
    FOREIGN KEY (operator_id) REFERENCES users(id),
    FOREIGN KEY (store_id) REFERENCES stores(id),
    FOREIGN KEY (barcode) REFERENCES products(barcode)
);

-- 初始化测试数据

-- 插入用户测试数据
-- 插入两条用户记录，分别为管理员和普通操作员
INSERT INTO users (username, password_hash, is_admin) VALUES 
('admin', 'pbkdf2:sha256:260000$xxxxxxxxxxxx', 1),
('operator1', 'pbkdf2:sha256:260000$xxxxxxxxxxxx', 0);

-- 插入门店测试数据
-- 插入三条门店记录，分别为旗舰店、分店 A 和分店 B，并设置相应的扣点率
INSERT INTO stores (store_name, deduction_rate) VALUES
('旗舰店', 0.1200),
('分店A', 0.1000),
('分店B', 0.1500);

-- 插入商品测试数据
-- 插入三条商品记录，分别为商品 A、商品 B 和商品 C，并设置相应的条形码
INSERT INTO products (barcode, product_name) VALUES
('690123456789', '商品A'),
('690123456788', '商品B'),
('690123456787', '商品C');
