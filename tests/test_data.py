from pycon_agent.data import load_schedule, Talk


def test_load_schedule_returns_talks():
    talks = load_schedule("schedule.json")
    assert len(talks) > 0
    assert all(isinstance(t, Talk) for t in talks)


def test_talk_has_required_fields():
    talks = load_schedule("schedule.json")
    talk = talks[0]
    assert talk.title
    assert talk.date
    assert talk.room


def test_load_schedule_excludes_non_talks():
    talks = load_schedule("schedule.json")
    titles_lower = [t.title.lower() for t in talks]
    assert not any("opening session" in t for t in titles_lower)
    assert not any("lightning talks" in t for t in titles_lower)


def test_talks_have_speakers():
    talks = load_schedule("schedule.json")
    with_speakers = [t for t in talks if t.speaker != "Unknown"]
    assert len(with_speakers) > len(talks) * 0.8


def test_search_by_keyword_in_title():
    talks = load_schedule("schedule.json")
    matches = [
        t for t in talks
        if "observability" in t.title.lower() or "observability" in (t.abstract or "").lower()
    ]
    assert len(matches) >= 1
    assert any("Dienst" in t.speaker for t in matches)
