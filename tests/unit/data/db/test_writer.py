from typing import List
import string

import pytest
from hypothesis import given
from shutterbug.data.star import Star, StarTimeseries
from shutterbug.data.db.model import StarDB, StarDBLabel, StarDBTimeseries
from shutterbug.data.db.writer import DBWriter
from sqlalchemy.orm import Session
from tests.unit.data.db.db_test_tools import sqlalchemy_db
from tests.unit.data.hypothesis_stars import star, stars


def reconstruct_star_from_db(
    star: StarDB, timeseries: List[StarDBTimeseries], label: StarDBLabel
) -> Star:
    db_time = []
    db_mag = []
    db_error = []
    for row in timeseries:
        db_time.append(row.time)
        db_mag.append(row.mag)
        db_error.append(row.error)
    rec_timeseries = StarTimeseries(time=db_time, mag=db_mag, error=db_error)
    rec_star = Star(
        name=label.name,
        dataset=label.dataset,
        x=star.x,
        y=star.y,
        timeseries=rec_timeseries,
    )
    return rec_star


@given(star())
def test_convert(star: Star):
    star_db = DBWriter._convert_to_model(star)
    reconstructed_star = reconstruct_star_from_db(
        star_db, star_db.timeseries, star_db.label
    )
    assert star == reconstructed_star


@given(stars(alphabet=string.printable, dataset="test", min_size=1))
def test_write(stars: List[Star]):
    engine = sqlalchemy_db()
    writer = DBWriter(engine)
    # write in
    if len(stars) == 1:
        writer.write(stars[0])
    else:
        writer.write(stars)
    # read out and assert
    read_stars = []

    with Session(engine, future=True) as session:
        for star in session.query(StarDB).all():
            rec_star = reconstruct_star_from_db(star, star.timeseries, star.label)
            read_stars.append(rec_star)
    present = [True if x in stars else False for x in read_stars]
    assert len(present) == len(stars)
    assert all(present)
