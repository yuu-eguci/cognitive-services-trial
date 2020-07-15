"""Cognitive Services trial

このスクリプトの目標。

- 画像を5個用意したから、それをメモリ上に読み込む。
- 画像を連結して1枚の画像にする。これもメモリ上で行う。
- 雰囲気見るためにそれを png 画像化する。
- メモリ上から Cognitive Services へ送り、返り値を取得する。
- 返り値をみて、へーこんな感じで返ってくるんや〜って思う。
- 連結画像の、これがこれで〜って関連付けを行う。

"""

import cv2
import numpy
import requests
import dotenv
import os
import json
import mysql.connector
from pprint import pprint


# .env で環境変数を取得する場合に対応します。
# raise_error_if_not_found: .env が見つからなくてもエラーを起こさない。
dotenv.load_dotenv(dotenv.find_dotenv(raise_error_if_not_found=False))


def get_env(keyname: str) -> str:
    """環境変数を取得します。

    Arguments:
        keyname {str} -- 環境変数名。

    Raises:
        EnvNotFoundError: 環境変数が見つからない。

    Returns:
        str -- 環境変数の値。
    """
    try:
        # GitHub Actions では環境変数が設定されていなくても yaml 内で空文字列が入ってしまう。空欄チェックも行います。
        _ = os.environ[keyname]
        if not _:
            raise KeyError(f'{keyname} is empty.')
        return _
    except KeyError as e:
        raise KeyError(keyname) from e


AZURE_COGNITIVE_SERVICES_SUBSCRIPTION_KEY = get_env(
    'AZURE_COGNITIVE_SERVICES_SUBSCRIPTION_KEY')
PERSON_GROUP_ID = get_env('PERSON_GROUP_ID')


def read_image(image_path: str) -> numpy.ndarray:

    # 画像を読み込みます。
    # NOTE: imread により画像が mat 形式のデータになります。
    # NOTE: mat ってのは numpy の1,2次元配列です。
    # NOTE: type(mat) -> <class 'numpy.ndarray'>
    # NOTE: 1次元のことを channel といい、2次元のことを dimension といいます。
    mat = cv2.imread(image_path)

    # NOTE: 'not mat' とか書くと The truth value of an array with
    # NOTE: more than one element is ambiguous. と言われる。
    assert mat is not None, '画像が読み込めなかったよ。'

    # cv2.IMREAD_GRAYSCALE を指定すると白黒になる。
    # mat_grayscale = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    # assert mat_grayscale is not None, 'グレースケール画像が読み込めなかったよ。'

    return mat


def show_image(mat_file: numpy.ndarray) -> None:

    # imshow と waitKey のセットで読み込んだ画像が閲覧できます。ニュッと GUI で出てくる。
    cv2.imshow('mat', mat_file)
    cv2.waitKey(0)


def get_image_size(mat_file: numpy.ndarray) -> tuple:

    # channel はカラー画像のとき存在します。
    # NOTE: グレースケールと見分けるのに使われるようだ。
    width, height, channel = mat_file.shape
    return (width, height)


def concatenate_tile(list_2d: list) -> numpy.ndarray:

    # mat_file の1次元配列を受け取り、タイル状に連結します。
    return cv2.vconcat([cv2.hconcat(list_1d) for list_1d in list_2d])


# mat_file = read_image('./100x100-dog.png')
# show_image(mat_file)

# 検証する画像のリストです。
target_images = [
    {
        'path': './100x100-dog.png',
        'mat': None,  # imread により得られる予定。
        'faceId': None,  # detect API により得られる予定。
        'candidatePersonId': None,  # identify API により得られる予定。
    },
    {'path': './100x100-egc.png'},
    {'path': './100x100-egc2.png'},
    {'path': './100x100-kbt.png'},
    {'path': './100x100-ymzk.png'},
    {'path': './100x100-dog.png'},
    {'path': './100x100-egc.png'},
    {'path': './100x100-egc2.png'},
    {'path': './100x100-kbt.png'},
    {'path': './100x100-ymzk.png'},
]

# 各画像について mat 形式を取得します。
for image in target_images:
    image['mat'] = read_image(image['path'])

# ブランク画像です。
# NOTE: 黒画像なら numpy.zeros((100, 100, 3), numpy.uint8)
blank_image = {
    'mat': numpy.ones((100, 100, 3), numpy.uint8) * 255,
}

