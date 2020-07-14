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


def read_image(image_path: str) -> numpy.ndarray:

    # 画像を読み込みます。
    # NOTE: imread により画像が mat 形式のデータになります。
    # NOTE: mat ってのは numpy の2,3次元配列です。
    # NOTE: type(mat) -> <class 'numpy.ndarray'>
    # NOTE: 2次元のことを channel といい、3次元のことを dimension といいます。
    mat = cv2.imread(image_path)

    # NOTE: 'not mat' とか書くと The truth value of an array with
    # NOTE: more than one element is ambiguous. と言われる。
    assert mat is not None, '画像が読み込めなかったよ。'

    # cv2.IMREAD_GRAYSCALE を指定すると白黒になる。
    mat_grayscale = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    assert mat_grayscale is not None, 'グレースケール画像が読み込めなかったよ。'

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

    # mat_file の2次元配列を受け取り、タイル状に連結します。
    return cv2.vconcat([cv2.hconcat(list_1d) for list_1d in list_2d])


# mat_file = read_image('./100x100-dog.png')
# show_image(mat_file)

mat_files = [
    read_image('./100x100-dog.png'),
    read_image('./100x100-egc.png'),
    read_image('./100x100-egc2.png'),
    read_image('./100x100-kbt.png'),
    read_image('./100x100-ymzk.png'),
    read_image('./100x100-dog.png'),
    read_image('./100x100-egc.png'),
    read_image('./100x100-egc2.png'),
    read_image('./100x100-kbt.png'),
    read_image('./100x100-ymzk.png'),
]

# ブランク画像です。
# NOTE: 黒画像なら numpy.zeros((100, 100, 3), numpy.uint8)
blank_mat_file = numpy.ones((100, 100, 3), numpy.uint8) * 255

# 各画像のサイズが100x100であることを確認します。
# NOTE: 連結するためにはサイズがあっていないといけないらしい。
for mat_file in mat_files:
    assert get_image_size(mat_file) == (100, 100), '100x100じゃない画像が紛れ込んでいます。'

# 配列を4x4にします。
list_2d = []
for vertical_index in range(4):
    list_2d.append([])
    for horizontal_index in range(4):
        # 空きマスにもブランク画像を
        mat_file = mat_files.pop(0) if len(mat_files) else blank_mat_file
        list_2d[vertical_index].append(mat_file)

# 4x4で連結します。
concatenated_mat_file = concatenate_tile(list_2d)
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
