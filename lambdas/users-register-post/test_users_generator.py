#!/usr/bin/env python3
"""
Script para generar usuarios de prueba para el endpoint /users/register
Genera datos aleatorios pero realistas para testing
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List

class TestUserGenerator:
    def __init__(self):
        self.nombres = [
            "Carlos Alberto", "María Elena", "José Antonio", "Ana Gabriela", 
            "Luis Fernando", "Carmen Rosa", "Pedro Pablo", "Luisa Fernanda",
            "Miguel Ángel", "Rosa María", "Juan Carlos", "Esperanza del Valle",
            "Rafael Eduardo", "Gloria Esperanza", "Andrés Felipe", "Beatriz Elena"
        ]
        
        self.apellidos = [
            "González", "Rodríguez", "Martínez", "García", "López", "Hernández",
            "Pérez", "Sánchez", "Ramírez", "Torres", "Flores", "Rivera",
            "Gómez", "Díaz", "Morales", "Jiménez", "Álvarez", "Romero"
        ]
        
        self.ciudades = [
            "Caracas", "Maracaibo", "Valencia", "Barquisimeto", "Maracay",
            "Ciudad Guayana", "Barcelona", "Maturín", "Puerto La Cruz", "Petare"
        ]
        
        self.sectores = [
            "Las Mercedes", "El Rosal", "La Candelaria", "Chacao", "Altamira",
            "Los Palos Grandes", "San Bernardino", "El Valle", "Catia", "Propatria"
        ]
        
        self.actividades = ["dependencia", "negocio"]
        self.posiciones_dependencia = [
            "Gerente de Ventas", "Analista Contable", "Asistente Administrativo",
            "Supervisor de Operaciones", "Coordinador de Marketing", "Especialista en RRHH"
        ]
        self.posiciones_negocio = [
            "Dueño de Tienda", "Comerciante", "Prestador de Servicios",
            "Empresario", "Consultor Independiente", "Técnico Especializado"
        ]
        
        self.relaciones = ["amigo", "familiar", "colega", "vecino", "conocido"]

    def generar_ci(self) -> str:
        """Genera una cédula venezolana aleatoria"""
        letra = random.choice(['V', 'E'])
        numero = random.randint(5000000, 35000000)
        return f"{letra}-{numero}"

    def generar_telefono(self) -> str:
        """Genera un número de teléfono venezolano"""
        prefijos = ['0414', '0424', '0416', '0426', '0412']
        prefijo = random.choice(prefijos)
        numero = random.randint(1000000, 9999999)
        return f"{prefijo}{numero}"

    def generar_fecha_nacimiento(self) -> str:
        """Genera fecha de nacimiento entre 18 y 65 años"""
        hoy = datetime.now()
        edad_min = 18
        edad_max = 65
        
        fecha_max = hoy - timedelta(days=edad_min * 365)
        fecha_min = hoy - timedelta(days=edad_max * 365)
        
        dias_diferencia = (fecha_max - fecha_min).days
        dias_random = random.randint(0, dias_diferencia)
        
        fecha_nacimiento = fecha_min + timedelta(days=dias_random)
        return fecha_nacimiento.strftime("%Y-%m-%d")

    def generar_ingreso_mensual(self, actividad: str) -> float:
        """Genera ingreso mensual según el tipo de actividad"""
        if actividad == "dependencia":
            return round(random.uniform(300, 2500), 2)
        else:  # negocio
            return round(random.uniform(200, 3500), 2)

    def generar_redes_sociales(self, nombre: str) -> Dict[str, str]:
        """Genera handles de redes sociales basados en el nombre"""
        nombre_clean = nombre.replace(" ", "").lower()
        sufijo = random.randint(10, 999)
        
        return {
            "instagram": f"@{nombre_clean}{sufijo}",
            "facebook": f"{nombre_clean}.{sufijo}",
            "tiktok": f"@{nombre_clean}_oficial" if random.choice([True, False]) else None
        }

    def generar_usuario(self, email_prefix: str = None) -> Dict:
        """Genera un usuario completo con datos aleatorios"""
        nombre = random.choice(self.nombres)
        apellido = random.choice(self.apellidos)
        full_name = f"{nombre} {apellido}"
        
        # Email único
        if email_prefix:
            email = f"{email_prefix}@impulsame.com"
        else:
            nombre_email = nombre.replace(" ", "").lower()
            apellido_email = apellido.lower()
            timestamp = datetime.now().strftime("%m%d%H%M")
            email = f"{nombre_email}.{apellido_email}.{timestamp}@impulsame.com"

        # Actividad y posición
        actividad = random.choice(self.actividades)
        if actividad == "dependencia":
            posicion = random.choice(self.posiciones_dependencia)
        else:
            posicion = random.choice(self.posiciones_negocio)

        # Dirección
        sector = random.choice(self.sectores)
        ciudad = random.choice(self.ciudades)
        numero = random.randint(1, 999)
        direccion = f"{sector}, Casa #{numero}, {ciudad}"

        # Referencias
        ref1_nombre = f"{random.choice(self.nombres)} {random.choice(self.apellidos)}"
        ref2_nombre = f"{random.choice(self.nombres)} {random.choice(self.apellidos)}"

        # Redes sociales
        redes = self.generar_redes_sociales(nombre)

        return {
            "email": email,
            "full_name": full_name,
            "birth_date": self.generar_fecha_nacimiento(),
            "ci": self.generar_ci(),
            "phone1": self.generar_telefono(),
            "phone2": self.generar_telefono() if random.choice([True, False]) else None,
            "address": direccion,
            "instagram": redes["instagram"],
            "facebook": redes["facebook"],
            "tiktok": redes["tiktok"],
            "ref1_name": ref1_nombre,
            "ref1_relation": random.choice(self.relaciones),
            "ref2_name": ref2_nombre,
            "ref2_relation": random.choice(self.relaciones),
            "monthly_income": str(self.generar_ingreso_mensual(actividad)),
            "activity_type": actividad,
            "position": posicion
        }

    def generar_curl_command(self, usuario: Dict, api_endpoint: str) -> str:
        """Genera comando curl para probar el API"""
        json_body = json.dumps(usuario, ensure_ascii=False)
        
        curl_command = f'''curl -X POST "{api_endpoint}/users/register" \\
  -H "Content-Type: application/json" \\
  -H "Accept: application/json" \\
  -d '{json_body}' '''
        
        return curl_command

    def generar_test_json(self, usuario: Dict) -> str:
        """Genera JSON para testing directo del Lambda"""
        test_event = {
            "httpMethod": "POST",
            "path": "/users/register",
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Test-Client/1.0"
            },
            "queryStringParameters": None,
            "pathParameters": None,
            "body": json.dumps(usuario, ensure_ascii=False),
            "isBase64Encoded": False,
            "requestContext": {
                "requestId": f"test-request-{random.randint(100, 999)}",
                "stage": "dev",
                "httpMethod": "POST",
                "path": "/users/register",
                "accountId": "123456789012",
                "identity": {
                    "sourceIp": "127.0.0.1"
                }
            }
        }
        
        return json.dumps(test_event, indent=2, ensure_ascii=False)

def main():
    generator = TestUserGenerator()
    
    # Configuración
    API_ENDPOINT = "https://zkmeuo2c8.execute-api.us-east-1.amazonaws.com/dev"  # Cambiar por tu endpoint real
    CANTIDAD_USUARIOS = 5
    
    print("=== GENERADOR DE USUARIOS DE PRUEBA ===\n")
    
    for i in range(1, CANTIDAD_USUARIOS + 1):
        print(f"--- USUARIO {i} ---")
        
        # Generar usuario
        usuario = generator.generar_usuario(f"test{i}")
        
        # Mostrar datos del usuario
        print("📋 Datos del usuario:")
        print(f"  Email: {usuario['email']}")
        print(f"  Nombre: {usuario['full_name']}")
        print(f"  CI: {usuario['ci']}")
        print(f"  Teléfono: {usuario['phone1']}")
        print(f"  Actividad: {usuario['activity_type']} - {usuario['position']}")
        print(f"  Ingreso: ${usuario['monthly_income']}")
        
        # Comando CURL
        print("\n🔧 Comando CURL:")
        curl_cmd = generator.generar_curl_command(usuario, API_ENDPOINT)
        print(curl_cmd)
        
        # JSON para Lambda
        print("\n📄 JSON para prueba directa Lambda:")
        test_json = generator.generar_test_json(usuario)
        print(test_json)
        
        print("\n" + "="*80 + "\n")

    print("✅ Usuarios generados exitosamente!")
    print(f"💡 Recuerda cambiar el API_ENDPOINT por tu URL real de API Gateway")

if __name__ == "__main__":
    main()