# 各画像のサイズが100x100であることを確認します。
# NOTE: 連結するためにはサイズがあっていないといけないらしい。
for image in target_images:
    assert get_image_size(image['mat']) == (100, 100), '100x100じゃない画像が紛れ込んでいます。'

# target_images を4x4の2次元リストに変換します。
target_images_2d = []
mat_list_2d = []
for vertical_index in range(4):
    target_images_2d.append([])
    mat_list_2d.append([])
    for horizontal_index in range(4):
        # 空きマスにもブランク画像を
        _ = target_images.pop(0) if len(target_images) else blank_image
        target_images_2d[vertical_index].append(_)
        mat_list_2d[vertical_index].append(_['mat'])

# mat ファイルを4x4で連結します。
concatenated_mat_file = concatenate_tile(mat_list_2d)
# 100px の4x4なので400x400になります。
# print(get_image_size(concatenated_mat_file))
# show_image(concatenated_mat_file)

# ローカルへの保存のやりかた2通りです。
# 1. cv2.imwrite を使う。
cv2.imwrite('./use_imwrite.png', concatenated_mat_file)
# 2. cv2.imencode と tobytes でバイナリに変換してから保存する。
encode_succeeded, buffer = cv2.imencode('.png', concatenated_mat_file)
bytes_image = buffer.tobytes()
with open('./use_imencode.png', 'wb') as f:
    f.write(bytes_image)


# /face/v1.0/detect
def face_api_detect(bytes_image: bytes) -> dict:

    url = 'https://japaneast.api.cognitive.microsoft.com/face/v1.0/detect'
    params = {
        'returnFaceId': 'true',
        'returnFaceAttributes': 'accessories,glasses,blur',
        'recognitionModel': "recognition_02",
    }
    headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': AZURE_COGNITIVE_SERVICES_SUBSCRIPTION_KEY,
    }
    response = requests.post(url=url,
                             params=params,
                             headers=headers,
                             data=bytes_image)
    return response.json()


# detection_results = face_api_detect(bytes_image)
# pprint(detection_results)
detection_results = [
    {'faceAttributes': {'accessories': [],
                        'blur': {'blurLevel': 'low', 'value': 0.0},
                        'glasses': 'NoGlasses'},
     'faceId': 'aee9e3aa-4aef-47f3-a823-0ca618c3f7d2',
     'faceRectangle': {'height': 84, 'left': 4, 'top': 115, 'width': 84}},
    {'faceAttributes': {'accessories': [],
                        'blur': {'blurLevel': 'low', 'value': 0.0},
                        'glasses': 'NoGlasses'},
     'faceId': '8b7d5ed9-add8-4016-a9be-9b7266664e0d',
     'faceRectangle': {'height': 83, 'left': 105, 'top': 215, 'width': 83}},
    {'faceAttributes': {'accessories': [],
                        'blur': {'blurLevel': 'medium', 'value': 0.28},
                        'glasses': 'NoGlasses'},
     'faceId': '3426a540-f9a8-4632-90a7-3c8069e888df',
     'faceRectangle': {'height': 83, 'left': 107, 'top': 14, 'width': 83}},
    {'faceAttributes': {'accessories': [],
                        'blur': {'blurLevel': 'medium', 'value': 0.38},
                        'glasses': 'NoGlasses'},
     'faceId': '888475d8-2c6b-4a8c-9ffa-5838ca9bdf0b',
     'faceRectangle': {'height': 82, 'left': 207, 'top': 115, 'width': 82}},
    {'faceAttributes': {'accessories': [],
                        'blur': {'blurLevel': 'low', 'value': 0.0},
                        'glasses': 'NoGlasses'},
     'faceId': '6065b3fd-c7e0-46ae-9677-543f0c87cc70',
     'faceRectangle': {'height': 78, 'left': 210, 'top': 18, 'width': 78}},
    {'faceAttributes': {'accessories': [],
                        'blur': {'blurLevel': 'low', 'value': 0.0},
                        'glasses': 'NoGlasses'},
     'faceId': '7798c3fc-d87e-4aca-b183-754c0e34691f',
     'faceRectangle': {'height': 78, 'left': 311, 'top': 118, 'width': 78}},
    {'faceAttributes': {'accessories': [],
                        'blur': {'blurLevel': 'low', 'value': 0.0},
                        'glasses': 'NoGlasses'},
     'faceId': '8f04bfb5-2b15-4814-841a-b9990bee45a5',
     'faceRectangle': {'height': 64, 'left': 17, 'top': 228, 'width': 64}},
    {'faceAttributes': {'accessories': [],
                        'blur': {'blurLevel': 'low', 'value': 0.0},
                        'glasses': 'NoGlasses'},
     'faceId': 'c5fa847b-3480-440b-b6f2-2934910e95f3',
     'faceRectangle': {'height': 64, 'left': 317, 'top': 28, 'width': 64}}
]

