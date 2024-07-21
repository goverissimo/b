# availability/utils.py
from datetime import datetime, timedelta
from .models import AvailabilitySlot, AppointmentDuration

# availability/utils.py
import logging

def get_available_time_slots(date):
    day_of_week = date.strftime('%a').upper()
    logging.info(f"Checking availability for {day_of_week}")
    
    slots = AvailabilitySlot.objects.filter(day_of_week=day_of_week)
    logging.info(f"Found {slots.count()} slots for {day_of_week}")
    
    duration = AppointmentDuration.objects.first()
    if duration:
        duration = duration.duration
    else:
        logging.warning("No AppointmentDuration found, using default of 60 minutes")
        duration = 60

    available_slots = []
    for slot in slots:
        current_time = datetime.combine(date, slot.start_time)
        end_time = datetime.combine(date, slot.end_time)
        
        while current_time + timedelta(minutes=duration) <= end_time:
            available_slots.append(current_time.time())
            current_time += timedelta(minutes=duration)

    logging.info(f"Generated {len(available_slots)} available time slots")
    return available_slots