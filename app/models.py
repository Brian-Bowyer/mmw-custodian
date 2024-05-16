from databases import Database
from sqlalchemy import Column, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, validates
from sqlalchemy.schema import CheckConstraint, UniqueConstraint
from sqlalchemy.types import DateTime, Integer, String

from app.constants import DATABASE_URL
from app.errors import BacktrackError

Base: type = declarative_base()
engine = create_engine(DATABASE_URL)
database = Database(DATABASE_URL)


class InitiativeTracker(Base):
    __tablename__ = "initiative_trackers"

    id = Column(Integer, primary_key=True)
    channel_id = Column(String, nullable=False, unique=True)
    current_round = Column(
        Integer, CheckConstraint("current_round >= 1"), nullable=False, default=1
    )
    current_index = Column(
        Integer, CheckConstraint("current_index >= 0"), nullable=False, default=0
    )

    @validates("current_round")
    def validate_current_round(self, key, value):
        if not value >= 1:
            raise BacktrackError("Current round cannot be less than 1")
        return value

    @validates("current_index")
    def validate_current_index(self, key, value):
        if not value >= 0:
            raise BacktrackError("Current index cannot be less than 0")
        return value


class InitiativeMember(Base):
    __tablename__ = "initiative_members"
    __table_args__ = (
        UniqueConstraint(
            "initiative_id", "player_name", name="unique_initiative_member"
        ),
    )

    id = Column(Integer, primary_key=True)
    initiative_id = Column(
        Integer,
        ForeignKey(InitiativeTracker.id, ondelete="CASCADE"),
        nullable=False,
    )
    player_name = Column(String, nullable=False)
    init_value = Column(Integer, nullable=False)
    tiebreaker = Column(Integer, nullable=False, default=0)

    deleted_at = Column(DateTime, nullable=True)
