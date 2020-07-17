import json
import requests
import numpy
import cv2
import const


class FaceApiClient:

    FACE_API_BASE_URL = 'https://japaneast.api.cognitive.microsoft.com/face/v1.0'  # noqa: E501

    @classmethod
    def detect_mat(cls, mat: numpy.ndarray) -> dict:

        # mat をバイナリに変換します。
        encode_succeeded, buffer = cv2.imencode('.png', mat)
        bytes_image = buffer.tobytes()

        # detection を行います。
        return cls.detect(bytes_image)

    @classmethod
    def detect(cls, bytes_image: bytes) -> dict:

        url = f'{cls.FACE_API_BASE_URL}/detect'
        params = {
            'recognitionModel': 'recognition_02',
        }
        headers = {
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key':
                const.AZURE_COGNITIVE_SERVICES_SUBSCRIPTION_KEY,
        }
        response = requests.post(url=url,
                                 params=params,
                                 headers=headers,
                                 data=bytes_image)
        return response.json()

    @classmethod
    def identify(cls, person_group_id: str, face_ids: list) -> dict:

        url = f'{cls.FACE_API_BASE_URL}/identify'
        headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key':
                const.AZURE_COGNITIVE_SERVICES_SUBSCRIPTION_KEY,
        }
        # NOTE: payload は積載物って意味。
        payload = {
            'personGroupId': person_group_id,
            'faceIds': face_ids,
            'maxNumOfCandidatesReturned': 1,
            'confidenceThreshold': .65,
        }
        response = requests.post(url=url,
                                 headers=headers,
                                 data=json.dumps(payload))
        return response.json()
