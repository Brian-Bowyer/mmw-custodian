from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import DateTime, Integer, String

from tables.base import Base


class Initiative(Base):
    __tablename__ = "initiative_trackers"

    id = Column(Integer, primary_key=True)
    channel_id = Column(String, nullable=False)
    current_round = Column(Integer, nullable=False, default=1)
    current_init = Column(Integer, nullable=False)


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
