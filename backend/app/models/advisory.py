from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class Advisory(Base):
    __tablename__ = "advisories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    crop = Column(String(100), nullable=False)
    risk_type = Column(String(50), nullable=False)
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False)
    title = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    recommendations = Column(JSON, nullable=False, default=list)
    preventive_actions = Column(JSON, nullable=False, default=list)
    urgency = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    time_window = Column(String(100), nullable=False)
    language = Column(String(10), nullable=False, default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    farm = relationship("Farm", back_populates="advisories")

    def __repr__(self):
        return (
            f"<Advisory id={self.id} farm_id={self.farm_id} crop={self.crop} "
            f"risk={self.risk_type} urgency={self.urgency} lang={self.language}>"
        )
