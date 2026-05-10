from pycon_agent.data import load_schedule
from pycon_agent.tools import search_talks, recommend_talks, find_related

TALKS = load_schedule("schedule.json")


def test_search_talks_finds_observability():
    results = search_talks("observability", TALKS)
    assert len(results) >= 1
    assert any("Dienst" in r["speaker"] for r in results)


def test_search_talks_finds_by_speaker():
    results = search_talks("Sebastian Raschka", TALKS)
    assert len(results) >= 1
    assert any("Raschka" in r["speaker"] for r in results)


def test_search_talks_returns_dict_format():
    results = search_talks("Python", TALKS)
    assert len(results) > 0
    result = results[0]
    assert "title" in result
    assert "speaker" in result
    assert "date" in result
    assert "room" in result


def test_search_talks_max_10_results():
    results = search_talks("Python", TALKS)
    assert len(results) <= 10


def test_search_talks_no_results():
    results = search_talks("xyzzyplugh42 frobnicator99", TALKS)
    assert len(results) == 0


def test_recommend_talks_returns_all():
    results = recommend_talks("data engineer interested in observability", TALKS)
    assert len(results) == len(TALKS)


def test_recommend_talks_truncates_abstracts():
    results = recommend_talks("any profile", TALKS)
    for r in results:
        if r.get("abstract"):
            assert len(r["abstract"]) <= 100


def test_find_related_by_exact_title():
    sovereignty_talk = next(t for t in TALKS if "sovereignty" in t.title.lower())
    results = find_related(sovereignty_talk.title, TALKS)
    assert len(results) >= 1
    assert all(r["title"] != sovereignty_talk.title for r in results)


def test_find_related_by_partial_title():
    results = find_related("Sovereignty", TALKS)
    assert len(results) >= 1


def test_find_related_unknown_talk():
    results = find_related("This Talk Does Not Exist At All", TALKS)
    assert len(results) == 0
