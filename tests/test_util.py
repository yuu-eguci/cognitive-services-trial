import util


def test_get_placeholder():
    assert util.get_placeholder(5) == '%s,%s,%s,%s,%s'


def test_convert_list_8x8_fills_blank():
    actual = util.convert_list_8x8(list(range(1, 60)), 0)

    assert actual == [
        [1, 2, 3, 4, 5, 6, 7, 8],
        [9, 10, 11, 12, 13, 14, 15, 16],
        [17, 18, 19, 20, 21, 22, 23, 24],
        [25, 26, 27, 28, 29, 30, 31, 32],
        [33, 34, 35, 36, 37, 38, 39, 40],
        [41, 42, 43, 44, 45, 46, 47, 48],
        [49, 50, 51, 52, 53, 54, 55, 56],
        [57, 58, 59, 0, 0, 0, 0, 0],
    ]


def test_convert_list_8x8_keeps_source_list():
    source = [1, 2, 3]

    util.convert_list_8x8(source, None)

    assert source == [1, 2, 3]
