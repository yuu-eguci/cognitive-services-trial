import mysql.connector
import const


class MySqlClient:

    def __enter__(self):
        mysql_connection_config = {
            'host': const.MYSQL_HOST,
            'user': const.MYSQL_USER,
            'password': const.MYSQL_PASSWORD,
            'database': const.MYSQL_DATABASE,
        }
        self.connection = mysql.connector.connect(**mysql_connection_config)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()

    def find_waiting_images(self) -> list:
        """未処理のレコードを HistoryFaceImage から取得します。

        Returns:
            list: HistoryFaceImage のレコード。
        """

        select_sql = ' '.join([
            'SELECT',
                'historyfaceimage.createdAt,',  # noqa: E131
                'historyfaceimage.imagePath,',
                'facedata.faceApiPersonId',
            'FROM historyfaceimage',
            'LEFT JOIN facedata',
                'ON historyfaceimage.historyFaceDataId = facedata.id',
            'WHERE',
                'recognitionStatus = 0',
        ])
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(select_sql)
        records = cursor.fetchall()
        cursor.close()

        return records
