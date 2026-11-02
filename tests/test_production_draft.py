from unittest import mock

import production_draft


def test_main_marks_invalid_records_pending_and_saves_results():
    records = [
        {'id': 1, 'imagePath': '/group/a.png', 'faceApiPersonId': 'p1'},
        {'id': 2, 'imagePath': None, 'faceApiPersonId': 'p1'},
    ]

    def identify(self):
        for face_image in self.face_images:
            face_image.candidate_person_id = 'p1'
            face_image.candidate_confidence = .9
        return self.face_images

    with mock.patch.object(production_draft.db_client,
                           'MySqlClient') as client_class, \
            mock.patch.object(production_draft.image.FaceImageSet,
                              'identify_by_face_api', identify):
        client = client_class.return_value.__enter__.return_value
        client.find_waiting_images.return_value = records

        production_draft._main()

    client.set_pending_status.assert_called_once_with([2])
    client.set_completed_status.assert_called_once_with(True, 'p1', .9, 1)


def test_main_logs_unexpected_errors():
    with mock.patch.object(production_draft, '_main',
                           side_effect=RuntimeError), \
            mock.patch.object(production_draft.logging,
                              'exception') as log_exception:
        production_draft.main()

    log_exception.assert_called_once()
