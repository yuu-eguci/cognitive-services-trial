
# Third-party modules.
import numpy
import cv2
from azure.storage.blob import BlobServiceClient

# My modules.
import const
import util
import face_api


class FaceImageSet:

    def __init__(self, face_images: list):
        self.face_images = face_images

    def __repr__(self) -> str:

        return [repr(face_image) for face_image in self.face_images]

    def identify_by_face_api(self) -> list:

        # 実画像を mat で取得します。
        mat_list = self.__get_mat_list()

        # mat を8x8で連結。内部で mat_list は空になります。
        concatenated_mat = self.__concatenate_mat_8x8(mat_list)

        # Detection API にまわし、結果を取得します。
        detection_result = face_api.FaceApiClient.detect_mat(concatenated_mat)

        # 各 FaceImage に faceId を与えます。
        self.__add_detected_face_ids(detection_result)

        # Identification API を利用し、各 FaceImage に candidate を与えます。
        self.__identify_and_add_candidates()

        # 各情報が付与された face_images を返却します。
        return self.face_images

    def __get_mat_list(self) -> list:
        """self.face_images の各画像について実画像を mat 形式で取得します。

        Returns:
            list: mat 形式の画像のリスト。
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

    def __concatenate_mat_8x8(self, list_1d: list) -> numpy.ndarray:
        """画像の一覧を連結し8x8の mat 形式で取得します。

        Args:
            list_1d (list): mat 形式の画像のリスト。64枚なくても大丈夫です。

        Returns:
            numpy.ndarray: 連結したひとつの mat 画像。
        """

        # 画像が64枚に満たないときのための空白画像です。
        blank_mat = numpy.ones((100, 100, 3), numpy.uint8) * 255

        # 8x8の2次元配列に変換します。
        list_2d = util.convert_list_8x8(list_1d, blank_mat)

        # mat の1次元配列を受け取り、タイル状に連結します。
        return cv2.vconcat([cv2.hconcat(list_1d) for list_1d in list_2d])

    def __add_detected_face_ids(self, detection_result: list) -> None:
        """FaceImage.detected_face_id を埋めます。

        Args:
            detection_result (list): Detection 結果。
        """

        # 画像の一覧を一時的に2次元配列にします。
        face_images_2d = util.convert_list_8x8(self.face_images, None)

        # faceRectangle の座標をもとに FaceImage.detected_face_id を埋めます。
        # HACK: detection_result を class 化すればもっと読みやすそう。
        for result in detection_result:
            face_rectangle = result['faceRectangle']

            # x 軸で何番目の画像?
            # NOTE: 画像サイズが100x100 なので、
            # NOTE: 左上の x 座標 / 100 で切り捨て除算を行えば、 x 軸のインデックスになります。
            horizontal_index = face_rectangle['left'] // 100
            # y 軸で何番目の画像?
            vertical_index = face_rectangle['top'] // 100

            # 座標から求めた、この faceId に対応する画像です。
            target_image = face_images_2d[vertical_index][horizontal_index]
            target_image.detected_face_id = result['faceId']

    def __identify_and_add_candidates(self) -> None:
        """Identification API を利用し、各 FaceImage に candidate を与えます。
        HACK: 読みづらすぎるし長いのでリファクタリング。
        """

        # Identification は person_group_id ごとに行います。
        # そのため face_images を person_group_id ごとに分けます。
        face_images_by_person_group_id = {}
        for face_image in self.face_images:
            person_group_id = face_image.get_person_group_id()
            if person_group_id not in face_images_by_person_group_id:
                face_images_by_person_group_id[person_group_id] = []
            face_images_by_person_group_id[person_group_id].append(face_image)

        # PersonGroupId ごとに identification API にまわします。
        for person_group_id, face_images_in_group in face_images_by_person_group_id.items():  # noqa: E501
            # このグループの画像の faceId 一覧を回収します。
            face_ids = [
                face_image.detected_face_id
                for face_image in face_images_in_group
                if face_image.detected_face_id
            ]

            while face_ids:

                # faceId 10件ずつ処理します。
                # NOTE: Identification API には最大で10件という制限があるため。
                face_ids_max10 = face_ids[:10]
                face_ids = face_ids[10:]

                # Identification API にまわし、結果を取得します。
                identification_result = face_api.FaceApiClient.identify(
                    person_group_id, face_ids_max10)

                # 各 FaceImage に candidate を与えます。
                self.__add_candidates(identification_result)

    def __add_candidates(self, identification_result: list) -> None:
        """FaceImage.candidate_person_id と FaceImage.candidate_confidence を埋めます。

        Args:
            identification_result (list): Identification 結果。
        """

        # 次の処理で扱いやすいよう identification_result の構造を変えます。
        # {faceId: {personId, confidence}}
        # HACK: identification_result を class 化すればもっと読みやすそう。
        result_dic = {}
        for result in identification_result:

            # 候補が見つからないときもあります。
            if not result['candidates']:
                continue

            result_dic[result['faceId']] = {
                'personId': result['candidates'][0]['personId'],
                'confidence': result['candidates'][0]['confidence'],
            }

        # 整理したデータをもとに candidate_person_id と candidate_confidence を埋めます。
        for face_image in self.face_images:

            if face_image.detected_face_id not in result_dic:
                continue

            face_image.candidate_person_id = result_dic[
                face_image.detected_face_id]['personId']
            face_image.candidate_confidence = result_dic[
                face_image.detected_face_id]['confidence']


class FaceImage:

    def __init__(self,
                 id: int,
                 image_path: str,
                 person_id_from_history_log: str,
                 detected_face_id: str = None,
                 candidate_person_id: str = None,
                 candidate_confidence: float = .0):
        self.id = id
        self.image_path = image_path
        self.person_id_from_history_log = person_id_from_history_log

        # Detection によって判明するであろう faceId です。
        # 顔が検出されなかった場合は None のままで、 identification には進みません。
        self.detected_face_id = detected_face_id

        # Identification によって判明するであろう personId です。
        # 顔の候補者が見つからなかった場合は None のままです。
        self.candidate_person_id = candidate_person_id
        self.candidate_confidence = candidate_confidence

    def __repr__(self) -> str:

        return ('FaceImage(%s, %s, %s, %s, %s, %s,)' % (
            self.id,
            f"'{self.image_path}'"
            if self.image_path else 'None',
            f"'{self.person_id_from_history_log}'"
            if self.person_id_from_history_log else 'None',
            f"'{self.detected_face_id}'"
            if self.detected_face_id else 'None',
            f"'{self.candidate_person_id}'"
            if self.candidate_person_id else 'None',
            self.candidate_confidence,
        ))

        return (
            f"FaceImage({self.id}, '{self.image_path}', '{self.person_id_from_history_log}', detected_face_id='{self.detected_face_id}', candidate_person_id='{self.candidate_person_id}', candidate_confidence={self.candidate_confidence})")  # noqa: E501

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

    def get_person_group_id(self) -> str:
        """この画像の PersonGroupId を取得します。
        container_name がそれに該当します。

        Returns:
            str: PersonGroupId。
        """

        container_name, blob_name = (self.get_container_and_blob_names())

        # NOTE: テストのためだけの処理です。コンテナ名 qrj3ntb8eh9z は icsoft として扱います。
        if container_name == 'qrj3ntb8eh9z':
            return 'icsoft'

        return container_name

    def matched(self) -> bool:
        """person_id_from_history_log と candidate_person_id が一致している。
        かつ、十分な確信度がある。

        Returns:
            bool: person_id_from_history_log == candidate_person_id
        """

        if self.person_id_from_history_log is None:
            return False

        person_id_is_matched = (
            self.person_id_from_history_log == self.candidate_person_id)
        has_enough_confidence = self.candidate_confidence >= .78

        return person_id_is_matched and has_enough_confidence
