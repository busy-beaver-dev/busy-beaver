from typing import List

from . import db, User


def fetch_all_users() -> List[User]:
    return db.query(User).all()


def fetch_matched_users(slack_names: List[str]) -> List[User]:
    return db.query(User).filter(User.slack.in_(slack_names)).all()
