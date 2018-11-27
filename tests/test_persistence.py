from busy_beaver.persistence import fetch_all_users, fetch_matched_users
from busy_beaver import db
from busy_beaver.models import User

import pytest


@pytest.fixture(scope="function")
def persisted_user():
    savepoint = db.session.begin_nested()
    db.session.begin_nested()

    for _ in range(2):
        user = User(**{
            "slack": "test_slack",
            "github": "github_account",
        })
        db.session.add(user)
    db.session.commit()

    yield

    savepoint.rollback()


@pytest.fixture(scope="function")
def persisted_full_db():
    savepoint = db.session.begin_nested()
    db.session.begin_nested()

    for _ in range(2):
        user = User(**{
            "slack": "test_slack_account",
            "github": "github_account",
        })
        db.session.add(user)

    for _ in range(20):
        user = User(**{
            "slack": "noise",
            "github": "noise",
        })
        db.session.add(user)

    yield

    savepoint.rollback()


def test_fetch_all_users(persisted_user):
    # Arrange
    # Act
    result = fetch_all_users()

    # Assert
    assert len(result) == 2


def test_fetch_matched_users(persisted_full_db):
    # Arrange
    # Act
    result = fetch_matched_users(["test_slack_account"])

    # Assert
    assert len(result) == 2
