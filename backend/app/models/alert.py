from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farmer_id = Column(Integer, ForeignKey("farmer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_name = Column(String(100), nullable=False)
    crop = Column(String(100), nullable=False)
    risk_type = Column(String(50), nullable=False)
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False)  # HIGH, CRITICAL
    short_explanation = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    farmer_profile = relationship("FarmerProfile", back_populates="alerts")
    farm = relationship("Farm", back_populates="alerts")

    def __repr__(self):
        return (
            f"<Alert id={self.id} farm_name='{self.farm_name}' risk={self.risk_type} "
            f"score={self.risk_score} read={self.is_read}>"
        )
