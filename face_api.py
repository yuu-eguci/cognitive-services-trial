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
