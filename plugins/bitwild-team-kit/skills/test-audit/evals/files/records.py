"""The client accepts V1 and V2 records. Each record has an integer ID.
Both supported display scales must fit the 144-pixel panel width.
"""


def parse_id(raw):
    return int(raw)


def read_v1(record):
    return parse_id(record["id"])


def read_v2(record):
    return parse_id(record["ref"])


def label_width(scale):
    return 68 * scale


def test_v1_id():
    assert read_v1({"id": "07"}) == 7


def test_v1_example_again():
    assert read_v1({"id": "07"}) == 7


def test_parse_id():
    assert parse_id("08") == 8


def test_v2_id():
    assert read_v2({"ref": "07", "id": "4"}) == 7


def test_large_text_fits():
    assert label_width(2) <= 144
