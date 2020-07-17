
def get_placeholder(count: int) -> str:
    """count ぶんのプレースホルダ文字列を作ります。
    %s, %s, %s, %s, ...

    Args:
        count (int): 欲しい %s の数。

    Returns:
        str: %s, %s, %s, %s, ...
    """

    return ','.join(('%s' for i in range(count)))


def convert_list_8x8(list_1d: list, blank: object) -> list:
    """1次元リストを8x8の2次元リストに変換します。

    Args:
        list_1d (list): 1次元リスト。
        blank (object): 空きスペースに置くオブジェクト。
        use_pop (bool): もとの1次元リストは空にする。

    Returns:
        list: 2次元リスト。
    """

    list_1d.extend([blank] * (64 - len(list_1d)))
    list_2d = [[] for i in range(8)]
    i = 0
    for v in range(8):
        for h in range(8):
            list_2d[v].append(list_1d[i])
            i += 1
    return list_2d


if __name__ == '__main__':

    # 簡易的なユニットテスト。
    actual = get_placeholder(5)
    expected = '%s,%s,%s,%s,%s'
    assert actual == expected

    actual = convert_list_8x8([i for i in range(1, 60)], 0)
    expected = [
        [1, 2, 3, 4, 5, 6, 7, 8],
        [9, 10, 11, 12, 13, 14, 15, 16],
        [17, 18, 19, 20, 21, 22, 23, 24],
        [25, 26, 27, 28, 29, 30, 31, 32],
        [33, 34, 35, 36, 37, 38, 39, 40],
        [41, 42, 43, 44, 45, 46, 47, 48],
        [49, 50, 51, 52, 53, 54, 55, 56],
        [57, 58, 59, 0, 0, 0, 0, 0]]
    assert actual == expected
