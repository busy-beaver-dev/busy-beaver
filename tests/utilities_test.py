import pytest

from adapters.utilities import create_github_navigation_panel, APINav


@pytest.mark.unit
def test_parsing_header_links():
    # Arrange
    link_header = (
        '<https://api.github.com/user/4369343/events/public?page=3>; rel="next", '
        '<https://api.github.com/user/4369343/events/public?page=10>; rel="last", '
        '<https://api.github.com/user/4369343/events/public?page=1>; rel="prev", '
        '<https://api.github.com/user/4369343/events/public?page=1>; rel="first"'
    )

    # Act
    links = create_github_navigation_panel(link_header)

    # Assert
    expected = APINav(
        first_link="https://api.github.com/user/4369343/events/public?page=1",
        prev_link="https://api.github.com/user/4369343/events/public?page=1",
        next_link="https://api.github.com/user/4369343/events/public?page=3",
        last_link="https://api.github.com/user/4369343/events/public?page=10",
    )
    assert links == expected


@pytest.mark.unit
def test_parsing_header_links_empty():
    # Arrange
    link_header = ""

    # Act
    # Assert
    with pytest.raises(ValueError):
        create_github_navigation_panel(link_header)
