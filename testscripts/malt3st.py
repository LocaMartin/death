import socket
import sys
import time

# --- Configuration ---
TARGET_FILE = (input('enter file name: '))
FUZZ_PAYLOAD_LENGTH = 4096  # Length of the repeating 'A's
FUZZ_BYTE = b'\x41'         # Hex for 'A'
# Other ideas for FUZZ_BYTE: b'\x90' (NOP sled), b'\x00' (null byte), random bytes

CONNECTION_TIMEOUT = 5 # seconds
RECEIVE_TIMEOUT = 5    # seconds
RETRY_DELAY = 1        # seconds before retrying connection

# --- Fuzzing Function ---
def fuzz_port(host, port, service_name, payload):
    print(f"[+] Fuzzing {host}:{port} ({service_name}) with {len(payload)} bytes...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(CONNECTION_TIMEOUT)

    try:
        sock.connect((host, port))
        sock.settimeout(RECEIVE_TIMEOUT) # Set receive timeout after connection

        # Send the payload
        sock.sendall(payload)
        print(f"    Payload sent. Waiting for response...")

        # Try to read response for a short period
        # Look for unusual responses, errors, or no response (indicating crash)
        try:
            response = sock.recv(4096)
            if response:
                print(f"    [+] Response received (hex): {response.hex()}")
                print(f"    [+] Response received (text): {response.decode(errors='ignore').strip()}")
            else:
                print("    [!] No response or connection closed gracefully.")
        except socket.timeout:
            print("    [!] Read timeout: No response after sending payload.")
        except Exception as e:
            print(f"    [!] Error receiving response: {e}")

    except ConnectionRefusedError:
        print(f"    [-] Connection refused by {host}:{port}.")
    except socket.timeout:
        print(f"    [!] Connection timeout for {host}:{port}. Service might be slow or crashed.")
    except Exception as e:
        print(f"    [!] An unexpected error occurred with {host}:{port}: {e}")
    finally:
        sock.close()
        # Small delay between tests to not overwhelm the target or get blocked
        time.sleep(RETRY_DELAY)

# --- Main Execution ---
if __name__ == "__main__":
    if not FUZZ_PAYLOAD_LENGTH or not FUZZ_BYTE:
        print("Error: FUZZ_PAYLOAD_LENGTH and FUZZ_BYTE must be set.")
        sys.exit(1)

    # Generate the fuzzer payload
    fuzz_payload = FUZZ_BYTE * FUZZ_PAYLOAD_LENGTH
    print(f"Generated fuzz payload: {FUZZ_BYTE.hex()} repeated {FUZZ_PAYLOAD_LENGTH} times.")

    try:
        with open(TARGET_FILE, 'r') as f:
            targets = f.readlines()

        if not targets:
            print(f"No targets found in {TARGET_FILE}. Run nmap scan first.")
            sys.exit(0)

        for line in targets:
            line = line.strip()
            if not line:
                continue

            parts = line.split(':')
            if len(parts) == 3:
                host = parts[0]
                port = int(parts[1])
                service = parts[2]
                fuzz_port(host, port, service, fuzz_payload)
            else:
                print(f"Skipping malformed line in {TARGET_FILE}: {line}")

    except FileNotFoundError:
        print(f"Error: Target file '{TARGET_FILE}' not found. Please run the nmap scan first.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during script execution: {e}")

    print("\n[+] Fuzzing complete.")
