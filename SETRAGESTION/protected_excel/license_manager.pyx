# license_manager.pyx
# Cython module for license protection

import hashlib
import platform
import os
import uuid
from datetime import datetime, timedelta

def get_machine_fingerprint():
    """Get a unique fingerprint of the machine"""
    try:
        # Get system info
        system = platform.system()
        node = platform.node()
        machine = platform.machine()
        processor = platform.processor()
        
        # Get CPU info
        cpu_count = os.cpu_count()
        
        # Get MAC address
        mac = hex(uuid.getnode())
        
        # Combine all
        fingerprint_data = f"{system}{node}{machine}{processor}{cpu_count}{mac}"
        
        # Hash it
        fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
        return fingerprint
    except:
        return "unknown"

def generate_license_key(fingerprint, expiry_days=365):
    """Generate a license key for the given fingerprint"""
    expiry = datetime.now() + timedelta(days=expiry_days)
    expiry_str = expiry.strftime("%Y%m%d")
    
    key_data = f"{fingerprint}{expiry_str}SETRAF_LICENSE"
    key = hashlib.sha256(key_data.encode()).hexdigest()[:16].upper()
    return key

def verify_license_key(key):
    """Verify if the license key is valid for this machine"""
    try:
        fingerprint = get_machine_fingerprint()
        current_date = datetime.now()
        
        # Try different expiry dates (last 30 days to account for clock differences)
        for days in range(-30, 31):
            test_date = current_date + timedelta(days=days)
            expiry_str = test_date.strftime("%Y%m%d")
            
            key_data = f"{fingerprint}{expiry_str}SETRAF_LICENSE"
            expected_key = hashlib.sha256(key_data.encode()).hexdigest()[:16].upper()
            
            if expected_key == key:
                return True
        
        return False
    except:
        return False

def check_license():
    """Check if license is valid, return True/False"""
    license_file = os.path.join(os.path.dirname(__file__), "license.key")
    
    if not os.path.exists(license_file):
        return False
    
    try:
        with open(license_file, "r") as f:
            key = f.read().strip()
        
        return verify_license_key(key)
    except:
        return False

def create_license_file():
    """Create a license file for this machine (for development)"""
    fingerprint = get_machine_fingerprint()
    key = generate_license_key(fingerprint)
    
    license_file = os.path.join(os.path.dirname(__file__), "license.key")
    with open(license_file, "w") as f:
        f.write(key)
    
    return key