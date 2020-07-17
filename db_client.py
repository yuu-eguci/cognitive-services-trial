
# Third-party modules.
import mysql.connector

# My modules.
import const
import util


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
                'historyfaceimage.id,',  # noqa: E131
                'historyfaceimage.createdAt,',
                'historyfaceimage.imagePath,',
                'facedata.faceApiPersonId',
            'FROM historyfaceimage',
            'LEFT JOIN facedata',
                'ON historyfaceimage.historyFaceDataId = facedata.id',
            'WHERE',
                'recognitionStatus = %s',
        ])
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(select_sql, (const.WORK_PROGRESS_STATUS['WAITING'],))
        records = cursor.fetchall()
        cursor.close()

        return records

    def set_pending_status(self, history_face_image_ids: list) -> None:
        """HistoryFaceImage に PENDING ステータスを付与します。

        Args:
            history_face_image_ids (list): HistoryFaceImage.id の一覧。
        """

        # id 用のプレースホルダです。
        placeholder = util.get_placeholder(len(history_face_image_ids))

        # [PENDING, id, id, id, ...] です。
        placeholder_values = [const.WORK_PROGRESS_STATUS['PENDING']]
        placeholder_values.extend(history_face_image_ids)

        update_sql = ' '.join([
            'UPDATE historyfaceimage',
            'SET recognitionStatus = %s',
            f'WHERE id IN ({placeholder})',
        ])
        cursor = self.connection.cursor()
        cursor.execute(update_sql, tuple(placeholder_values))
        cursor.close()
        self.connection.commit()
