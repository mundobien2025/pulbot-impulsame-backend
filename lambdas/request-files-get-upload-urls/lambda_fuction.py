import json
import boto3
import os
from datetime import datetime, timezone
import uuid
from botocore.exceptions import ClientError

# Inicializar cliente S3
s3_client = boto3.client('s3')

# Configuración
ALLOWED_FILE_TYPES = {
    'pdf': 'application/pdf',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
PRESIGNED_URL_EXPIRATION = 3600  # 1 hora

def lambda_handler(event, context):
    """
    Lambda function para generar URLs prefirmadas para subir archivos a S3
    
    Expected request body:
    {
        "files": [
            {
                "field_name": "documento_identidad",
                "file_name": "cedula.pdf",
                "file_size": 1024000,
                "content_type": "application/pdf"
            },
            {
                "field_name": "comprobante_ingresos", 
                "file_name": "nomina.jpg",
                "file_size": 2048000,
                "content_type": "image/jpeg"
            }
        ]
    }
    """
    
    try:
        # Obtener variables de ambiente
        environment = os.environ.get('ENVIRONMENT', 'dev')
        bucket_name = os.environ.get('S3_BUCKET_NAME')
        
        if not bucket_name:
            return create_error_response(
                message="S3 bucket not configured",
                error_code="BUCKET_NOT_CONFIGURED",
                status_code=500,
                environment=environment
            )
        
        # Parsear el body del request
        if event.get('body'):
            try:
                body = json.loads(event['body'])
            except json.JSONDecodeError:
                return create_error_response(
                    message="Invalid JSON in request body",
                    error_code="INVALID_JSON",
                    status_code=400,
                    environment=environment
                )
        else:
            return create_error_response(
                message="Request body is required",
                error_code="MISSING_BODY",
                status_code=400,
                environment=environment
            )
        
        # Validar estructura del request
        files = body.get('files', [])
        if not files or not isinstance(files, list):
            return create_error_response(
                message="Files array is required and must contain at least one file",
                error_code="INVALID_FILES_ARRAY",
                status_code=400,
                environment=environment
            )
        
        # Validar que no exceda el límite de archivos (máximo 5 según tu formulario)
        if len(files) > 5:
            return create_error_response(
                message="Maximum 5 files allowed per request",
                error_code="TOO_MANY_FILES",
                status_code=400,
                environment=environment
            )
        
        # Procesar cada archivo y generar URLs prefirmadas
        upload_urls = []
        validation_errors = []
        
        for i, file_info in enumerate(files):
            # Validar campos requeridos
            validation_error = validate_file_info(file_info, i)
            if validation_error:
                validation_errors.append(validation_error)
                continue
            
            # Validar tipo de archivo
            file_extension = file_info['file_name'].split('.')[-1].lower()
            if file_extension not in ALLOWED_FILE_TYPES:
                validation_errors.append({
                    "file_index": i,
                    "field": "file_name",
                    "message": f"File type '{file_extension}' not allowed. Allowed types: {list(ALLOWED_FILE_TYPES.keys())}"
                })
                continue
            
            # Validar tamaño del archivo
            if file_info['file_size'] > MAX_FILE_SIZE:
                validation_errors.append({
                    "file_index": i,
                    "field": "file_size", 
                    "message": f"File size exceeds maximum allowed size of {MAX_FILE_SIZE} bytes"
                })
                continue
            
            # Validar content type
            expected_content_type = ALLOWED_FILE_TYPES[file_extension]
            if file_info['content_type'] != expected_content_type:
                validation_errors.append({
                    "file_index": i,
                    "field": "content_type",
                    "message": f"Invalid content type. Expected '{expected_content_type}' for .{file_extension} files"
                })
                continue
            
            # Generar key único para S3
            unique_id = str(uuid.uuid4())
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            s3_key = f"uploads/{file_info['field_name']}/{timestamp}_{unique_id}_{file_info['file_name']}"
            
            # Generar URL prefirmada
            try:
                presigned_url = s3_client.generate_presigned_url(
                    'put_object',
                    Params={
                        'Bucket': bucket_name,
                        'Key': s3_key,
                        'ContentType': file_info['content_type'],
                        'ContentLength': file_info['file_size']
                    },
                    ExpiresIn=PRESIGNED_URL_EXPIRATION
                )
                
                upload_urls.append({
                    "field_name": file_info['field_name'],
                    "file_name": file_info['file_name'],
                    "s3_key": s3_key,
                    "upload_url": presigned_url,
                    "expires_in": PRESIGNED_URL_EXPIRATION,
                    "content_type": file_info['content_type'],
                    "max_file_size": file_info['file_size']
                })
                
            except ClientError as e:
                return create_error_response(
                    message="Failed to generate presigned URL",
                    error_code="S3_PRESIGN_ERROR",
                    status_code=500,
                    environment=environment,
                    details={"aws_error": str(e)}
                )
        
        # Si hay errores de validación, retornarlos
        if validation_errors:
            return create_error_response(
                message="Validation errors found",
                error_code="VALIDATION_ERROR",
                status_code=400,
                environment=environment,
                details={"validation_errors": validation_errors}
            )
        
        # Retornar respuesta exitosa
        return create_success_response(
            message="Upload URLs generated successfully",
            data={
                "upload_urls": upload_urls,
                "bucket_name": bucket_name,
                "total_files": len(upload_urls)
            },
            environment=environment
        )
        
    except Exception as e:
        return create_error_response(
            message="Internal server error",
            error_code="INTERNAL_ERROR", 
            status_code=500,
            environment=os.environ.get('ENVIRONMENT', 'dev'),
            details={"error": str(e)}
        )

def validate_file_info(file_info, index):
    """Valida la información de cada archivo"""
    required_fields = ['field_name', 'file_name', 'file_size', 'content_type']
    
    for field in required_fields:
        if field not in file_info:
            return {
                "file_index": index,
                "field": field,
                "message": f"Field '{field}' is required"
            }
    
    # Validar tipos de datos
    if not isinstance(file_info['file_size'], int) or file_info['file_size'] <= 0:
        return {
            "file_index": index,
            "field": "file_size",
            "message": "File size must be a positive integer"
        }
    
    # Validar que el nombre del archivo tenga extensión
    if '.' not in file_info['file_name']:
        return {
            "file_index": index,
            "field": "file_name", 
            "message": "File name must include file extension"
        }
    
    return None

def create_success_response(message, data, environment, user_id=None):
    """Crear respuesta de éxito estándar"""
    response_body = {
        "success": True,
        "message": message,
        "data": data,
        "environment": environment,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if user_id:
        response_body["user_id"] = user_id
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(response_body)
    }

def create_error_response(message, error_code, status_code, environment, details=None):
    """Crear respuesta de error estándar"""
    response_body = {
        "success": False,
        "message": message,
        "error_code": error_code,
        "environment": environment,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if details:
        response_body["details"] = details
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(response_body)
    }
