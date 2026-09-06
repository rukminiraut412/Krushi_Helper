from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farmer_id = Column(Integer, ForeignKey("farmer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_name = Column(String(100), nullable=False)
    area = Column(Float, nullable=True)  # in acres
    crop = Column(String(100), nullable=True)
    sowing_date = Column(Date, nullable=True)
    soil_type = Column(String(50), nullable=True)
    irrigation_available = Column(Boolean, default=False, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    farmer_profile = relationship("FarmerProfile", back_populates="farms")
    risk_predictions = relationship(
        "RiskPrediction",
        back_populates="farm",
        cascade="all, delete-orphan",
        order_by="desc(RiskPrediction.created_at)"
    )
    advisories = relationship(
        "Advisory",
        back_populates="farm",
        cascade="all, delete-orphan",
        order_by="desc(Advisory.created_at)"
    )
    alerts = relationship(
        "Alert",
        back_populates="farm",
        cascade="all, delete-orphan",
        order_by="desc(Alert.created_at)"
    )

    def __repr__(self):
        return f"<Farm id={self.id} farm_name={self.farm_name} crop={self.crop}>"
