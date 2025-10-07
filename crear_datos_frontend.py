"""
Script para crear datos de ejemplo compatibles con el frontend Svelte
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Configurar Django
sys.path.append('/Users/sfherrera/Documents/Desarrollos/REGISTRO_AJUSTES/Back/Registro_Ajustes_Back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registro_ajustes.settings')
django.setup()

from adjustments.frontend_models import RegistroAjuste
from django.contrib.auth.models import User

def crear_datos_ejemplo():
    """Crear datos de ejemplo para probar el frontend"""
    
    # Crear usuario de ejemplo si no existe
    user, created = User.objects.get_or_create(
        username='admin@ejemplo.com',
        defaults={
            'email': 'admin@ejemplo.com',
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
    )
    
    if created:
        user.set_password('admin123')
        user.save()
        print(f"Usuario creado: {user.email}")
    else:
        # Actualizar contraseña si el usuario ya existe
        user.set_password('admin123')
        user.is_active = True
        user.save()
        print(f"Usuario actualizado: {user.email}")
    
    # Datos de ejemplo para registros
    registros_ejemplo = [
        {
            'id_cuenta': 'CTA-001-2024',
            'id_acuerdo_servicio': 'AS-001-2024',
            'id_cargo_facturable': 'CF-001-2024',
            'fecha_ajuste': date.today() - timedelta(days=5),
            'asesor_que_ajusto': 'María González',
            'valor_ajustado': Decimal('-150000.00'),
            'justificacion': 'Cliente reportó diferencia en facturación vs servicios recibidos',
        },
        {
            'id_cuenta': 'CTA-002-2024',
            'id_acuerdo_servicio': 'AS-002-2024',
            'id_cargo_facturable': 'CF-002-2024',
            'fecha_ajuste': date.today() - timedelta(days=3),
            'asesor_que_ajusto': 'Carlos Rodríguez',
            'valor_ajustado': Decimal('-75000.00'),
            'justificacion': 'Error detectado en auditoria interna',
        },
        {
            'id_cuenta': 'CTA-003-2024',
            'id_acuerdo_servicio': 'AS-003-2024',
            'id_cargo_facturable': 'CF-003-2024',
            'fecha_ajuste': date.today() - timedelta(days=1),
            'asesor_que_ajusto': 'Ana Martínez',
            'valor_ajustado': Decimal('-250000.00'),
            'justificacion': 'Descuento corporativo del 15% no fue aplicado en la facturación original',
        },
        {
            'id_cuenta': 'CTA-004-2024',
            'id_acuerdo_servicio': 'AS-004-2024',
            'id_cargo_facturable': 'CF-004-2024',
            'fecha_ajuste': date.today(),
            'asesor_que_ajusto': 'Luis Torres',
            'valor_ajustado': Decimal('-95000.00'),
            'justificacion': 'Cliente solicitó reducción en el alcance del servicio',
        },
        {
            'id_cuenta': 'CTA-005-2024',
            'id_acuerdo_servicio': 'AS-005-2024',
            'id_cargo_facturable': 'CF-005-2024',
            'fecha_ajuste': date.today() - timedelta(days=7),
            'asesor_que_ajusto': 'Patricia Vega',
            'valor_ajustado': Decimal('-180000.00'),
            'justificacion': 'Se detectó duplicación en la facturación de servicios mensuales',
        }
    ]
    
    # Crear los registros si no existen
    for registro_data in registros_ejemplo:
        registro, created = RegistroAjuste.objects.get_or_create(
            id_cuenta=registro_data['id_cuenta'],
            defaults={**registro_data, 'created_by': user}
        )
        
        if created:
            print(f"Registro creado: {registro.id_cuenta} - ${registro.valor_ajustado}")
        else:
            print(f"Registro ya existe: {registro.id_cuenta}")
    
    print(f"\nTotal de registros en base de datos: {RegistroAjuste.objects.count()}")
    print("Datos de ejemplo creados exitosamente!")

if __name__ == '__main__':
    crear_datos_ejemplo()