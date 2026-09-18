from simon.hebrew_letters import to_base_form
from simon.subword_bank import load_bank, load_clues


def test_bank_loads_and_is_reasonably_sized():
    bank = load_bank()
    assert 50 <= len(bank) <= 1000


def test_every_entry_has_at_least_three_subwords():
    bank = load_bank()
    for base_word, subwords in bank.items():
        assert len(subwords) >= 3, base_word


def test_every_subword_is_at_least_two_letters():
    bank = load_bank()
    for base_word, subwords in bank.items():
        for word in subwords:
            assert len(word) >= 2, (base_word, word)


def test_subwords_letters_are_a_subset_of_base_word_letters():
    bank = load_bank()
    for base_word, subwords in bank.items():
        base_key = to_base_form(base_word)
        base_counts = {ch: base_key.count(ch) for ch in set(base_key)}
        for word in subwords:
            key = to_base_form(word)
            for ch in set(key):
                assert key.count(ch) <= base_counts.get(ch, 0), (base_word, word)


def test_every_subword_in_the_bank_has_a_clue():
    bank = load_bank()
    clues = load_clues()
    for base_word, subwords in bank.items():
        for word in subwords:
            assert word in clues, (base_word, word)
            assert clues[word].strip(), (base_word, word)
