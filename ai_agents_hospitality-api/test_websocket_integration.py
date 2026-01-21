from fastapi.testclient import TestClient
from main import app
import json
import sys

def test_websocket_integration():
    print("🚀 Starting WebSocket Integration Test")
    print("======================================")
    
    try:
        client = TestClient(app)
        
        # Generate a UUID for the connection
        connection_uuid = "test-uuid-123"
        
        print(f"📡 Connecting to WebSocket at /ws/{connection_uuid}...")
        
        with client.websocket_connect(f"/ws/{connection_uuid}") as websocket:
            # Send a test message
            test_message = "list the hotels in france"
            print(f"📤 Sending message: {test_message}")
            websocket.send_text(test_message)
            
            # Receive response
            print("⏳ Waiting for response...")
            response = websocket.receive_text()
            print(f"📥 Received raw response: {response[:100]}..." if len(response) > 100 else f"📥 Received raw response: {response}")
            
            # Verify response format (JSONSTART...JSONEND)
            if response.startswith("JSONSTART") and response.endswith("JSONEND"):
                json_content = response[9:-7]
                try:
                    data = json.loads(json_content)
                    print("\n📋 Parsed Response Content:")
                    print("-" * 40)
                    print(data.get("content", "No content found"))
                    print("-" * 40)
                    
                    # Check if we got a valid response
                    if "content" in data and len(data["content"]) > 0:
                        print("\n✅ WebSocket integration test PASSED!")
                        return True
                    else:
                        print("\n❌ WebSocket integration test FAILED: Empty content")
                        return False
                except json.JSONDecodeError:
                    print("\n❌ WebSocket integration test FAILED: Invalid JSON content")
                    return False
            else:
                print("\n❌ WebSocket integration test FAILED: Invalid format (missing JSONSTART/JSONEND wrapper)")
                return False
                
    except Exception as e:
        print(f"\n❌ WebSocket integration test FAILED with error: {e}")
        return False

if __name__ == "__main__":
    success = test_websocket_integration()
    sys.exit(0 if success else 1)