# faceRectangle から、画像に rectangle を書いてみる。(脇道)
for result in detection_results:
    face_rectangle = result['faceRectangle']
    left_top = (face_rectangle['left'], face_rectangle['top'])
    right_bottom = (face_rectangle['left'] + face_rectangle['width'],
                    face_rectangle['top'] + face_rectangle['height'])
    cv2.rectangle(concatenated_mat_file,
                  left_top, right_bottom, (255, 0, 0))
show_image(concatenated_mat_file)

# target_images それぞれの画像と faceId を結びつけます。 faceRectangle の座標が目印となります。
# target_image['faceId'] を埋めるということ。
for result in detection_results:
    face_rectangle = result['faceRectangle']

    # x 軸で何番目の画像?
    # NOTE: 画像サイズが100x100 なので、左上の x 座標 / 100 で切り捨て除算を行えば、 x 軸のインデックスになります。
    horizontal_index = face_rectangle['left'] // 100
    # y 軸で何番目の画像?
    vertical_index = face_rectangle['top'] // 100

    # 座標から求めた、この faceId に対応する画像です。
    target_image = target_images_2d[vertical_index][horizontal_index]
    target_image['faceId'] = result['faceId']

# 2次元配列だとこのあとは扱いづらいから1次元配列に戻します。
# HACK: 2次元 -> 1次元のシンプルなやり方があるような気がする。
# HACK: 最初から配列を numpy.array で扱っておればいけそう。
target_images = []
for lis in target_images_2d:
    target_images.extend(lis)

# # 紐付けの確認。
# for image in target_images:
#     print('path:', image['path'] if 'path' in image else None,
#           '---',
#           'faceId:', image['faceId'] if 'faceId' in image else None)


# /face/v1.0/identify
def face_api_identify(face_ids: list) -> dict:

    url = 'https://japaneast.api.cognitive.microsoft.com/face/v1.0/identify'
    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': AZURE_COGNITIVE_SERVICES_SUBSCRIPTION_KEY,
    }
    # NOTE: payload は積載物って意味。
    payload = {
        'personGroupId': PERSON_GROUP_ID,
        'faceIds': face_ids,
        'maxNumOfCandidatesReturned': 1,
        'confidenceThreshold': .65,
    }
    response = requests.post(url=url,
                             headers=headers,
                             data=json.dumps(payload))
    return response.json()


# 取得できた faceId を <PERSON_GROUP_ID> の identify に回します。
face_ids = [
    _['faceId']
    for _ in target_images
    if 'faceId' in _ and _['faceId']
]
# identification_results = face_api_identify(face_ids)
# pprint(identification_results)
identification_results = [
    {'candidates': [{'confidence': 0.683,
                     'personId': 'e03ce785-280c-45c9-a3d8-93a1626bc980'}],
     'faceId': '3426a540-f9a8-4632-90a7-3c8069e888df'},
    {'candidates': [{'confidence': 0.84629,
                     'personId': 'e03ce785-280c-45c9-a3d8-93a1626bc980'}],
     'faceId': '6065b3fd-c7e0-46ae-9677-543f0c87cc70'},
    {'candidates': [{'confidence': 0.98266,
                     'personId': '8d82ac11-ee91-4577-b165-70b6c4200621'}],
        'faceId': 'c5fa847b-3480-440b-b6f2-2934910e95f3'},
    {'candidates': [{'confidence': 0.73718,
                     'personId': 'bc5a2352-852a-48f9-8150-447e3c49eb79'}],
        'faceId': 'aee9e3aa-4aef-47f3-a823-0ca618c3f7d2'},
    {'candidates': [{'confidence': 0.68109,
                     'personId': 'e03ce785-280c-45c9-a3d8-93a1626bc980'}],
        'faceId': '888475d8-2c6b-4a8c-9ffa-5838ca9bdf0b'},
    {'candidates': [{'confidence': 0.85085,
                     'personId': 'e03ce785-280c-45c9-a3d8-93a1626bc980'}],
        'faceId': '7798c3fc-d87e-4aca-b183-754c0e34691f'},
    {'candidates': [{'confidence': 0.98209,
                     'personId': '8d82ac11-ee91-4577-b165-70b6c4200621'}],
        'faceId': '8f04bfb5-2b15-4814-841a-b9990bee45a5'},
    {'candidates': [{'confidence': 0.7313,
                     'personId': 'bc5a2352-852a-48f9-8150-447e3c49eb79'}],
        'faceId': '8b7d5ed9-add8-4016-a9be-9b7266664e0d'}
]

