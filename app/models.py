from databases import Database
from sqlalchemy import Column, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import DateTime, Integer, String

from app.constants import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL)
database = Database(DATABASE_URL)


class Initiative(Base):
    __tablename__ = "initiative_trackers"

    id = Column(Integer, primary_key=True)
    channel_id = Column(String, nullable=False)
    current_round = Column(Integer, nullable=False, default=1)
    current_init = Column(Integer, nullable=True)


class InitiativeMember(Base):
    __tablename__ = "initiative_members"

    id = Column(Integer, primary_key=True)
    initiative_id = Column(
        Integer,
        ForeignKey(Initiative.id, ondelete="CASCADE"),
        nullable=False,
    )
    player_name = Column(String, nullable=False)
    init_value = Column(Integer, nullable=False)
    tiebreaker_order = Column(Integer, nullable=False)

    deleted_at = Column(DateTime, nullable=True)
