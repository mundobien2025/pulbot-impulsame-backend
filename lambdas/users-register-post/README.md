# Como consumir este endpoint /users/register



# Cambiar por tu URL real de API Gateway
export API_URL="https://tu-api-id.execute-api.us-east-1.amazonaws.com/dev"

curl -X POST "$API_URL/users/register" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "email": "test.nuevo@impulsame.com",
    "full_name": "Roberto Carlos Mendoza",
    "birth_date": "1985-03-20",
    "ci": "V-19876543",
    "phone1": "04141234567",
    "phone2": "04241234567",
    "address": "Av. Libertador, Torre #45, Caracas",
    "instagram": "@robertomendoza",
    "facebook": "roberto.mendoza",
    "tiktok": "@roberto_oficial",
    "ref1_name": "Ana Patricia López",
    "ref1_relation": "amigo",
    "ref2_name": "Carlos Eduardo Silva",
    "ref2_relation": "familiar",
    "monthly_income": "1200",
    "activity_type": "dependencia",
    "position": "Analista de Sistemas"
  }'
