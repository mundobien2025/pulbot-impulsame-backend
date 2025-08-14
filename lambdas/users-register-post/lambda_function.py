import os
import boto3
import pymysql
from datetime import datetime
import uuid
import json
import base64

# Configuración desde variables de entorno
DB_HOST = os.environ['DB_HOST']
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']
DB_NAME = os.environ.get('DB_NAME', 'impulsame_dev')
AWS_BUCKET = os.environ['AWS_BUCKET_USER_DATOS']

def lambda_handler(event, context):
    try:
        # 1. Validar y parsear datos de entrada
        try:
            data = json.loads(event['body'])
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Error parsing JSON: {str(e)}'})
            }

        # 2. Validar campos obligatorios
        required_fields = ['email', 'full_name', 'ci', 'phone1', 'id_file', 'rif_file']
        for field in required_fields:
            if field not in data:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }

        # 3. Conectar a RDS (sin SSL)
        try:
            connection = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME,
                connect_timeout=5,
                ssl=False
            )
        except pymysql.MySQLError as e:
            print(f"[ERROR] DB Connection: {str(e)}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Database connection failed'})
            }

        # 4. Procesar archivos y subir a S3
        s3 = boto3.client('s3')
        user_folder = f"{datetime.now().strftime('%d%m%Y')}-{data['ci']}-{data['full_name'].replace(' ', '_')}"
        uploaded_files = {}

        file_mappings = {
            'id_file': 'cedula.pdf',
            'rif_file': 'rif.pdf',
            'ref1_id': 'ref1_cedula.pdf',
            'ref2_id': 'ref2_cedula.pdf',
            'work_cert': 'constancia.pdf'
        }

        for field, filename in file_mappings.items():
            if field in data and data[field]:
                try:
                    file_key = f"{user_folder}/{filename}"
                    file_data = base64.b64decode(data[field]['data'])
                    
                    s3.put_object(
                        Bucket=AWS_BUCKET,
                        Key=file_key,
                        Body=file_data,
                        ContentType=data[field].get('content_type', 'application/pdf')
                    )
                    
                    uploaded_files[field] = f"s3://{AWS_BUCKET}/{file_key}"
                except Exception as e:
                    print(f"[ERROR] Uploading {field}: {str(e)}")
                    connection.close()
                    return {
                        'statusCode': 500,
                        'body': json.dumps({'error': f'Failed to upload {field}'})
                    }

        # 5. Insertar en la base de datos
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO users (
                    id, email, full_name, birth_date, ci, phone1, phone2, address,
                    instagram, facebook, tiktok, ref1_name, ref1_relation,
                    ref2_name, ref2_relation, monthly_income, activity_type,
                    position, id_file_path, rif_file_path, ref1_id_path, ref2_id_path, work_cert_path
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(sql, (
                    str(uuid.uuid4()),
                    data['email'],
                    data['full_name'],
                    data.get('birth_date', '1970-01-01'),
                    data['ci'],
                    data['phone1'],
                    data.get('phone2'),
                    data.get('address', ''),
                    data.get('instagram'),
                    data.get('facebook'),
                    data.get('tiktok'),
                    data.get('ref1_name', ''),
                    data.get('ref1_relation', 'otro'),
                    data.get('ref2_name', ''),
                    data.get('ref2_relation', 'otro'),
                    float(data.get('monthly_income', 0)),
                    data.get('activity_type', 'dependencia'),
                    data.get('position', ''),
                    uploaded_files['id_file'],
                    uploaded_files['rif_file'],
                    uploaded_files.get('ref1_id', ''),
                    uploaded_files.get('ref2_id', ''),
                    uploaded_files.get('work_cert')
                ))
            
            connection.commit()
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'userId': cursor.lastrowid,
                    's3Location': f"s3://{AWS_BUCKET}/{user_folder}/"
                })
            }
            
        except pymysql.MySQLError as e:
            print(f"[ERROR] Database insert: {str(e)}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Database operation failed'})
            }
            
        finally:
            if connection:
                connection.close()
                
    except Exception as e:
        print(f"[UNHANDLED ERROR] {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
