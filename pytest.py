# import app
# import pytest
# import pymysql
# from app import get_db_connection

from werkzeug.security import generate_password_hash, check_password_hash
# # 测试正常连接
# def test_get_db_connection_success():
#     connection = get_db_connection()
#     assert connection is not None

# # 测试连接失败情况
# def test_get_db_connection_failure():
#     # 模拟错误的配置
#     app.config['MYSQL_HOST'] = 'invalid_host'
#     with pytest.raises(pymysql.err.OperationalError):
#         get_db_connection()


password = "1234"
hashed_password = generate_password_hash(password)

print("password哈西值：" + hashed_password) 
# 模拟用户登录时输入的密码


# 验证密码
if check_password_hash(hashed_password, password):
    password1 = check_password_hash(hashed_password, password)
    print("密码验证成功" + str(password1))
else:
    print("密码验证失败")