import json

from tuitris.scores import MAX_SCORES, HighScore, HighScores


def test_load_returns_empty_when_file_missing(tmp_path):
    hs = HighScores.load(tmp_path / "missing.json")
    assert hs.entries == []


def test_load_returns_empty_on_corrupt_file(tmp_path):
    path = tmp_path / "scores.json"
    path.write_text("{not json")
    hs = HighScores.load(path)
    assert hs.entries == []


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "scores.json"
    hs = HighScores(path=path, entries=[HighScore("ABC", 1000, 5, 1)])
    hs.save()
    reloaded = HighScores.load(path)
    assert len(reloaded.entries) == 1
    assert reloaded.entries[0].initials == "ABC"
    assert reloaded.entries[0].score == 1000


def test_qualifies_when_under_max(tmp_path):
    hs = HighScores(path=tmp_path / "s.json")
    assert hs.qualifies(1) is True
    assert hs.qualifies(0) is False


def test_qualifies_only_above_lowest_when_full(tmp_path):
    hs = HighScores(
        path=tmp_path / "s.json",
        entries=[HighScore("X", 100 - i, 0, 1) for i in range(MAX_SCORES)],
    )
    assert len(hs.entries) == MAX_SCORES
    lowest = hs.entries[-1].score
    assert hs.qualifies(lowest) is False  # must be strictly greater
    assert hs.qualifies(lowest + 1) is True


def test_insert_returns_rank_and_sorts_descending(tmp_path):
    hs = HighScores(
        path=tmp_path / "s.json",
        entries=[HighScore("OLD", 500, 5, 1), HighScore("OLD", 100, 1, 1)],
    )
    rank = hs.insert(HighScore("NEW", 300, 3, 1))
    assert rank == 1
    assert [e.score for e in hs.entries] == [500, 300, 100]


def test_insert_trims_to_max(tmp_path):
    hs = HighScores(
        path=tmp_path / "s.json",
        entries=[HighScore("X", 1000 - i, 0, 1) for i in range(MAX_SCORES)],
    )
    rank = hs.insert(HighScore("NEW", 9999, 0, 1))
    assert rank == 0
    assert len(hs.entries) == MAX_SCORES
    # Lowest of the previous entries got pushed out.
    assert hs.entries[0].score == 9999
    assert hs.entries[-1].score == 1000 - (MAX_SCORES - 2)


def test_insert_persists_to_disk(tmp_path):
    path = tmp_path / "scores.json"
    hs = HighScores(path=path)
    hs.insert(HighScore("ZZZ", 42, 1, 1))
    raw = json.loads(path.read_text())
    assert raw[0]["initials"] == "ZZZ"
    assert raw[0]["score"] == 42


def test_load_sorts_entries_descending_even_if_file_unsorted(tmp_path):
    path = tmp_path / "scores.json"
    path.write_text(
        json.dumps(
            [
                {"initials": "LOW", "score": 100, "lines": 1, "level": 1},
                {"initials": "HIG", "score": 999, "lines": 9, "level": 9},
                {"initials": "MID", "score": 500, "lines": 5, "level": 5},
            ]
        )
    )
    hs = HighScores.load(path)
    assert [e.initials for e in hs.entries] == ["HIG", "MID", "LOW"]
