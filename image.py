
class FaceImage:

    def __init__(self,
                 id: int,
                 image_path: str,
                 person_id_from_history_log: str):
        self.id = id
        self.image_path = image_path
        self.person_id_from_history_log = person_id_from_history_log

    def __repr__(self) -> str:
        return (
            f"FaceImage({self.id}, '{self.image_path}', '{self.person_id_from_history_log}')")  # noqa: E501

    @classmethod
    def from_history_face_image_record(cls, record: dict) -> 'FaceImage':
        """HistoryFaceImage のレコードから FaceImage インスタンスを生成します。

        Returns:
            FaceImage: インスタンス。
        """

        return cls(record['id'],
                   record['imagePath'],
                   record['faceApiPersonId'])

    def is_valid(self) -> bool:
        """有効な FaceImage である。
        imagePath と personId の両方がないと detection と identification はできません。

        Returns:
            bool: Detection と identification のできる FaceImage である。
        """

        return self.image_path and self.person_id_from_history_log