# 次の処理で扱いやすいよう identification_results の構造を変えます。
identification_results_dic = {}
for result in identification_results:
    # 候補が見つからないときもあります。
    if not result['candidates']:
        continue

    # { [faceId]:{[candidatePersonId], [confidence]} }
    identification_results_dic[result['faceId']] = {
        'candidatePersonId': result['candidates'][0]['personId'],
        'confidence': result['candidates'][0]['confidence'],
    }

# print(identification_results_dic)

# target_images それぞれの画像と candidate を結びつけます。
# target_image['candidatePersonId'] を埋めるということ。ついでに confidence も追加しよう。
for _ in target_images:
    # そもそも顔が detect されなかった(faceId がない)画像であるときもあります。
    if not _.get('faceId'):
        continue

    # 候補が見つからなかった(identify の結果に自分の faceId が含まれていない)ときもあります。
    if _['faceId'] not in identification_results_dic:
        continue

    candidate_for_this_image = identification_results_dic[_['faceId']]
    _['candidatePersonId'] = candidate_for_this_image['candidatePersonId']
    _['confidence'] = candidate_for_this_image['confidence']

# 紐付けの確認。
# for image in target_images:
#     print({
#         'path': image.get('path'),
#         'faceId': image.get('faceId'),
#         'candidatePersonId': image.get('candidatePersonId'),
#         'confidence': image.get('confidence'),
#     })


# cognitive services とはもう関係ないけど、 mysql に接続して candidatePersonId の正体をつきとめよう。
def find_members_by_person_ids(candidate_person_ids: set) -> list:

    MYSQL_HOST = get_env('MYSQL_HOST')
    MYSQL_PASSWORD = get_env('MYSQL_PASSWORD')
    MYSQL_USER = get_env('MYSQL_USER')
    MYSQL_DATABASE = get_env('MYSQL_DATABASE')

    # DB 接続を行います。
    mysql_connection_config = {
        'host': MYSQL_HOST,
        'user': MYSQL_USER,
        'password': MYSQL_PASSWORD,
        'database': MYSQL_DATABASE,
    }
    connection = mysql.connector.connect(**mysql_connection_config)

    # candidatePersonId ぶんのプレースホルダを作ります。 %s, %s, %s, %s, ...
    place_holder = ','.join(('%s' for i in range(len(candidate_person_ids))))

    # candidatePersonId が誰なのか取得します。
    select_sql = ' '.join([
        'SELECT',
            'facedata.faceApiPersonId,',
            'facedata.tmpName,',
            'facedata.member,',
            'member.name,',
            'member.company',
        'FROM facedata',
        'LEFT JOIN member',
            'ON facedata.member = member.id',
        f'WHERE facedata.faceApiPersonId IN ({place_holder})',
    ])
    cursor = connection.cursor(dictionary=True)
    cursor.execute(select_sql, tuple(candidate_person_ids))
    records = cursor.fetchall()
    cursor.close()

    # HACK: with ステートメントで書けるようにする。
    connection.close()

    return records


candidate_person_ids = set((
    _['candidatePersonId']
    for _ in target_images
    if _.get('candidatePersonId')
))
found_records = find_members_by_person_ids(candidate_person_ids)
pprint(found_records)

# 次の処理で使いやすいように { [faceApiPersonId]: [member 情報] } 構造にします。
found_records_dic = {}
for record in found_records:
    found_records_dic[record['faceApiPersonId']] = {
        'company': record['company'],
        'member': record['member'],
        'name': record['name'],
        'tmpName': record['tmpName'],
    }

# target_images それぞれの画像と member を結びつけます。
# target_image['member'] を埋めるということ。
for _ in target_images:
    # この image と一致した personId は結果にあるか?
    if _.get('candidatePersonId') not in found_records_dic:
        continue

    _['member'] = found_records_dic.get(_.get('candidatePersonId'))

# 紐付けの確認。
for image in target_images:
    print({
        'path': image.get('path'),
        # 'faceId': image.get('faceId'),
        # 'candidatePersonId': image.get('candidatePersonId'),
        'confidence': image.get('confidence'),
        'member': image.get('member'),
    })
