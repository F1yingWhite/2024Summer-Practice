import pymysql
import traceback


class DataSource(object):
    def __init__(self):
        self.conn = self.to_connect()

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def to_connect(self):
        # 假设 params 是一个包含数据库连接参数的字典
        params = {
            'host': '58.87.105.2',  # 数据库主机名
            'port': 3306,  # 数据库端口号，默认为3306
            'user': 'root',  # 数据库用户名
            'passwd': 'BeiJingJiaoTongDaXue1234567890',  # 数据库密码
            'db': 'railway',  # 数据库名称
            'charset': 'utf8'  # 字符编码
        }
        try:
            connection = pymysql.connect(**params)
            return connection
        except pymysql.MySQLError as e:
            print(f"Error connecting to database: {e}")
            return None

    def is_connected(self):
        """Check if the server is alive"""
        if not self.conn:
            self.conn = self.to_connect()

        try:
            self.conn.ping(reconnect=True)
            print("db is connecting")
        except:
            traceback.print_exc()
            self.conn = self.to_connect()
            if self.conn:
                print("db reconnected")
            else:
                print("db reconnection failed")

    def query(self, sql):
        """
        查询数据
        :param sql: 要执行的SQL查询语句
        :return: 查询结果，每条记录是一个字典，包括列名和数据
        """
        if not self.conn:
            self.is_connected()
            if not self.conn:
                print("Failed to connect to database.")
                return None

        try:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        except pymysql.MySQLError as e:
            print(f"Error executing query: {e}")
            return None

    def insert_dataframe(self, df, table_name):
        """
        批量插入或更新 DataFrame 数据到数据库
        :param df: 要插入的 DataFrame
        :param table_name: 数据库中的表名
        """
        if not self.conn:
            self.is_connected()
            if not self.conn:
                print("Failed to connect to database for inserting data.")
                return False

        cols = ','.join(list(df.columns))
        placeholders = ','.join(['%s'] * len(df.columns))
        updates = ','.join([f"{col}=VALUES({col})" for col in df.columns])
        sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {updates}"

        try:
            with self.conn.cursor() as cursor:
                # 执行批量插入或更新
                cursor.executemany(sql, df.values.tolist())
                self.conn.commit()
                print("Data inserted or updated successfully.")
                return True
        except pymysql.MySQLError as e:
            print(f"Error inserting or updating data: {e}")
            self.conn.rollback()
            return False

