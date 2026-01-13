"""
Simple API Test Script
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def run_test():
    print("=" * 40)
    print("SIMPLE BACKEND TEST")
    print("=" * 40)

    # 1. Test Root
    try:
        print("\n1. Testing Connection (GET /)...")
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return

    # 2. Test New Game
    try:
        print("\n2. Testing New Game (POST /game/new)...")
        response = requests.post(
            f"{BASE_URL}/game/new",
            json={"starting_scenario": "Test scenario."}
        )
        if response.status_code == 200:
            print(f"✅ Success! Session created.")
            print(f"   Session ID: {response.json().get('session_id')}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ Test Failed: {e}")

    print("\n" + "=" * 40)

if __name__ == "__main__":
    run_test()
