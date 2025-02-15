import os

# 定义一个配置类，用于存储应用程序的配置信息
class Config:
    # MySQL 数据库的主机地址，这里设置为本地主机
    MYSQL_HOST = 'localhost'
    # MySQL 数据库的用户名，这里设置为 root
    MYSQL_USER = 'root'
    # MySQL 数据库的密码
    MYSQL_PASSWORD = 'songsong'
    # 要使用的 MySQL 数据库的名称，这里设置为 sales_data
    MYSQL_DB = 'sales_data'
    # 应用程序的密钥，用于会话管理和数据加密等安全相关操作
    SECRET_KEY = 'your-secret-key-here'
    # 上传文件的存储文件夹路径，通过 os 模块动态获取当前文件所在目录并拼接 'uploads' 文件夹
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    # 允许上传的文件扩展名集合，这里只允许上传扩展名为 xlsx 的文件
    ALLOWED_EXTENSIONS = {'xlsx'}
