from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    drought_score = Column(Integer, nullable=False)
    flood_score = Column(Integer, nullable=False)
    heat_score = Column(Integer, nullable=False)
    extreme_rainfall_score = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False)
    contributing_factors = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    farm = relationship("Farm", back_populates="risk_predictions")

    def __repr__(self):
        return (
            f"<RiskPrediction id={self.id} farm_id={self.farm_id} "
            f"risk_level={self.risk_level} created_at={self.created_at}>"
        )
