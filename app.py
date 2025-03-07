import os
from flask import Flask, render_template, request, redirect, url_for, session, send_file, make_response
from flask_mysqldb import MySQL 
import pandas as pd # type: ignore
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 从配置文件加载
app.config.from_pyfile('config.py')

# 配置数据库连接池参数
app.config.update({
    'MYSQL_CONNECT_TIMEOUT': 30,
    'MYSQL_POOL_SIZE': 20,
    'MYSQL_POOL_NAME': 'main_pool',
    'MYSQL_AUTOCOMMIT': True
})

mysql = MySQL(app)

# 数据库初始化
def init_db():
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                role ENUM('admin', 'operator') NOT NULL,
                login_attempts INT DEFAULT 0,
                last_login DATETIME,
                status ENUM('active', 'locked') DEFAULT 'active'
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS stores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                store_name VARCHAR(100) NOT NULL,
                deduction_rate DECIMAL(5,2) NOT NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INT AUTO_INCREMENT PRIMARY KEY,
                barcode VARCHAR(50) NOT NULL,
                product_name VARCHAR(100) NOT NULL,
                quantity INT NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                deduction_rate DECIMAL(5,2) NOT NULL,
                deduction_amount DECIMAL(10,2) NOT NULL,
                settlement_amount DECIMAL(10,2) NOT NULL,
                `years_month` CHAR(7) NOT NULL,
                `import_time` DATETIME NOT NULL,
                client_name VARCHAR(100),
                salesperson VARCHAR(50),
                `operator` VARCHAR(50),
                store_id INT,
                FOREIGN KEY (store_id) REFERENCES stores(id)
            )
        ''')
        
        # 插入测试用户
        # test_users = [
        #     ('admin', generate_password_hash('1234'), 'admin'),
        #     ('operator1', generate_password_hash('Operator1!'), 'operator')
        # ]
        # cur.executemany(
        #     "INSERT IGNORE INTO users (username, password, role) VALUES (%s, %s, %s)",
        #     test_users
        # )
        # mysql.connection.commit()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('error.html', message='用户名和密码不能为空')
            
        try:
            cur = mysql.connection.cursor()
            # 先检查登录尝试次数
            cur.execute("""
                SELECT id, password, role, login_attempts, last_login, status 
                FROM users 
                WHERE username = %s
                AND status = 'active'
                AND (login_attempts < 5 OR TIMESTAMPDIFF(MINUTE, last_login, NOW()) >= 30)
            """, (username,))
            user = cur.fetchone()

            # cur.execute("""
            #     SELECT id, password, 
            #     FROM operators
            #     WHERE username = %s
            #     """, (username,))
            # opuser = cur.fetchone()
            
            if not user:
                return render_template('error.html', message='账户已锁定或用户名不存在，请30分钟后再试')
                
            if check_password_hash(user['password'], password):  # 修正密码验证参数顺序
                # 重置登录尝试次数
                cur.execute("""
                    UPDATE users 
                    SET login_attempts = 0, last_login = NOW() 
                    WHERE id = %s
                """, (user['id'],))
                mysql.connection.commit()
                
                session.permanent = True
                session['user_id'] = user['id']
                session['username'] = username
                session['role'] = user['role']
                session['ip'] = request.remote_addr
                
                # 根据角色跳转不同页面
                if user['role'] == 'admin':
                    return redirect(url_for('dashboard'))
                return redirect(url_for('dashboard'))
            else:
                # 增加登录尝试次数
                cur.execute("""
                    UPDATE users 
                    SET login_attempts = login_attempts + 1, last_login = NOW() 
                    WHERE id = %s
                """, (user['id'],))
                mysql.connection.commit()
                remaining_attempts = 4 - user['login_attempts']
                return render_template('error.html', 
                    message=f'登录失败，剩余尝试次数：{remaining_attempts}次，连续5次失败将锁定账户')
                
        except Exception as e:
            mysql.connection.rollback()
            return render_template('error.html', message='登录异常：' + str(e))
        finally:
            cur.close()
            
    # 添加安全头
    response = make_response(render_template('login.html'))
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        # 查询销售数据
        cur.execute("""
            SELECT 
                sd.barcode AS '商品条码',
                sd.product_name AS '商品名称',
                sd.sales_quantity AS '销售数量',
                sd.sales_price AS '销售单价',
                sd.sales_amount AS '销售金额',
                sd.deduction_rate AS '扣点比例',
                sd.deduction_amount AS '扣点金额',
                sd.settlement_amount AS '结算金额',
                sd.years_month AS '年月',
                sd.import_time AS '导入时间',
                sd.client_name AS '客户名称',
                sd.salesperson AS '业务员',
                sd.operator AS '操作员'
            FROM sales sd
            JOIN stores ON sd.store_id = stores.id
            ORDER BY import_time DESC
            LIMIT 1000
        """)
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]  # 获取字段名称
        
        return render_template('dashboard.html', 
                             data=data,
                             columns=columns,
                             role=session['role'])
    
    except Exception as e:
        return render_template('error.html', message='数据加载失败: ' + str(e))
    finally:
        cur.close()

@app.route('/import', methods=['GET', 'POST'])
def import_data():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                return render_template('error.html', message='请选择要上传的文件')
            
            file = request.files['file']
            if file.filename == '':
                return render_template('error.html', message='未选择文件')
            
            if not file.filename.endswith(('.xls', '.xlsx')):
                return render_template('error.html', message='仅支持Excel文件')
            
            # 读取Excel数据
            df = pd.read_excel(file)
            
            # 验证必要列
            required_columns = ['条码', '商品名称', '数量', '单价', '扣率', '客户名称', '业务员', '年月']
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                return render_template('error.html', message=f'缺少必要列: {", ".join(missing)}')
            
            # 转换数据
            current_time = datetime.now()
            data_to_insert = []
            for _, row in df.iterrows():
                # 验证门店信息
                cur = mysql.connection.cursor()
                cur.execute("""
                    SELECT s.id, s.deduction_rate 
                    FROM stores s
                    WHERE LOWER(s.store_name) = LOWER(%s) 
                    LIMIT 1
                """, (row['客户名称'].strip(),))
                store = cur.fetchone()
                if not store:
                    return render_template('error.html', message=f'未找到门店: {row["客户名称"]}')
                
                # 数据验证和转换
                try:
                    quantity = int(row['数量'])
                    unit_price = float(row['单价'])
                    deduction_rate = float(row['扣率'])
                except ValueError as e:
                    return render_template('error.html', message=f'数据转换失败: {str(e)}')
                total_amount = quantity * unit_price
                deduction_amount = total_amount * deduction_rate / 100
                settlement_amount = total_amount - deduction_amount
                
                data_to_insert.append((
                    row['条码'],
                    row['商品名称'],
                    quantity,
                    unit_price,
                    total_amount,
                    deduction_rate,
                    deduction_amount,
                    settlement_amount,
                    row['年月'],
                    current_time,
                    row['客户名称'],
                    row['业务员'],
                    session['username'],
                    store['id']
                ))
            
            # 批量插入数据库
            cur = mysql.connection.cursor()
            cur.executemany('''
                INSERT INTO sales sd(
                    sd.barcode, sd.product_name, sd.sales_quantity, sd.sales_price, sd.sales_amount,
                    sd.deduction_rate, sd.deduction_amount, sd.settlement_amount,
                    sd.years_month, sd.import_time, sd.client_name, sd.salesperson, sd.operator, sd.store_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', data_to_insert)
            
            mysql.connection.commit()
            return redirect(url_for('export_data'))
            
        except pd.errors.EmptyDataError:
            return render_template('error.html', message='Excel文件内容为空')
        except pd.errors.ParserError:
            return render_template('error.html', message='Excel文件解析失败')
        except Exception as e:
            mysql.connection.rollback()
            return render_template('error.html', message=f'导入失败: {str(e)}')
    
    return render_template('import.html')

@app.route('/export', methods=['GET', 'POST'])
def export_data():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # 获取查询参数
        store_id = request.form.get('store_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # 构建基础查询
        query = """
            SELECT sd.id, sd.barcode, sd.product_name, sd.quantity, sd.unit_price, sd.total_amount,
                   sd.deduction_rate, sd.deduction_amount, sd.settlement_amount,
                   sd.years_month, sd.import_time, st.store_name, sd.operator
            FROM sales sd
            JOIN stores st ON sd.store_id = st.id
            WHERE 1=1
        """
        params = []
        
        # 添加过滤条件
        if store_id:
            query += " AND sd.store_id = %s"
            params.append(store_id)
        if start_date and end_date:
            query += " AND sd.import_time BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        # 执行查询
        cursor = mysql.connection.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()

        # 创建DataFrame
        df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])
        
        # 生成Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        
        output.seek(0)
        return send_file(output, 
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        download_name='sales_export.xlsx',
                        as_attachment=True)

    # 获取门店列表用于筛选
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, store_name FROM stores")
    stores = cursor.fetchall()
    cursor.close()
    
    return render_template('export.html', stores=stores)

if __name__ == '__main__':
    # init_db()
    app.run(debug=True)
