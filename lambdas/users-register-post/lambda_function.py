import os
import boto3
import pymysql
from datetime import datetime
import uuid
import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuración desde variables de entorno
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_NAME = os.environ.get('DB_NAME', 'impulsame_dev')
AWS_BUCKET = os.environ.get('AWS_BUCKET_USER_DATOS')

def lambda_handler(event, context):
    try:
        logger.info(f"Event received: {json.dumps(event)}")
        
        # CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Allow-Credentials': 'true'
        }
        
        # Handle OPTIONS request for CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            logger.info("Handling CORS preflight request")
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({'message': 'CORS preflight successful'})
            }
        
        # Check if body exists
        if not event.get('body'):
            logger.warning("No body in request")
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        # Parse request body
        try:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': f'Invalid JSON: {str(e)}'})
            }
        
        # Validate required fields (solo campos de texto)
        required_fields = ['email', 'full_name', 'ci', 'phone1']
        missing_fields = [field for field in required_fields if not body.get(field)]
        
        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                })
            }
        
        # Validate email format
        email = body.get('email', '').strip().lower()
        if not email or '@' not in email:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Valid email is required'})
            }
        
        # Generate user ID
        user_id = str(uuid.uuid4())
        logger.info(f"Generated user ID: {user_id}")
        
        # Process user data (solo texto, sin archivos)
        user_data = prepare_user_data(body, user_id)
        
        # Generate folder name for future file uploads
        folder_name = generate_folder_name(body['ci'], body['full_name'])
        logger.info(f"Generated folder name for future uploads: {folder_name}")
        
        # Database transaction
        connection = None
        
        try:
            # Get database connection
            connection = get_database_connection()
            
            # Check if email already exists
            if email_exists(connection, email):
                return {
                    'statusCode': 409,
                    'headers': cors_headers,
                    'body': json.dumps({
                        'error': 'Email already registered',
                        'message': 'A user with this email already exists'
                    })
                }
            
            # Check if CI already exists
            if ci_exists(connection, body['ci']):
                return {
                    'statusCode': 409,
                    'headers': cors_headers,
                    'body': json.dumps({
                        'error': 'CI already registered',
                        'message': 'A user with this CI already exists'
                    })
                }
            
            # Insert user into database
            insert_user_to_database(connection, user_data)
            
            # Commit transaction
            connection.commit()
            logger.info(f"User {user_data['email']} registered successfully")
            
            response_data = {
                'success': True,
                'user_id': user_id,
                'message': 'User registered successfully',
                'data': {
                    'email': user_data['email'],
                    'full_name': user_data['full_name'],
                    'ci': user_data['ci'],
                    'phone1': user_data['phone1'],
                    'folder_name': folder_name,
                    'files_uploaded': False,
                    'next_step': 'Upload documents using /users/upload-documents endpoint'
                },
                'environment': os.environ.get('ENVIRONMENT', 'unknown'),
                'timestamp': datetime.now().isoformat()
            }
            
            return {
                'statusCode': 201,
                'headers': cors_headers,
                'body': json.dumps(response_data)
            }
            
        except Exception as e:
            logger.error(f"Database transaction failed: {str(e)}", exc_info=True)
            
            # Rollback database changes
            if connection:
                try:
                    connection.rollback()
                    logger.info("Database transaction rolled back")
                except Exception as rollback_error:
                    logger.error(f"Error during rollback: {str(rollback_error)}")
            
            return {
                'statusCode': 500,
                'headers': cors_headers,
                'body': json.dumps({
                    'error': 'Registration failed',
                    'message': 'User registration could not be completed'
                })
            }
            
        finally:
            if connection:
                connection.close()
                logger.info("Database connection closed")
                
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def prepare_user_data(body, user_id):
    """
    Prepara los datos del usuario para inserción en la base de datos (solo texto)
    """
    now = datetime.now()
    
    user_data = {
        'id': user_id,
        'email': body.get('email', '').strip().lower(),
        'full_name': body.get('full_name'),
        'birth_date': body.get('birth_date'),
        'ci': body.get('ci'),
        'phone1': body.get('phone1'),
        'phone2': body.get('phone2'),
        'address': body.get('address'),
        'instagram': body.get('instagram'),
        'facebook': body.get('facebook'),
        'tiktok': body.get('tiktok'),
        'ref1_name': body.get('ref1_name'),
        'ref1_relation': body.get('ref1_relation'),
        'ref2_name': body.get('ref2_name'),
        'ref2_relation': body.get('ref2_relation'),
        'monthly_income': float(body.get('monthly_income', 0)) if body.get('monthly_income') else None,
        'activity_type': body.get('activity_type'),
        'position': body.get('position'),
        'created_at': now,
        'updated_at': now,
        # Archivos se setean como NULL por defecto
        'id_file_path': None,
        'rif_file_path': None,
        'ref1_id_path': None,
        'ref2_id_path': None,
        'work_cert_path': None,
        'files_uploaded': False,
        'files_upload_date': None
    }
    
    return user_data

