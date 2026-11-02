import os

# const.py reads these at import time. Dummy values keep tests offline and
# make sure a developer's real .env is never used (dotenv does not override).
for _key in (
    'AZURE_COGNITIVE_SERVICES_SUBSCRIPTION_KEY',
    'PERSON_GROUP_ID',
    'MYSQL_HOST',
    'MYSQL_PASSWORD',
    'MYSQL_USER',
    'MYSQL_DATABASE',
    'AZURE_STORAGE_CONNECTION_STRING',
):
    os.environ[_key] = f'dummy-{_key.lower()}'
