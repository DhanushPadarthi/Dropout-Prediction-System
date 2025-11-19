import requests
import json

def test_api_endpoints():
    base_url = "http://127.0.0.1:8000"
    
    endpoints = [
        "/",
        "/health/",
        "/test/",
        "/api/students/dashboard-stats/",
        "/api/students/analytics/"
    ]
    
    print("Testing Django API endpoints...")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:100]}...")
            else:
                print(f"   Error: {response.text[:100]}...")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: Connection failed - {e}")
        print("-" * 30)

if __name__ == "__main__":
    test_api_endpoints()