def get_database_connection():
    """
    Establece conexión con la base de datos MySQL
    """
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False  # Para manejar transacciones manualmente
        )
        logger.info("Database connection established")
        return connection
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise e

def insert_user_to_database(connection, user_data):
    """
    Inserta el usuario en la base de datos (solo datos de texto)
    """
    try:
        with connection.cursor() as cursor:
            # SQL para insertar usuario
            sql = """
            INSERT INTO users (
                id, email, full_name, birth_date, ci, phone1, phone2, address,
                instagram, facebook, tiktok, ref1_name, ref1_relation, ref2_name, ref2_relation,
                monthly_income, activity_type, position, id_file_path, rif_file_path,
                ref1_id_path, ref2_id_path, work_cert_path, files_uploaded, files_upload_date,
                created_at, updated_at
            ) VALUES (
                %(id)s, %(email)s, %(full_name)s, %(birth_date)s, %(ci)s, %(phone1)s, %(phone2)s, %(address)s,
                %(instagram)s, %(facebook)s, %(tiktok)s, %(ref1_name)s, %(ref1_relation)s, %(ref2_name)s, %(ref2_relation)s,
                %(monthly_income)s, %(activity_type)s, %(position)s, %(id_file_path)s, %(rif_file_path)s,
                %(ref1_id_path)s, %(ref2_id_path)s, %(work_cert_path)s, %(files_uploaded)s, %(files_upload_date)s,
                %(created_at)s, %(updated_at)s
            )
            """
            
            cursor.execute(sql, user_data)
            logger.info(f"User inserted into database with ID: {user_data['id']}")
            
    except Exception as e:
        logger.error(f"Database insertion failed: {str(e)}")
        raise e

def email_exists(connection, email):
    """
    Verifica si el email ya existe en la base de datos
    """
    try:
        with connection.cursor() as cursor:
            sql = "SELECT COUNT(*) as count FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            return result['count'] > 0
    except Exception as e:
        logger.error(f"Error checking email existence: {str(e)}")
        raise e

def ci_exists(connection, ci):
    """
    Verifica si la CI ya existe en la base de datos
    """
    try:
        with connection.cursor() as cursor:
            sql = "SELECT COUNT(*) as count FROM users WHERE ci = %s"
            cursor.execute(sql, (ci,))
            result = cursor.fetchone()
            return result['count'] > 0
    except Exception as e:
        logger.error(f"Error checking CI existence: {str(e)}")
        raise e

# Funciones de utilidad para archivos (para futuro endpoint de upload)
def clean_name(name):
    """
    Limpia el nombre dejando solo caracteres ASCII 65-90 (A-Z) y 97-122 (a-z)
    Capitaliza la primera letra de cada palabra y separa con guión bajo
    """
    # Remover caracteres no ASCII válidos
    clean_chars = []
    for char in name:
        if (65 <= ord(char) <= 90) or (97 <= ord(char) <= 122) or char == ' ':
            clean_chars.append(char)
    
    clean_name = ''.join(clean_chars)
    
    # Dividir por espacios, capitalizar y unir con guión bajo
    words = [word.capitalize() for word in clean_name.split() if word]
    return '_'.join(words)

def generate_folder_name(ci, full_name):
    """
    Genera el nombre de la carpeta: ddmmaaaa-cedula-nombre_limpio
    Para futuro uso en endpoint de upload de archivos
    """
    # Fecha actual en formato ddmmaaaa
    now = datetime.now()
    date_str = now.strftime("%d%m%Y")
    
    # Limpiar nombre
    cleaned_name = clean_name(full_name)
    
    return f"{date_str}-{ci}-{cleaned_name}"
