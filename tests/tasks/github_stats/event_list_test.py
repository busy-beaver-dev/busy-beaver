import pytest

from busy_beaver.apps.github_summary.event_list import (
    EventList,
    CommitsList,
    CreatedReposList,
    ForkedReposList,
    IssuesOpenedList,
    PublicizedReposList,
    PullRequestsList,
    ReleasesPublishedList,
    StarredReposList,
)


def test_event_list_default_matches_all_events():
    event_list = EventList()
    assert event_list.matches_event("literally anything")


def test_base_event_list_format_text_has_default_values():
    links = ["http://example.com", "https://example.org"]

    output = EventList()._format_text(links)

    assert ">:heart: 2 events" in output
    for link in links:
        assert link in output


def test_event_lists_can_override_nouns_and_emoji():
    class NewList(EventList):
        EMOJI = ":something-amazing:"
        NOUN = "some complex thing"

    event_list = NewList()
    assert ">:something-amazing: 1 some complex thing" in event_list._format_text("a")
    assert ">:something-amazing: 2 some complex things" in event_list._format_text("ab")


lists_with_event_criteria = {
    CommitsList: {"type": "PushEvent"},
    CreatedReposList: {"type": "CreateEvent", "payload": {"ref_type": "repository"}},
    ForkedReposList: {"type": "ForkEvent"},
    IssuesOpenedList: {"type": "IssuesEvent", "payload": {"action": "opened"}},
    PublicizedReposList: {"type": "PublicEvent"},
    PullRequestsList: {"type": "PullRequestEvent", "payload": {"action": "opened"}},
    ReleasesPublishedList: {"type": "ReleaseEvent"},
    StarredReposList: {"type": "WatchEvent", "payload": {"action": "started"}},
}


@pytest.mark.parametrize("list_class,event_params", lists_with_event_criteria.items())
def test_list_detects_events_correctly(list_class, event_params):
    assert list_class.matches_event(event_params)
    assert list_class().matches_event(event_params)

    bad_event_params = {k: "not_quite_{}".format(v) for k, v in event_params.items()}
    assert not list_class.matches_event(bad_event_params)
    assert not list_class().matches_event(bad_event_params)


def test_issued_open_list_generates_custom_links():
    event_list = IssuesOpenedList()
    event_list.append(
        {
            "payload": {"issue": {"html_url": "example.com", "number": 4}},
            "repo": {"name": "some_repository"},
        }
    )
    assert f"<example.com|some_repository#4>" in event_list.generate_summary_text()
