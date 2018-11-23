import pytest

from adapters.utilities import GitHubLink, header_links


@pytest.mark.unit
def test_parsing_header_links():
    # Arrange
    link_header = (
        '<https://api.github.com/user/4369343/events/public?page=2>; rel="next", '
        '<https://api.github.com/user/4369343/events/public?page=10>; rel="last"'
    )

    # Act
    links = list(header_links(link_header))

    # Assert
    expected_links = [
        GitHubLink(
            type_="next", url="https://api.github.com/user/4369343/events/public?page=2"
        ),
        GitHubLink(
            type_="last",
            url="https://api.github.com/user/4369343/events/public?page=10",
        ),
    ]
    assert set(links) == set(expected_links)
