from unittest import mock

import cv2
import numpy
import pytest

import image


def make_face_image(id_, path='/group/a.png', person_id='p1', **kwargs):
    return image.FaceImage(id_, path, person_id, **kwargs)


def test_from_history_face_image_record():
    face_image = image.FaceImage.from_history_face_image_record(
        {'id': 1, 'imagePath': '/group/a.png', 'faceApiPersonId': 'p1'})

    assert (face_image.id, face_image.image_path,
            face_image.person_id_from_history_log) == (1, '/group/a.png', 'p1')
    assert face_image.detected_face_id is None
    assert face_image.candidate_person_id is None
    assert face_image.candidate_confidence == .0


@pytest.mark.parametrize('path, person_id, expected', [
    ('/group/a.png', 'p1', True),
    (None, 'p1', False),
    ('/group/a.png', None, False),
])
def test_is_valid(path, person_id, expected):
    assert image.FaceImage(1, path, person_id).is_valid() is expected


@pytest.mark.parametrize('path, expected', [
    ('/group/a.png', 'group'),
    ('/qrj3ntb8eh9z/a.png', 'icsoft'),
])
def test_get_person_group_id(path, expected):
    assert make_face_image(1, path).get_person_group_id() == expected


@pytest.mark.parametrize('person_id, candidate, confidence, expected', [
    ('p1', 'p1', .78, True),
    ('p1', 'p1', .77, False),
    ('p1', 'p2', .99, False),
    (None, None, .99, False),
])
def test_matched(person_id, candidate, confidence, expected):
    face_image = make_face_image(
        1, person_id=person_id,
        candidate_person_id=candidate, candidate_confidence=confidence)

    assert face_image.matched() is expected


def png_bytes():
    mat = numpy.zeros((100, 100, 3), numpy.uint8)
    return cv2.imencode('.png', mat)[1].tobytes()


def test_identify_by_face_api_maps_results_to_images():
    # 12 images in one group: faces in all but the last one.
    face_images = [make_face_image(i) for i in range(12)]
    detection = [
        {'faceId': f'f{i}',
         'faceRectangle': {'left': (i % 8) * 100 + 5,
                           'top': (i // 8) * 100 + 5}}
        for i in range(11)
    ]

    def identify(person_group_id, face_ids):
        return [
            {'faceId': face_id,
             'candidates': [] if face_id == 'f0'
             else [{'personId': 'p1', 'confidence': .9}]}
            for face_id in face_ids
        ]

    with mock.patch.object(image, 'BlobServiceClient') as blob_service, \
            mock.patch.object(image.face_api.FaceApiClient, 'detect_mat',
                              return_value=detection) as detect_mat, \
            mock.patch.object(image.face_api.FaceApiClient, 'identify',
                              side_effect=identify) as identify_mock:
        (blob_service.from_connection_string.return_value
         .get_blob_client.return_value
         .download_blob.return_value
         .readall.return_value) = png_bytes()

        result = image.FaceImageSet(face_images).identify_by_face_api()

    assert detect_mat.call_args.args[0].shape == (800, 800, 3)
    assert [c.args for c in identify_mock.call_args_list] == [
        ('group', [f'f{i}' for i in range(10)]),
        ('group', ['f10']),
    ]
    assert result is face_images
    assert [f.detected_face_id for f in result] == (
        [f'f{i}' for i in range(11)] + [None])
    assert result[0].candidate_person_id is None
    assert result[1].candidate_person_id == 'p1'
    assert result[1].candidate_confidence == .9
    assert result[11].candidate_person_id is None


def test_face_image_repr():
    face_image = make_face_image(1, detected_face_id='f1')

    assert repr(face_image) == (
        "FaceImage(1, '/group/a.png', 'p1', 'f1', None, 0.0,)")


def test_face_image_set_repr():
    face_images = [make_face_image(1), make_face_image(2)]

    assert repr(image.FaceImageSet(face_images)) == (
        f'FaceImageSet({face_images!r})')
