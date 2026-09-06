from datetime import datetime, timezone
from typing import Optional, Protocol
from app.schemas.climate import SoilDataResponse


class IoTSensorAdapter(Protocol):
    """
    Protocol / Interface for future IoT soil moisture probes and telemetry gateways.
    Implementations can connect to MQTT brokers, LoRaWAN base stations, or Modbus RS485 sensors.
    """
    async def read_moisture(self, sensor_id: str) -> float:
        ...

    async def read_ph(self, sensor_id: str) -> float:
        ...


class SoilService:
    """
    Soil Health and Moisture Telemetry Service.
    Computes volumetric moisture content, water deficit indices, and soil suitability.
    Architecture is prepared for plug-and-play IoT probe adapters.
    """

    def __init__(self, iot_adapter: Optional[IoTSensorAdapter] = None):
        self.iot_adapter = iot_adapter

    def get_soil_data_for_farm(
        self,
        farm_id: int,
        farm_name: str,
        soil_type: Optional[str] = None,
        irrigation_available: bool = False
    ) -> SoilDataResponse:
        """
        Retrieves current soil moisture and water availability metrics.
        In prototype mode, generates calibrated realistic agronomic data based on soil classification.
        """
        st = soil_type or "Black Soil (Regur)"

        # Calibrated moisture benchmarks depending on soil type and irrigation
        # Black soil has high moisture retention capacity; Sandy loam drains fast.
        base_moisture = 34.0 if "black" in st.lower() else (28.0 if "alluvial" in st.lower() else 22.0)
        if irrigation_available:
            base_moisture += 8.0

        # Farm-specific slight variation
        variation = ((farm_id * 7) % 11) - 4
        calculated_moisture = round(max(10.0, min(55.0, base_moisture + variation)), 1)

        # Classify water availability
        if calculated_moisture < 18.0:
            water_availability = "Critical Deficit"
            condition = "Severe moisture stress in root zone. Immediate irrigation recommended."
        elif calculated_moisture < 26.0:
            water_availability = "Low / Moderate Deficit"
            condition = "Topsoil dry; moisture present in deeper root layer. Watch for wilt."
        elif calculated_moisture <= 45.0:
            water_availability = "Adequate"
            condition = "Optimal soil moisture profile for nutrient absorption and vegetative growth."
        else:
            water_availability = "Saturated / Excessive"
            condition = "High water table or post-irrigation saturation. Ensure proper drainage."

        # Soil pH benchmark
        ph = 7.2 if "black" in st.lower() else 6.6

        return SoilDataResponse(
            farm_id=farm_id,
            farm_name=farm_name,
            soil_type=st,
            soil_moisture=calculated_moisture,
            water_availability=water_availability,
            soil_condition=condition,
            ph_level=ph,
            organic_matter_pct=1.4,
            timestamp=datetime.now(timezone.utc),
            is_demo=True,
            data_source="Calibrated Soil Agro-Model (IoT Gateway Emulation)",
            sensor_status="Ready for IoT Sensor Probe Sync"
        )


soil_service = SoilService()
