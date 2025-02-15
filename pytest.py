import pytest
import pymysql
from app import get_db_connection

# 测试正常连接
def test_get_db_connection_success():
    connection = get_db_connection()
    assert connection is not None

# 测试连接失败情况
def test_get_db_connection_failure():
    # 模拟错误的配置
    app.config['MYSQL_HOST'] = 'invalid_host'
    with pytest.raises(pymysql.err.OperationalError):
        get_db_connection()
