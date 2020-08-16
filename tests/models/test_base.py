from busy_beaver.models import BaseModel


def test_basemodel_tablename():
    assert BaseModel.__tablename__ == "basemodel"
