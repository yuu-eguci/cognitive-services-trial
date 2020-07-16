"""Production Draft

このスクリプトの目標。

- 本番のための下書き。
- こっちで成功したら、向こうへ追加してデプロイする。

"""

import logging


# ローカル環境ではコレを書かないと logging.*** は機能しません。
logging.basicConfig(level=logging.DEBUG)


def main() -> None:

    # 未処理の HistoryFaceImage レコードを DB から取得します。
    # TODO: mysql_client = mysql_client.MySqlClient()
    # TODO: mysql_client.find_waiting_images()
    logging.warning('未処理の HistoryFaceImage レコードを DB から取得しました。件数: n')

    # 64画像ずつ処理します。
    # TODO: lis[:64]

    # 各画像のインスタンスを作成します。
    # TODO: face_image = face_image.FaceImage(image_path,
    #                                         person_id_from_history_log)

    # 64画像はセットで扱います。
    # TODO: face_image_set = FaceImageSet(face_images)

    # Identification を行います。FaceImage.candidate_person_id を取得します。
    # (画像の連結、 FaceAPI による detection、同じく identification すべて行います。)
    # TODO: identified_face_images = face_image_set.identify_by_face_api()

    # 結果をもって、 HistoryFaceImage レコードを更新します。
    # TODO: mysql_client.update_history_face_image()

    logging.warning(
        'taskal-history-face-image-recognition-function-app 処理終了です。')


if __name__ == '__main__':
    main()
