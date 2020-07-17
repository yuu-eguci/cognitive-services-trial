
def get_placeholder(count: int) -> str:
    """count ぶんのプレースホルダ文字列を作ります。
    %s, %s, %s, %s, ...

    Args:
        count (int): 欲しい %s の数。

    Returns:
        str: %s, %s, %s, %s, ...
    """

    return ','.join(('%s' for i in range(count)))


if __name__ == '__main__':

    # 簡易的なユニットテスト。
    actual = get_placeholder(5)
    expected = '%s,%s,%s,%s,%s'
    assert actual == expected
