from simon.user_profile import profile_from_route, route_path


def test_route_path_strips_query_string():
    assert route_path("/simon?user=efraim") == "/simon"


def test_route_path_no_query_string():
    assert route_path("/simon") == "/simon"


def test_route_path_root_with_query():
    assert route_path("/?user=efraim") == "/"


def test_profile_from_route_reads_known_profile():
    assert profile_from_route("/?user=efraim") == "efraim"


def test_profile_from_route_none_when_missing():
    assert profile_from_route("/") is None


def test_profile_from_route_none_when_unknown_profile():
    assert profile_from_route("/?user=stranger") is None


def test_profile_from_route_works_on_any_path():
    assert profile_from_route("/simon?user=tomer") == "tomer"
