import json
from unittest import mock

import numpy
import pytest
import requests

import face_api

BASE_URL = 'https://japaneast.api.cognitive.microsoft.com/face/v1.0'
KEY = 'dummy-azure_cognitive_services_subscription_key'


def test_detect_posts_binary_image():
    with mock.patch.object(face_api.requests, 'post') as post:
        post.return_value.json.return_value = [{'faceId': 'f1'}]

        result = face_api.FaceApiClient.detect(b'png-bytes')

    assert result == [{'faceId': 'f1'}]
    kwargs = post.call_args.kwargs
    assert kwargs['url'] == f'{BASE_URL}/detect'
    assert kwargs['params'] == {'recognitionModel': 'recognition_02'}
    assert kwargs['headers'] == {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': KEY,
    }
    assert kwargs['data'] == b'png-bytes'


def test_detect_mat_sends_png():
    mat = numpy.zeros((2, 2, 3), numpy.uint8)

    with mock.patch.object(face_api.FaceApiClient, 'detect') as detect:
        face_api.FaceApiClient.detect_mat(mat)

    assert detect.call_args.args[0].startswith(b'\x89PNG')


def test_identify_posts_json_payload():
    with mock.patch.object(face_api.requests, 'post') as post:
        post.return_value.json.return_value = []

        face_api.FaceApiClient.identify('group', ['f1', 'f2'])

    kwargs = post.call_args.kwargs
    assert kwargs['url'] == f'{BASE_URL}/identify'
    assert kwargs['headers']['Ocp-Apim-Subscription-Key'] == KEY
    assert json.loads(kwargs['data']) == {
        'personGroupId': 'group',
        'faceIds': ['f1', 'f2'],
        'maxNumOfCandidatesReturned': 1,
        'confidenceThreshold': .65,
    }


@pytest.mark.parametrize('call', [
    lambda: face_api.FaceApiClient.detect(b'png-bytes'),
    lambda: face_api.FaceApiClient.identify('group', ['f1']),
])
def test_requests_use_timeout(call):
    with mock.patch.object(face_api.requests, 'post') as post:
        call()

    assert post.call_args.kwargs['timeout'] == face_api.TIMEOUT_SECONDS


@pytest.mark.parametrize('call', [
    lambda: face_api.FaceApiClient.detect(b'png-bytes'),
    lambda: face_api.FaceApiClient.identify('group', ['f1']),
])
def test_api_error_raises(call):
    with mock.patch.object(face_api.requests, 'post') as post:
        post.return_value.raise_for_status.side_effect = (
            requests.HTTPError('401'))

        with pytest.raises(requests.HTTPError):
            call()
