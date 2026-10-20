from visho.gps import gps_to_decimal


def test_north_east():
    assert abs(gps_to_decimal((37, 30, 0), "N") - 37.5) < 1e-9


def test_south_west_is_negative():
    assert gps_to_decimal((14, 15, 0), "W") == -14.25


def test_invalid_input():
    assert gps_to_decimal((1, 2), "N") is None
