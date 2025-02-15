from flask import Flask, render_template, request, redirect, url_for, send_file, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from openpyxl import load_workbook
import pymysql.cursors
from config import Config
from openpyxl import Workbook
import os
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 数据库连接
def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            if user:
                return User(user_id)
    finally:
        conn.close()
    return None

@app.route('/logout')
@login_required  # 添加登录验证装饰器
def logout():
    logout_user()  # 使用 Flask-Login 的 logout_user 函数
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return redirect(url_for('import_data'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
                user = cursor.fetchone()
                if user and check_password_hash(user['password_hash'], password):
                    login_user(User(user['id']))
                    return redirect(url_for('index'))
        finally:
            conn.close()
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/import', methods=['GET', 'POST'])
@login_required
def import_data():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
            
        file = request.files['file']
        store_id = request.form.get('store_id')
        
        if file.filename == '':
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # 读取Excel文件
            wb = load_workbook(filepath)
            ws = wb.active
            
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    # 获取扣点比例
                    cursor.execute('SELECT deduction_rate FROM stores WHERE id = %s', (store_id,))
                    store = cursor.fetchone()
                    deduction_rate = store['deduction_rate'] if store else 0.0
                    
                    # 处理数据
                    for row in ws.iter_rows(min_row=2, values_only=True):
                        barcode, quantity, unit_price, total = row
                        deduction_amount = total * deduction_rate
                        settlement_amount = total - deduction_amount
                        
                        # 获取商品名称
                        product_name = get_product_name(barcode)  # 需要实现商品查询逻辑
                        
                        cursor.execute('''
                            INSERT INTO sales_records 
                            (barcode, product_name, quantity, unit_price, total_amount, 
                             deduction_rate, deduction_amount, settlement_amount,
                             year_month, import_time, operator_id, store_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            barcode, 
                            product_name,
                            quantity,
                            unit_price,
                            total,
                            deduction_rate,
                            deduction_amount,
                            settlement_amount,
                            datetime.now().strftime('%Y-%m'),
                            datetime.now(),
                            current_user.id,
                            store_id
                        ))
                    conn.commit()
                    flash('数据导入成功')
            except Exception as e:
                conn.rollback()
                flash(f'导入失败: {str(e)}')
            finally:
                conn.close()
            
            return redirect(url_for('import_data'))
    return render_template('import.html')

@app.route('/export')
@login_required
def export_data():
    # 获取查询参数
    store_id = request.args.get('store_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # 构建基础查询
    query = '''
        SELECT s.barcode, p.name as product_name, s.quantity, 
               s.unit_price, s.total_amount, s.deduction_rate,
               s.deduction_amount, s.settlement_amount,
               s.year_month, s.import_time, 
               st.name as store_name, u.username as operator
        FROM sales_records s
        LEFT JOIN products p ON s.barcode = p.barcode
        LEFT JOIN stores st ON s.store_id = st.id
        LEFT JOIN users u ON s.operator_id = u.id
        WHERE 1=1
    '''
    params = []
    
    # 添加过滤条件
    if store_id:
        query += " AND s.store_id = %s"
        params.append(store_id)
    if start_date and end_date:
        query += " AND s.import_time BETWEEN %s AND %s" 
        params.extend([start_date, end_date])

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()

            # 创建Excel文件
            wb = Workbook()
            ws = wb.active
            ws.title = "销售数据"
            
            # 添加表头
            headers = ['商品条码', '商品名称', '销售数量', '销售单价', '销售金额',
                      '扣点比例', '扣点金额', '结算金额', '年月', '导入时间',
                      '客户名称', '操作员']
            ws.append(headers)
            
            # 填充数据
            for row in results:
                ws.append([
                    row['barcode'],
                    row['product_name'],
                    row['quantity'],
                    row['unit_price'],
                    row['total_amount'],
                    row['deduction_rate'],
                    row['deduction_amount'],
                    row['settlement_amount'],
                    row['year_month'],
                    row['import_time'].strftime('%Y-%m-%d %H:%M:%S'),
                    row['store_name'],
                    row['operator']
                ])
            
            # 保存临时文件
            filename = f"export_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
            filepath = os.path.join(app.config['EXPORT_FOLDER'], filename)
            wb.save(filepath)
            
            return send_file(filepath, as_attachment=True, download_name=f"销售数据导出_{filename}")
            
    except Exception as e:
        flash(f'导出失败: {str(e)}')
        return redirect(url_for('index'))
    finally:
        conn.close()

def get_product_name(barcode):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT name FROM products WHERE barcode = %s', (barcode,))
            product = cursor.fetchone()
            if product:
                return product['name']
    finally:
        conn.close()
    return None

if __name__ == '__main__':
    app.run(debug=True)
