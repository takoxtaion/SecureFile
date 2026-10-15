# SecureFile

A desktop **File Integrity Monitoring (FIM)** application built with Python and PyQt6. SecureFile watches folders you choose, detects when files are modified or deleted, keeps backups of the original files, and lets authorized users restore tampered files with one click.

## Features

- **Integrity monitoring**: computes a SHA-256 hash of every file in a watched folder and compares it on each scan.
- **Tamper detection**: files are flagged as `SECURE`, `TAMPERED`, or `DELETED`.
- **Automatic backups**: a safe copy of each file is saved when a folder is first added, and another one is saved whenever tampering is detected.
- **One-click restore**: restore a tampered file from its original safe backup.
- **User accounts**: register and sign in; the first registered user automatically becomes the admin.
- **Role-based access control**: `admin` and `user` roles with `READ`, `WRITE`, and `EXECUTE` access levels.
- **Approval workflow**: regular users can request folder monitoring or a permission upgrade, and admins approve or review the requests.
- **Audit log**: logins, scans, tamper alerts, and restores are recorded with timestamps.

## Permission model

| Role / Level | Can do |
|---|---|
| **admin** | Add/remove monitored folders, scan, restore, view logs and backups, approve requests |
| **user** with `READ` (default) | View monitored folders and file statuses |
| **user** with `WRITE` | Everything in `READ`, plus run scans |
| **user** with `EXECUTE` | Everything in `WRITE`, plus restore files |

New accounts start with `READ`. Users can request an upgrade from the dashboard, and an admin approves it in the **Requests** tab.

## Project structure

```
SecureFile/
├── mian.py        # Application entry point
├── interface.py   # PyQt6 GUI (login, dashboard, logs, backups, requests)
├── auth.py        # Registration and login (AuthService)
├── database.py    # SQLite storage (DatabaseManager)
└── monitor.py     # Hashing, scanning, backup and restore (SecurityEngine)
```

## Requirements

- Python 3.8 or newer
- [PyQt6](https://pypi.org/project/PyQt6/)

SecureFile uses only the Python standard library (`sqlite3`, `hashlib`, `shutil`, etc.) beyond PyQt6.

## Installation

```bash
# Clone the repository
git clone https://github.com/takoxtaion/SecureFile.git
cd SecureFile

# (Optional) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install PyQt6
```

## Usage

```bash
python mian.py
```

1. **Register** the first account. It becomes the **admin**.
2. **Sign in**, then open the **Monitoring** tab.
3. **Add a folder** (admin). SecureFile hashes every file in it and creates the initial safe backups.
4. Click **Scan** at any time to check for changes. Modified files are marked `TAMPERED` and deleted files `DELETED`.
5. Select a file and click **Restore** to bring back the original version.

Regular users can register their own accounts, then use **Request Monitoring** or **Request Upgrade**. Admins handle these in the **Requests** tab.

## How it works

1. When a folder is added, every file is hashed with SHA-256 and copied to `backups/<id>/` as an `INITIAL_SAFE_*` backup.
2. On **Scan**, each file is re-hashed and compared with its stored hash.
   - Different hash → the file is backed up as a `TAMPER_EVENT_*` copy and marked `TAMPERED`.
   - File missing → marked `DELETED`.
3. On **Restore**, the earliest `INITIAL_SAFE_*` backup replaces the current file. Close the file in other programs first, or the restore will fail.

## Data storage

SecureFile creates these in the directory it is run from:

| Path | Contents |
|---|---|
| `system_vault.db` | SQLite database with `users`, `watched_files`, `logs`, and `access_requests` tables |
| `backups/` | Initial and tamper-event copies of monitored files |


