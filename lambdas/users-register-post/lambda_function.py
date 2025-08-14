import os
import boto3
import pymysql
from datetime import datetime
import uuid
import json
import base64
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
        
        # Validate required fields
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
        
        # For now, return success without database/S3 operations to test basic functionality
        logger.info("Basic validation passed, creating mock response")
        
        # Generate mock user ID
        user_id = str(uuid.uuid4())
        
        response_data = {
            'success': True,
            'user_id': user_id,
            'message': 'User registration received successfully',
            'data': {
                'email': body['email'],
                'full_name': body['full_name'],
                'ci': body['ci'],
                'phone1': body['phone1']
            },
            'environment': os.environ.get('ENVIRONMENT', 'unknown'),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Returning success response for user: {body['email']}")
        
        return {
            'statusCode': 201,
            'headers': cors_headers,
            'body': json.dumps(response_data)
        }
        
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

# Funciones para database y S3 (deshabilitadas por ahora para testing)
def get_database_connection():
    """Get database connection - currently disabled for testing"""
    logger.info("Database connection called (disabled for testing)")
    pass

def upload_to_s3(key, data):
    """Upload to S3 - currently disabled for testing"""  
    logger.info(f"S3 upload called for key: {key} (disabled for testing)")
    return f"s3://{AWS_BUCKET}/{key}"
