import requests
import time
import subprocess

# Start the server in background
process = subprocess.Popen(["uvicorn", "src.api.main:app", "--host", "127.0.0.1", "--port", "8000"])

BASE_URL = "http://127.0.0.1:8000"

# Wait for server to be ready
retries = 10
while retries > 0:
    try:
        requests.get(f"{BASE_URL}/health")
        break
    except:
        time.sleep(1)
        retries -= 1

if retries == 0:
    print("❌ Server failed to start")
    process.terminate()
    exit(1)

USERS = {
    "alice": "token-alice", # admin
    "bob": "token-bob",     # ml_engineer
    "carol": "token-carol", # data_analyst
    "dave": "token-dave",   # intern
}

TEST_CASES = [
    ("alice", "/api/patients/raw", 200),
    ("bob", "/api/patients/raw", 403),
    ("bob", "/api/patients/anonymized", 200),
    ("carol", "/api/patients/anonymized", 403),
    ("carol", "/api/metrics/aggregated", 200),
    ("dave", "/api/metrics/aggregated", 403),
]

try:
    for user_name, endpoint, expected_status in TEST_CASES:
        headers = {"Authorization": f"Bearer {USERS[user_name]}"}
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        print(f"User: {user_name:8} | Endpoint: {endpoint:25} | Expected: {expected_status} | Got: {response.status_code}")
        assert response.status_code == expected_status
    print("\n✅ All RBAC test cases passed!")
finally:
    process.terminate()
