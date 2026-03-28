import logging
import json
from datetime import datetime

from ..core.event_bus import event_bus
from ..core.event_types import SensorEvent
from ..db.session import get_db_context
from ..models.sensor_reading import SensorReading
from ..models.device import Device

logger = logging.getLogger(__name__)


class PersistenceConsumer:
    """EventBus subscriber — persists every SensorEvent to SQLite."""

    def __init__(self):
        event_bus.subscribe("SensorEvent", self.on_sensor_event)

    async def on_sensor_event(self, event: SensorEvent) -> None:
        reading = event.reading
        try:
            with get_db_context() as db:
                # Ensure device exists
                dev = db.query(Device).filter(Device.id == reading.device_id).first()
                if dev is None:
                    dev = Device(
                        id=reading.device_id,
                        name=reading.device_id,
                        type="rack",
                        zone="default",
                    )
                    db.add(dev)
                    db.flush()

                db.add(SensorReading(
                    device_id=reading.device_id,
                    timestamp=reading.timestamp,
                    inlet_temp_c=reading.inlet_temp_c,
                    outlet_temp_c=reading.outlet_temp_c,
                    power_kw=reading.power_kw,
                    cooling_output_kw=reading.cooling_output_kw,
                    airflow_cfm=reading.airflow_cfm,
                    humidity_pct=reading.humidity_pct,
                    cpu_util_pct=reading.cpu_util_pct,
                    network_bps=reading.network_bps,
                    pue_instant=reading.pue_instant,
                    raw_json=json.dumps({
                        "inlet_temp_c": reading.inlet_temp_c,
                        "power_kw": reading.power_kw,
                    }, default=str),
                ))
                db.commit()
        except Exception as e:
            logger.error("PersistenceConsumer error: %s", e)


persistence_consumer = PersistenceConsumer()
