#!/usr/bin/env python3
"""
LongPlay Studio License Manager
Simple serial key validation system
"""

import os
import json
import hashlib
import platform
from pathlib import Path
from datetime import datetime

# ==================== Configuration ====================
APP_NAME = "LongPlay Studio"
APP_VERSION = "4.24f"
LICENSE_FILE = ".longplay_license"

# Secret salt for key generation (change this for your own app!)
SECRET_SALT = "LongPlay_MrArranger_2024_Secret_Key"

# Valid serial prefixes (you can generate more)
VALID_PREFIXES = ["LP24", "LPRO", "LPVIP"]


def get_license_path() -> Path:
    """Get the license file path in user's home directory"""
    return Path.home() / LICENSE_FILE


def get_machine_id() -> str:
    """Get a unique machine identifier"""
    # Combine multiple system identifiers
    machine_info = f"{platform.node()}-{platform.machine()}-{platform.processor()}"
    return hashlib.md5(machine_info.encode()).hexdigest()[:12].upper()


def generate_serial_key(prefix: str = "LP24", custom_id: str = None) -> str:
    """
    Generate a valid serial key
    Format: PREFIX-XXXX-XXXX-XXXX
    
    Args:
        prefix: Key prefix (LP24, LPRO, LPVIP)
        custom_id: Optional custom identifier for the key
    """
    if prefix not in VALID_PREFIXES:
        prefix = "LP24"
    
    # Generate unique parts
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    unique_id = custom_id or hashlib.md5(os.urandom(16)).hexdigest()[:8]
    
    # Create key parts
    combined = f"{SECRET_SALT}-{prefix}-{timestamp}-{unique_id}"
    hash_value = hashlib.sha256(combined.encode()).hexdigest().upper()
    
    # Format: PREFIX-XXXX-XXXX-XXXX
    part1 = hash_value[:4]
    part2 = hash_value[4:8]
    part3 = hash_value[8:12]
    
    return f"{prefix}-{part1}-{part2}-{part3}"


def validate_serial_key(serial: str) -> tuple[bool, str]:
    """
    Validate a serial key
    
    Returns:
        (is_valid, message)
    """
    if not serial:
        return False, "Serial key is empty"
    
    # Clean up input
    serial = serial.strip().upper()
    
    # Check format: PREFIX-XXXX-XXXX-XXXX
    parts = serial.split("-")
    if len(parts) != 4:
        return False, "Invalid format. Expected: XXXX-XXXX-XXXX-XXXX"
    
    prefix = parts[0]
    
    # Check prefix
    if prefix not in VALID_PREFIXES:
        return False, f"Invalid prefix. Expected one of: {', '.join(VALID_PREFIXES)}"
    
    # Check each part length
    if not all(len(p) == 4 for p in parts[1:]):
        return False, "Invalid format. Each part should be 4 characters"
    
    # Check if all parts are alphanumeric
    if not all(p.isalnum() for p in parts):
        return False, "Invalid characters in serial key"
    
    # Additional validation: checksum verification
    # For simplicity, we'll accept any key with valid format and prefix
    # In production, you'd verify against a database or algorithm
    
    return True, f"Valid {get_license_type(prefix)} license"


def get_license_type(prefix: str) -> str:
    """Get license type from prefix"""
    types = {
        "LP24": "Standard",
        "LPRO": "Professional",
        "LPVIP": "VIP Lifetime"
    }
    return types.get(prefix, "Standard")


def save_license(serial: str, customer_name: str = "") -> bool:
    """Save license to file"""
    try:
        license_data = {
            "serial": serial.strip().upper(),
            "customer_name": customer_name,
            "machine_id": get_machine_id(),
            "activated_at": datetime.now().isoformat(),
            "app_version": APP_VERSION
        }
        
        license_path = get_license_path()
        with open(license_path, "w") as f:
            json.dump(license_data, f, indent=2)
        
        # Make file hidden on Unix systems
        if os.name != 'nt':
            os.chmod(license_path, 0o600)
        
        return True
    except Exception as e:
        print(f"Error saving license: {e}")
        return False


def load_license() -> dict:
    """Load license from file"""
    try:
        license_path = get_license_path()
        if license_path.exists():
            with open(license_path, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading license: {e}")
    return {}


def check_license() -> tuple[bool, str, dict]:
    """
    Check if the application is licensed
    
    Returns:
        (is_licensed, message, license_data)
    """
    license_data = load_license()
    
    if not license_data:
        return False, "No license found", {}
    
    serial = license_data.get("serial", "")
    is_valid, message = validate_serial_key(serial)
    
    if not is_valid:
        return False, message, license_data
    
    # Optional: Check machine ID (prevent copying license to other machines)
    # stored_machine_id = license_data.get("machine_id", "")
    # current_machine_id = get_machine_id()
    # if stored_machine_id != current_machine_id:
    #     return False, "License is registered to a different machine", license_data
    
    return True, message, license_data


def remove_license() -> bool:
    """Remove the license file"""
    try:
        license_path = get_license_path()
        if license_path.exists():
            os.remove(license_path)
        return True
    except Exception as e:
        print(f"Error removing license: {e}")
        return False


# ==================== Pre-generated Serial Keys ====================
# You can generate and sell these keys
# Run: python -c "from license_manager import generate_serial_key; print(generate_serial_key('LP24'))"

SAMPLE_KEYS = """
# Sample valid keys for testing (generate your own for production!):
# 
# Standard License (LP24):
#   LP24-A1B2-C3D4-E5F6
#
# Professional License (LPRO):  
#   LPRO-X1Y2-Z3W4-V5U6
#
# VIP Lifetime License (LPVIP):
#   LPVIP-1234-5678-9ABC
"""


if __name__ == "__main__":
    # Test key generation
    print("=" * 50)
    print("LongPlay Studio - License Key Generator")
    print("=" * 50)
    
    print("\n📝 Generating sample keys:\n")
    
    for prefix in VALID_PREFIXES:
        key = generate_serial_key(prefix)
        license_type = get_license_type(prefix)
        print(f"  {license_type}: {key}")
    
    print("\n" + "=" * 50)
    print("💡 To validate a key:")
    print('   python -c "from license_manager import validate_serial_key; print(validate_serial_key(\'LP24-XXXX-XXXX-XXXX\'))"')
    print("=" * 50)
