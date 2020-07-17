"""Cognitive Services trial with Azure Blob Storage

このスクリプトの目標。

- trial.py で作っているような画像を Azure Blob Storage の画像をもとに作る。

"""

import dotenv
import os
from azure.storage.blob import BlobServiceClient
import cv2
import numpy


# 環境変数取得します。
dotenv.load_dotenv(dotenv.find_dotenv(raise_error_if_not_found=False))
CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']
CONTAINER_NAME = os.environ['PERSON_GROUP_ID']

# BlobServiceClient を作成します。
blob_service_client = BlobServiceClient.from_connection_string(
    CONNECTION_STRING)

# ContainerClient を作成します。
# container_client = blob_service_client.get_container_client(
#     CONTAINER_NAME)

# BlobClient を作成します。
# blob_client = container_client.get_blob_client('100x100-dog.png')

# BlobClient は BlobServiceClient から直接、 ContainerClient をすっ飛ばして作ることも可能。
blob_client = blob_service_client.get_blob_client(
    container=CONTAINER_NAME, blob='100x100-dog.png')

# 画像を DL します。
downloaded_bytes = blob_client.download_blob().readall()

# ここでなんちゃらかんちゃらして画像を mat 化します。
downloaded_ndarray = numpy.frombuffer(downloaded_bytes, numpy.uint8)
downloaded_mat = cv2.imdecode(downloaded_ndarray, cv2.IMREAD_COLOR)

# mat 化しちゃえば結合とかやりたい放題です。
cv2.imshow('mat', downloaded_mat)
cv2.waitKey(0)

# よし、できているようだ。
