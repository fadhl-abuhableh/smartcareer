import socket
import requests
import json

def get_local_ip():
    """Get the local IP address of this machine"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't have to be reachable, just for the socket to obtain local IP
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def check_server():
    """Check if the server is running and display full URL information"""
    local_ip = get_local_ip()
    print(f"Local IP address: {local_ip}")
    
    # Build URL for update-profile endpoint
    update_profile_url = f"http://{local_ip}:5000/api/update-profile"
    test_connection_url = f"http://{local_ip}:5000/api/test-connection"
    
    print(f"\nUpdate Profile URL: {update_profile_url}")
    print(f"Test Connection URL: {test_connection_url}")
    
    # Test the test-connection endpoint with full IP
    try:
        # First try localhost to verify the server is running
        localhost_response = requests.get("http://localhost:5000/api/test-connection")
        print(f"\nServer status on localhost: {localhost_response.status_code}")
        
        # Then try the full IP address
        ip_response = requests.get(test_connection_url)
        print(f"Server status on {local_ip}: {ip_response.status_code}")
        
        print("\nSERVER IS ACCESSIBLE FROM THE NETWORK")
        print("Make sure your Android app is using this URL pattern:")
        print(f"http://{local_ip}:5000/api/update-profile")
        
    except requests.exceptions.ConnectionError:
        print("\nWARNING: Server is not accessible on the network IP!")
        print("Make sure you're running Flask with host='0.0.0.0'")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    check_server() 