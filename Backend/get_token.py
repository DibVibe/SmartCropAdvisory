#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartCropAdvisory.settings')
django.setup()

from Apps.UserManagement.mongo_models import MongoUser
from django.test import Client
import json

print("=== GETTING VALID AUTH TOKEN ===")

# Set a known password for the test user
test_user = MongoUser.objects(username='testuser').first()
if test_user:
    # Set password
    test_user.set_password('newpassword123')
    test_user.save()
    print(f"✅ Password set for user: {test_user.username}")
    
    # Test login via API
    client = Client()
    login_data = {
        'username': 'testuser', 
        'password': 'newpassword123'
    }
    
    response = client.post('/api/v1/users/login/', 
        json.dumps(login_data),
        content_type='application/json'
    )
    
    print(f"Login status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('token'):
            print("🎉 SUCCESS!")
            print(f"Valid token: {data['token']}")
            print(f"\n=== COPY THIS TO POSTMAN ===")
            print(f"Authorization: Bearer {data['token']}")
            print(f"\nURL: http://localhost:8000/api/v1/advisory/farms/cdeb3e33-cced-4582-92c1-b9f46f35cc6b/dashboard/")
        else:
            print(f"❌ Login failed: {data}")
    else:
        print(f"❌ HTTP Error: {response.content.decode()}")
        
else:
    print("❌ No testuser found in MongoDB")

print("\n=== ALTERNATIVE: LOGIN VIA POSTMAN ===")
print("POST http://localhost:8000/api/v1/users/login/")
print("Body: {")
print('  "username": "testuser",')
print('  "password": "newpassword123"')
print("}")
