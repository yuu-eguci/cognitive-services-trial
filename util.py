
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

    list_2d = [[] for i in range(8)]
    i = 0
    for v in range(8):
        for _ in range(8):
            if i < len(list_1d):
                list_2d[v].append(list_1d[i])
                i += 1
            else:
                list_2d[v].append(blank)
    return list_2d
