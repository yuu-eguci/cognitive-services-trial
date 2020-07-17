import dotenv
import os


# .env で環境変数を取得する場合に対応します。
# NOTE: raise_error_if_not_found: .env が見つからなくてもエラーを起こさない。
dotenv.load_dotenv(dotenv.find_dotenv(raise_error_if_not_found=False))


def _get_env(keyname: str) -> str:
    """環境変数を取得します。

    Arguments:
        keyname {str} -- 環境変数名。

    Raises:
        KeyError: 環境変数が見つからない。

    Returns:
        str -- 環境変数の値。
    """
    # GitHub Actions では環境変数が設定されていなくても yaml 内で空文字列が入ってしまう。空欄チェックも行います。
    _ = os.environ[keyname]
    if not _:
        raise KeyError(f'{keyname} is empty.')
    return _


AZURE_COGNITIVE_SERVICES_SUBSCRIPTION_KEY = _get_env(
    'AZURE_COGNITIVE_SERVICES_SUBSCRIPTION_KEY')
PERSON_GROUP_ID = _get_env('PERSON_GROUP_ID')
MYSQL_HOST = _get_env('MYSQL_HOST')
MYSQL_PASSWORD = _get_env('MYSQL_PASSWORD')
MYSQL_USER = _get_env('MYSQL_USER')
MYSQL_DATABASE = _get_env('MYSQL_DATABASE')
AZURE_STORAGE_CONNECTION_STRING = _get_env('AZURE_STORAGE_CONNECTION_STRING')

if __name__ == '__main__':
    print(AZURE_COGNITIVE_SERVICES_SUBSCRIPTION_KEY)
    print(PERSON_GROUP_ID)
    print(MYSQL_HOST)
    print(MYSQL_PASSWORD)
    print(MYSQL_USER)
    print(MYSQL_DATABASE)
