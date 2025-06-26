
# PwnCheck - Pwned Password Checker


## Overview

**PwnCheck** is a Python-based tool that scans a list of passwords (from a CSV file) to determine if they have been compromised in known data breaches. It utilizes the **Have I Been Pwned (HIBP) Pwned Passwords API**, which allows secure and anonymous checking of passwords via the **k-Anonymity** model. This means the script never sends a full password (or its complete hash) to the API. Instead, it only uses the first 5 characters of the SHA-1 hash of each password, receiving a list of matching hash suffixes and breach counts in return. By comparing against the full hash, PwnCheck can tell you if a password appears in the breached-password database and how many times it has been seen, without revealing the password to any third party.

## Features

- Secure password checking using k-Anonymity model.
- Counts how many times a password appears in breach datasets.
- CSV integration for bulk checking.
- Multi-threaded password scanning.
- LRU cache for reused passwords.
- Docker support.
- Fully configurable via CLI.

## Requirements

- Python 3.7+
- `requests`, `pandas`, `numpy`

## Installation

### Local

```bash
git clone https://github.com/mirawara/pwncheck.git
cd pwncheck
pip install -r requirements.txt
```

### Docker

```bash
docker build -t pwncheck .
docker run --rm -v "$(pwd)/account.csv:/app/account.csv" pwncheck account.csv --account_name_col "Account" --password_col "Password"
```

## Usage

### Basic

```bash
python pwncheck.py account.csv --account_name_col "Account" --password_col "Password"
```

### Options

- `--maxsize`: Cache size (default: 1000)
- `--max_workers`: Number of threads (default: 10)
- `--delimiter`: CSV delimiter (default: ',')
- `--encoding`: CSV encoding (default: ISO-8859-1)

## Example CSV

```
Account,Password,Username,URL,Note
"Google","password123","user1@gmail.com","https://accounts.google.com","Account Google"
"Facebook","password456","user2@facebook.com","https://www.facebook.com","Account Facebook"
"Twitter","mypassword789","user3@twitter.com","https://www.twitter.com","Account Twitter"
"LinkedIn","securepass","user4@linkedin.com","https://www.linkedin.com","Account LinkedIn"
```

## Project Structure

- `pwncheck.py`: Main script.
- `Dockerfile`: Container configuration.
- `requirements.txt`: Python dependencies.
- `account.csv`: Sample CSV input.

## Potential Improvements and Tips

This project is fully functional, but there are several ways it could be improved or extended:

- **HTTP Request Headers:** Currently, the script doesn't set a custom User-Agent header in the API requests. According to HIBP API guidelines, you should include a descriptive User-Agent string identifying your application. This can help HIBP operators see who is using the service and is generally good practice. For example, one could modify requests.get(url) to requests.get(url, headers={"User-Agent": "PwnCheck/1.0"}). In some cases, not providing a User-Agent might result in a 403 Forbidden response, so this is a recommended improvement.

- **Output Options:** Currently, results are printed to standard output. You might add an option to save results to a file (e.g., output a CSV of compromised accounts, or generate a report). This could be useful for large scans where you want to keep a record of which accounts need attention.

- **Password Exposure in Output:** The output lists the password in plain text alongside the account. While this is convenient, be mindful if you share or store this output - it contains sensitive data. An improvement could be to omit the actual password in the report (since you already know which account's password is compromised, and printing the password isn't strictly necessary). Or, mask it (e.g., show only the first 2 characters). This is more about operational security when using the tool.

- **Performance Tuning:** The default thread count (10) and caching (1000 entries) can be adjusted. If you have a very large CSV (say tens of thousands of entries), you could increase --max_workers to use more threads if your internet connection and the HIBP service can handle it. However, since HIBP has no set rate limit for Pwned Passwords, the main bottleneck will be your network and HIBP's own throughput. Monitor for any HTTP 429 responses (too many requests) just in case. You could also experiment with an asynchronous approach (using asyncio and an HTTP client like aiohttp) for potentially better performance, though that would add complexity.

- **Memory Usage:** Using pandas to read the entire CSV is easy, but for extremely large files you might want to stream through the file instead of loading everything into memory at once. A possible enhancement is to iterate over the CSV using Python's built-in CSV reader or pandas chunks. Given most use cases and modern memory sizes, this is usually not an issue for reasonable CSV sizes.

- **NTLM Hash Option:** HIBP's API can also work with NTLM hashes (for Windows environment passwords) by adding ?mode=ntlm to the URL. This script is hardcoded for SHA-1 (which is the default and what you'd want for checking plain passwords). It's unlikely you need NTLM mode unless integrating specifically with Windows hashed passwords, but it's something to note as a possible extension.

- **Using Offline Data:** HIBP provides downloadable dumps of all compromised password hashes (SHA-1 and NTLM). For very high-volume or offline use, one could download the corpus and check passwords locally without hitting the API. This project doesn't do that (it relies on the live API, which is always up-to-date), but if you needed to check millions of passwords regularly, an offline check might be faster. Keep in mind the data set is huge (tens of gigabytes).

## 📄 License

This project is licensed under the [MIT License](LICENSE).

You are free to use, modify, and distribute this software, as long as the original copyright and license notice are included.

# Buy me a coffee ☕
[paypal.me/mirawara](https://paypal.me/mirawara)

---
© Lorenzo Mirabella - PwnCheck