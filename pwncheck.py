import hashlib
import requests
from requests.exceptions import RequestException
from functools import lru_cache
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

@lru_cache(maxsize=None)
def check_password_pwned(password):
    """
    Checks if a given password has been pwned using the Pwned Passwords API.

    Args:
        password (str): The password to check.

    Returns:
        int: The number of times the password has been compromised, or 0 if not found.
    """
    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    first5_hash = sha1_password[:5]
    tail_hash = sha1_password[5:]
    
    url = f'https://api.pwnedpasswords.com/range/{first5_hash}'
    try:
        response = requests.get(url)
        response.raise_for_status()
    except RequestException as e:
        print(f'API Error: {e}')
        return 0
    
    hashes = (line.split(':') for line in response.text.splitlines())
    for h, count in hashes:
        if h == tail_hash:
            return int(count)
    
    return 0

def process_account(account, password):
    """
    Processes an account and password pair to check if the password has been compromised.

    Args:
        account (str): The account name.
        password (str): The password to check.

    Returns:
        tuple or None: A tuple (account, password, count) if the password is compromised,
                        otherwise None.
    """
    count = check_password_pwned(password)
    if count > 0:
        return (account, password, count)
    return None

def check_passwords_in_csv(csv_filename, account_name_col, password_col, max_workers, delimiter, encoding):
    """
    Checks passwords in a CSV file for compromises and returns a list of compromised accounts.

    Args:
        csv_filename (str): Path to the CSV file.
        account_name_col (str): Name of the column containing account names.
        password_col (str): Name of the column containing passwords.
        max_workers (int): Maximum number of concurrent threads.
        delimiter (str): Delimiter used in the CSV file.
        encoding (str): Encoding of the CSV file.

    Returns:
        list: A list of tuples containing (account, password, count) for compromised passwords.
    """
    compromised_accounts = []
    
    df = pd.read_csv(csv_filename, encoding=encoding, delimiter=delimiter)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_account, row[account_name_col], row[password_col]): row
            for _, row in df.iterrows()
        }
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                compromised_accounts.append(result)
    
    return compromised_accounts

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check passwords in a CSV file for compromises.")
    
    parser.add_argument('csv_filename', type=str, help="Path to the CSV file.")
    
    parser.add_argument('--account_name_col', type=str, required=True, help="Name of the column containing account names.")
    parser.add_argument('--password_col', type=str, required=True, help="Name of the column containing passwords.")
    
    parser.add_argument('--maxsize', type=int, default=1000, help="Maximum size of the LRU cache (default: 1000).")
    parser.add_argument('--max_workers', type=int, default=10, help="Maximum number of concurrent threads (default: 10).")
    parser.add_argument('--delimiter', type=str, default=',', help="Delimiter used in the CSV file (default: ',').")
    parser.add_argument('--encoding', type=str, default='ISO-8859-1', help="Encoding of the CSV file (default: 'ISO-8859-1').")
    
    args = parser.parse_args()

    # Set the cache size based on user input
    check_password_pwned = lru_cache(maxsize=args.maxsize)(check_password_pwned)

    compromised_accounts = check_passwords_in_csv(
        args.csv_filename,
        args.account_name_col,
        args.password_col,
        args.max_workers,
        args.delimiter,
        args.encoding
    )
    
    if compromised_accounts:
        print("Accounts with compromised passwords:")
        for account, password, count in compromised_accounts:
            print(f"Account: {account}, Password: {password}, Compromised {count} times.")
    else:
        print("No compromised passwords found.")
