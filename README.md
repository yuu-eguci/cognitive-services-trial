cognitive-services-trial
===

Trial of the Azure Cognitive Services Face API.
Up to 64 face images (100x100 px) are tiled into one 8x8 image, sent to the
Face API once for detection, and then identified per PersonGroup.

## Status

- Docker: 対応!
- Python: 3.14
- Linter: ruff 0.17
- Test: pytest 9.2
- Central libraries: opencv-python 5.0, azure-storage-blob 12.31, mysql-connector-python 26.10

## Files

| File | Description |
|---|---|
| `production_draft.py` | Draft of the production batch: reads waiting `HistoryFaceImage` records from MySQL, identifies faces, and writes results back. |
| `image.py` | `FaceImage` / `FaceImageSet`: downloads images from Azure Blob Storage, tiles them, and maps API results back to each image. |
| `face_api.py` | Thin client for the Face API `detect` / `identify` endpoints. |
| `db_client.py` | MySQL client for `HistoryFaceImage`. |
| `const.py` | Settings read from environment variables. |
| `util.py` | Small helpers. |
| `trial.py`, `with_azure_blob_storage.py` | Early exploration scripts (they open a GUI window and need real services). |

## Installation

[uv](https://docs.astral.sh/uv/) is required.

```bash
uv sync
```

.env is required to run the scripts against real services.

```plaintext
AZURE_COGNITIVE_SERVICES_SUBSCRIPTION_KEY=***
PERSON_GROUP_ID=***
MYSQL_HOST=***
MYSQL_PASSWORD=***
MYSQL_USER=***
MYSQL_DATABASE=***
AZURE_STORAGE_CONNECTION_STRING=***
```

```bash
uv run python production_draft.py
```

## Docker

```bash
docker build -t cognitive-services-trial .
docker run --rm cognitive-services-trial pytest
docker run --rm --env-file .env cognitive-services-trial
```

The image runs `production_draft.py` by default. The GUI scripts (`trial.py`, `with_azure_blob_storage.py`) are meant for local use, not for the container.

## Development

Tests mock Azure and MySQL, so no credentials or network access are needed.

```bash
uv run ruff check .
uv run pytest
```
