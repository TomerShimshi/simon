from simon.hebrew_letters import to_base_form, to_display_form


def test_to_base_form_maps_each_final_letter():
    assert to_base_form("ך") == "כ"
    assert to_base_form("ם") == "מ"
    assert to_base_form("ן") == "נ"
    assert to_base_form("ף") == "פ"
    assert to_base_form("ץ") == "צ"


def test_to_base_form_leaves_non_sofit_letters_untouched():
    assert to_base_form("דבש") == "דבש"


def test_to_base_form_maps_every_character_not_just_the_last():
    assert to_base_form("םםם") == "מממ"


def test_to_base_form_handles_empty_string():
    assert to_base_form("") == ""


def test_to_display_form_only_changes_last_character():
    assert to_display_form("מנמ") == "מנם"


def test_to_display_form_no_op_when_last_char_is_not_sofit_eligible():
    assert to_display_form("דבש") == "דבש"


def test_to_display_form_handles_empty_string():
    assert to_display_form("") == ""


def test_to_display_form_single_character():
    assert to_display_form("כ") == "ך"
