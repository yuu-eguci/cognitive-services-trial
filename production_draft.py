"""Production Draft

このスクリプトの目標。

- 本番のための下書き。
- こっちで成功したら、向こうへ追加してデプロイする。

"""

# Built-in modules.
import logging

# My modules.
import db_client
import image


# ローカル環境ではコレを書かないと logging.*** は機能しません。
logging.basicConfig(level=logging.DEBUG)


def main() -> None:

    logging.warning(
        'taskal-history-face-image-recognition-function-app 処理開始。')

    try:
        _main()
    except Exception:
        logging.exception('エラーが発生しました。')
        logging.error(
            'taskal-history-face-image-recognition-function-app 異常終了。')
    else:
        logging.warning(
            'taskal-history-face-image-recognition-function-app 正常終了。')


def _main() -> None:

    # 未処理の HistoryFaceImage レコードを DB から取得します。
    with db_client.MySqlClient() as mysql_client:
        records = mysql_client.find_waiting_images()
        logging.warning(
            f'未処理の HistoryFaceImage レコードを DB から取得しました。件数: {len(records)}')

    # 各画像のインスタンスを作成します。
    face_images = []
    defective_face_images = []
    for record in records:
        face_image = image.FaceImage.from_history_face_image_record(record)
        if face_image.is_valid():
            face_images.append(face_image)
        else:
            defective_face_images.append(face_image)
    logging.warning(
        f'有効なレコード件数: {len(face_images)}, 無効なレコード件数: {len(defective_face_images)}')  # noqa: E501

    # 無効なレコードには保留ステータスを付与します。
    if defective_face_images:
        with db_client.MySqlClient() as mysql_client:
            history_face_image_ids = [_.id for _ in defective_face_images]
            mysql_client.set_pending_status(history_face_image_ids)
        logging.warning('無効レコードへの保留ステータス付与完了。')
    else:
        logging.warning('保留ステータス付与スキップ。無効レコードがないため。')

    # Identification 処理の完了した FaceImage を格納します。
    identified_face_images_all = []

    while face_images:

        # 64画像ずつ処理します。
        images_max64 = face_images[:64]
        face_images = face_images[64:]
        logging.warning(f'残り{len(face_images)}個。')

        # 64画像はセットで扱います。
        face_image_set = image.FaceImageSet(images_max64)

        # Identification を行います。
        # (画像の連結、 FaceAPI による detection、同じく identification すべて行います。)
        identified_face_images = face_image_set.identify_by_face_api()

        # 別のリストに格納します。 while 外で一気に DB 更新を行うためです。
        identified_face_images_all.extend(identified_face_images)

    # 結果をもって、 HistoryFaceImage レコードを更新します。
    if not identified_face_images_all:
        return
    with db_client.MySqlClient() as mysql_client:

        for face_image in identified_face_images_all:
            mysql_client.set_completed_status(
                face_image.matched(),
                face_image.candidate_person_id,
                face_image.candidate_confidence,
                face_image.id,
            )
            logging.warning(
                f'UPDATE 完了: {face_image}, matched={face_image.matched()}')

        logging.warning('レコードへの処理済みステータス付与完了。')


if __name__ == '__main__':
    main()
