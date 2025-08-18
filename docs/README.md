# API Response Standards - Development Policy

## Overview
Este documento establece los estándares de respuesta para todas las APIs del proyecto Impulsame. Estas normas deben seguirse estrictamente para mantener consistencia entre frontend y backend.

## Backend Response Format

### Standard Success Response
Todos los endpoints del backend deben devolver respuestas JSON directas con la siguiente estructura:

```json
{
  "success": true,
  "message": "Descriptive success message",
  "data": {
    // Datos específicos del endpoint
  },
  "user_id": "uuid-string", // Si aplica
  "environment": "dev|qa|prod",
  "timestamp": "ISO-8601-timestamp"
}
```

### Standard Error Response
Para errores, usar esta estructura:

```json
{
  "success": false,
  "message": "Descriptive error message",
  "error_code": "SPECIFIC_ERROR_CODE", // Opcional
  "details": {
    // Detalles adicionales del error si son necesarios
  },
  "environment": "dev|qa|prod",
  "timestamp": "ISO-8601-timestamp"
}
```

### HTTP Status Codes
- **200**: Operación exitosa
- **201**: Recurso creado exitosamente
- **400**: Error de validación/datos incorrectos
- **401**: No autorizado
- **403**: Prohibido
- **404**: Recurso no encontrado
- **409**: Conflicto (ej: usuario ya existe)
- **500**: Error interno del servidor

## Frontend Integration Standards

### API Service Structure
Todos los servicios de API en el frontend deben seguir esta estructura:

```typescript
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// Tipo específico de respuesta del backend
export interface BackendResponseType {
  success: boolean;
  message: string;
  data: {
    // Estructura específica de datos
  };
  user_id?: string;
  environment: string;
  timestamp: string;
}

// Función de servicio
async function apiCall(data: InputType): Promise<ApiResponse<BackendResponseType>> {
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(data),
    });

    const responseText = await response.text();
    
    // Validar content-type
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      return {
        success: false,
        error: `Server error: Expected JSON but got ${contentType}`,
      };
    }

    // Parsear respuesta DIRECTAMENTE (no wrapeada)
    const parsedResponse: BackendResponseType = JSON.parse(responseText);

    // Manejar errores HTTP
    if (!response.ok) {
      return {
        success: false,
        error: parsedResponse.message || `HTTP ${response.status}`,
      };
    }

    // Verificar éxito en el payload
    if (!parsedResponse.success) {
      return {
        success: false,
        error: parsedResponse.message || 'Error en la operación',
      };
    }

    return {
      success: true,
      data: parsedResponse,
      message: parsedResponse.message,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Error desconocido',
    };
  }
}
```

## Key Rules

### ❌ NO HACER
- **NO** usar wrappers adicionales como `BackendResponse` con `statusCode`, `headers`, `body`
- **NO** devolver strings JSON dentro de otros objetos
- **NO** asumir estructuras de respuesta sin documentar

### ✅ SÍ HACER
- **SÍ** devolver JSON directo desde el backend
- **SÍ** parsear `responseText` directamente en el frontend
- **SÍ** incluir siempre `success`, `message`, `environment`, `timestamp`
- **SÍ** manejar errores HTTP y de validación consistentemente
- **SÍ** usar TypeScript interfaces para tipar respuestas

## Lambda Function Response Pattern

Para funciones Lambda con API Gateway, usar este patrón:

```python
import json
from datetime import datetime
import os

def lambda_handler(event, context):
    try:
        # Lógica del endpoint
        
        # Respuesta exitosa
        response_body = {
            "success": True,
            "message": "Operation completed successfully",
            "data": {
                # Datos específicos
            },
            "environment": os.environ.get('ENVIRONMENT', 'dev'),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            'statusCode': 200,  # o 201 para creación
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_body)
        }
        
    except ValidationError as e:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                "success": False,
                "message": str(e),
                "environment": os.environ.get('ENVIRONMENT', 'dev'),
                "timestamp": datetime.utcnow().isoformat()
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                "success": False,
                "message": "Internal server error",
                "environment": os.environ.get('ENVIRONMENT', 'dev'),
                "timestamp": datetime.utcnow().isoformat()
            })
        }
```

## Examples

### Ejemplo: User Registration
**Backend Response:**
```json
{
  "success": true,
  "user_id": "769d53ce-5150-4730-b6ce-9f7f98701bc7",
  "message": "User registered successfully",
  "data": {
    "email": "user@example.com",
    "full_name": "John Doe",
    "ci": "V-12345678",
    "phone1": "04120000000",
    "folder_name": "18082025-V-12345678-John_Doe",
    "files_uploaded": false,
    "next_step": "Upload documents using /users/upload-documents endpoint"
  },
  "environment": "dev",
  "timestamp": "2025-08-18T15:40:59.947602"
}
```

**Frontend Handling:**
```typescript
const response = await apiService.registerUser(userData);
if (response.success && response.data) {
  // Acceder a response.data.user_id, response.data.data.folder_name, etc.
  setCurrentStep('file_uploads');
} else {
  alert('Error: ' + response.error);
}
```

## Commit Message Convention

Cuando implementes estos estándares, usa conventional commits:

```bash
git add .
git commit -m "feat(api): implement standard response format for [endpoint-name]

- Add consistent success/error response structure
- Include environment and timestamp in all responses
- Follow established API response standards
- Update frontend service to handle direct JSON parsing"
git push origin dev
```

## Enforcement

- **Code Reviews**: Verificar que todas las APIs sigan estos estándares
- **Testing**: Incluir tests que validen el formato de respuesta
- **Documentation**: Actualizar documentación de API con cada nuevo endpoint
- **Frontend Services**: Crear templates/snippets para servicios de API consistentes

---

**Nota**: Esta política es efectiva inmediatamente para todos los nuevos endpoints y debe aplicarse retroactivamente a endpoints existentes durante refactoring.
