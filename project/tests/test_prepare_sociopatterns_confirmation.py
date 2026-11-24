from experiments.prepare_sociopatterns_confirmation import parse_kenya, parse_tij


def test_parse_tij_uses_first_three_columns_only():
    assert parse_tij(["20 3 8 classA classB", "40 8 9"]) == [(20, "3", "8"), (40, "8", "9")]


def test_parse_kenya_makes_household_scoped_node_ids_and_ordered_time():
    rows = [{"h1": "E", "m1": "23", "h2": "F", "m2": "3", "day": "2", "hour": "14"}]
    assert parse_kenya(rows) == [(136800, "E-23", "F-3")]
