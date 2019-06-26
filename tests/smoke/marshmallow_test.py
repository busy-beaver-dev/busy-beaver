"""Ensure Marshmallow is working the way we intended"""

from marshmallow import Schema, fields
import pytest

from datetime import date


class ArtistSchema(Schema):
    name = fields.Str()


class AlbumSchema(Schema):
    title = fields.Str()
    release_date = fields.Date()
    artist = fields.Nested(ArtistSchema())


@pytest.mark.smoke
def test_marshmallow_smoke_test():
    bowie = dict(name="David Bowie")
    album = dict(artist=bowie, title="Hunky Dory", release_date=date(1971, 12, 17))

    schema = AlbumSchema()
    result = schema.dump(album)

    assert result["title"] == "Hunky Dory"
    assert result["release_date"] == "1971-12-17"
    assert result["artist"]["name"] == "David Bowie"
