
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

    def set_completed_status(self,
                             matched: bool,
                             candidate_person_id: str,
                             candidate_confidence: float,
                             history_face_image_id: int):
        """HistoryFaceImage に COMPLETED ステータスを付与します。

        Args:
            matched (bool): HistoryFaceImage.matched の値。
            candidate_person_id (str): .candidatePersonId の値。
            candidate_confidence (float): .candidateConfidence の値。
            history_face_image_id (int): .id の値。
        """

        update_sql = ' '.join([
            'UPDATE historyfaceimage',
            'SET',
                'recognitionStatus = %s,',  # noqa: E131
                'matched = %s,',
                'candidatePersonId = %s,',
                'candidateConfidence = %s,',
                "updatedAt = DATE_FORMAT(NOW(), '%Y-%m-%dT%H:%i:00.000Z')",
            'WHERE id = %s',
        ])
        cursor = self.connection.cursor()
        cursor.execute(update_sql, (const.WORK_PROGRESS_STATUS['COMPLETED'],
                                    matched,
                                    candidate_person_id,
                                    candidate_confidence,
                                    history_face_image_id))
        cursor.close()
        self.connection.commit()
