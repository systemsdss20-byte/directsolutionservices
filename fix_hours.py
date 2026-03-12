import os
import django
from datetime import timedelta

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Direct.settings')
django.setup()

from Direct.Apps.Attendanceapp.models import Attendance

def fix_hours():
    print("Iniciando reparación de horas...")
    
    # Buscamos registros donde 'hours' sea menor a 1 segundo, lo que indica el error de migración
    # (El valor HH:MM:SS se guardó como HHMMSS microsegundos)
    records = Attendance.objects.filter(hours__lt=timedelta(seconds=1), hours__isnull=False)
    
    count = 0
    for att in records:
         # Obtenemos los microsegundos totales. 
         # Ej: si era 08:30:00 -> se guardó como 0.083000 segundos -> 83000 microsegundos
        micros = att.hours.microseconds
        
        if micros > 0:
            # Asumimos que el formato corrupto es HHMMSS en microsegundos
            # Ej: 83330 -> 8 horas, 33 mi, 30 seg
            
            hours = micros // 10000
            minutes = (micros // 100) % 100
            seconds = micros % 100
            
            # Validación simple para evitar crear fechas inválidas (ej: 99 minutos)
            if 0 <= hours < 24 and 0 <= minutes < 60 and 0 <= seconds < 60:
                new_duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                
                print(f"Corrigiendo ID {att.id}: {att.hours} -> {new_duration}")
                att.hours = new_duration
                att.save()
                count += 1
            else:
                print(f"Saltando ID {att.id} valor extraño: {att.hours} (HHMMSS={hours}:{minutes}:{seconds})")

    print(f"Finalizado. Total de registros corregidos: {count}")

if __name__ == '__main__':
    fix_hours()
