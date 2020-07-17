
import numpy
import cv2
from azure.storage.blob import BlobServiceClient
import const


class FaceImageSet:

    def __init__(self, face_images: list):
        self.face_images = face_images

    def identify_by_face_api(self) -> list:

        # 実画像を mat で取得します。
        mat_list = self.__get_mat_list()

        # mat を8x8で連結。

        # detect

        # FaceImage & faceId 紐付け。

        # identify

        # FaceImage & faceId & candidate 紐付け。

        # 各情報が付与された face_images を返却します。

    def __get_mat_list(self):
        """self.face_images の各画像について実画像を mat 形式で取得します。
        ジェネレータです。リストを返却しません。
        """

        # BlobServiceClient を作成します。
        blob_service_client = BlobServiceClient.from_connection_string(
            const.AZURE_STORAGE_CONNECTION_STRING)

        # 各 FaceImage の実画像を mat 形式で取得します。
        mat_list = []
        for face_image in self.face_images:

            # BlobClient を作成します。
            container_name, blob_name = (
                face_image.get_container_and_blob_names())
            blob_client = blob_service_client.get_blob_client(
                container=container_name, blob=blob_name)

            # 画像を DL します。
            # HACK: azure.core.pipeline.policies.http_logging_policy のログが多すぎてログが見づらい。抑制。  # noqa
            downloaded_bytes = blob_client.download_blob().readall()

            # 画像を mat 化します。
            downloaded_ndarray = numpy.frombuffer(downloaded_bytes, numpy.uint8)
            downloaded_mat = cv2.imdecode(downloaded_ndarray, cv2.IMREAD_COLOR)
            mat_list.append(downloaded_mat)
        return mat_list


class FaceImage:

    def __init__(self,
                 id: int,
                 image_path: str,
                 person_id_from_history_log: str):
        self.id = id
        self.image_path = image_path
        self.person_id_from_history_log = person_id_from_history_log

        # Detection によって判明するであろう faceId です。
        # 顔が検出されなかった場合は None のままで、 identification には進みません。
        self.detected_face_id: str = None

        # Identification によって判明するであろう personId です。
        # 顔の候補者が見つからなかった場合は None のままです。
        self.candidate_person_id: str = None
        self.candidate_confidence: float = .0

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

    def get_container_and_blob_names(self) -> iter:
        """/container_name/blob_name を分解して取得します。

        Returns:
            filter object: コンテナ名, Blob 名。
        """

        return filter(lambda _: _, self.image_path.split('/'))
