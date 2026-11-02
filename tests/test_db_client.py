from unittest import mock

import pytest

import db_client


@pytest.fixture
def connection():
    with mock.patch.object(db_client.mysql.connector, 'connect') as connect:
        yield connect, connect.return_value


def test_context_manager_connects_and_closes(connection):
    connect, conn = connection

    with db_client.MySqlClient():
        pass

    connect.assert_called_once_with(
        host='dummy-mysql_host',
        user='dummy-mysql_user',
        password='dummy-mysql_password',
        database='dummy-mysql_database',
    )
    conn.close.assert_called_once()


def test_find_waiting_images(connection):
    _, conn = connection
    cursor = conn.cursor.return_value
    cursor.fetchall.return_value = [{'id': 1}]

    with db_client.MySqlClient() as client:
        records = client.find_waiting_images()

    assert records == [{'id': 1}]
    sql, params = cursor.execute.call_args.args
    assert 'FROM historyfaceimage' in sql
    assert params == (0,)


def test_set_pending_status(connection):
    _, conn = connection
    cursor = conn.cursor.return_value

    with db_client.MySqlClient() as client:
        client.set_pending_status([10, 11])

    sql, params = cursor.execute.call_args.args
    assert sql.endswith('WHERE id IN (%s,%s)')
    assert params == (3, 10, 11)
    conn.commit.assert_called_once()


def test_set_completed_status(connection):
    _, conn = connection
    cursor = conn.cursor.return_value

    with db_client.MySqlClient() as client:
        client.set_completed_status(True, 'p1', .9, 10)

    sql, params = cursor.execute.call_args.args
    assert sql.endswith('WHERE id = %s')
    assert params == (2, True, 'p1', .9, 10)
    conn.commit.assert_called_once()
