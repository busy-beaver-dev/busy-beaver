"""Ensure Marshmallow is working the way we intended"""

from datetime import date

from marshmallow import Schema, fields
from marshmallow.exceptions import ValidationError
import pytest


class ArtistSchema(Schema):
    name = fields.Str()


class AlbumSchema(Schema):
    title = fields.Str(required=True)
    release_date = fields.Date()
    artist = fields.Nested(ArtistSchema())


@pytest.mark.smoke
def test_marshmallow_successful_validation():
    # Arrange
    bowie = dict(name="David Bowie")
    album = dict(artist=bowie, title="Hunky Dory", release_date=date(1971, 12, 17))
    schema = AlbumSchema()

    # Act
    result = schema.dump(album)

    # Assert
    assert result["title"] == "Hunky Dory"
    assert result["release_date"] == "1971-12-17"
    assert result["artist"]["name"] == "David Bowie"


@pytest.mark.smoke
def test_marshmallow_failed_validation():
    # Arrange
    album = {"release_date": "1971-12-17", "artist": {"name": "David Bowie"}}
    schema = AlbumSchema()

    # Act
    with pytest.raises(ValidationError):
        schema.load(album)
