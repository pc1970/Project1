# Glamour Hair Salon – Setup & User Guide

## Table of Contents
1. [Requirements](#1-requirements)
2. [Quick Start (Development)](#2-quick-start-development)
3. [Configuration – SMS & Email](#3-configuration--sms--email)
4. [Loading Sample Data](#4-loading-sample-data)
5. [Using the App](#5-using-the-app)
6. [Building the Windows Installer](#6-building-the-windows-installer)
7. [File Overview](#7-file-overview)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Requirements

| Software | Version | Download |
|---|---|---|
| Python | 3.10 or newer | https://www.python.org/downloads/ |
| pip | bundled with Python | – |
| NSIS *(Windows installer only)* | 3.x | https://nsis.sourceforge.io |

---

## 2. Quick Start (Development)

Open a terminal, navigate to the `hairsalon/` folder, then run:

```bash
# 1 – Install Python dependencies
pip install -r requirements.txt

# 2 – Copy the example config and fill in your credentials
cp .env.example .env
#   (edit .env with your Twilio and SMTP details – see Section 3)

# 3 – (Optional) Load sample data
python seed_data.py

# 4 – Start the server
python app.py
```

Open your browser at **http://localhost:5000**

The database file (`salon.db`) is created automatically on first run.
To change the port, set `PORT=8080` (or any port) in your `.env` file.

---

## 3. Configuration – SMS & Email

Copy `.env.example` to `.env` and fill in the values below.
The app runs fine without them – notifications are simply skipped and a warning is logged.

### SMS via Twilio

1. Create a free account at **https://www.twilio.com**
2. From the Twilio Console, copy your **Account SID** and **Auth Token**
3. Buy or use a trial phone number (must be SMS-capable)

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+15551234567
```

> **Trial accounts:** Twilio trial accounts can only send SMS to verified numbers.
> Verify your test phone at Console → Phone Numbers → Verified Caller IDs.

### Email via SMTP

The app uses standard SMTP, so it works with any provider.

**Gmail example** (recommended for testing):
1. Enable 2-Step Verification on your Google account
2. Generate an **App Password**: Google Account → Security → App Passwords
3. Use the 16-character App Password as `SMTP_PASSWORD` (not your normal password)

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
SMTP_FROM=your@gmail.com
SMTP_FROM_NAME=Glamour Hair Salon
SMTP_USE_TLS=1
```

**Outlook / Office 365:**
```
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
```

**SendGrid:**
```
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
```

### When notifications fire

| Event | SMS | Email |
|---|---|---|
| New appointment booked | ✓ | ✓ |
| Appointment cancelled | ✓ | ✓ |
| Manual reminder (bell icon) | ✓ | ✓ |

---

## 4. Loading Sample Data

Running `seed_data.py` populates the database with:

- **3 staff members** – Sophia (Senior Stylist), James (Colorist), Ava (Junior Stylist)
- **8 services** – Women's Cut, Men's Cut, Full Color, Highlights, Balayage, Keratin Treatment, Deep Conditioning, Blowout & Style
- **10 customers** with names, emails, and phone numbers
- **15 appointments** spread across past, today, and upcoming dates

```bash
python seed_data.py
```

You can run it multiple times safely – it checks for duplicates before inserting.

To reset the database entirely, just delete `salon.db` and restart `app.py`.

---

## 5. Using the App

### Dashboard
- Shows today's appointment count, confirmed revenue, total customers, and active staff at a glance
- Lists all upcoming appointments (next 10) in a table

### Appointments tab
- **Filter** by date, status (scheduled / confirmed / completed / cancelled), or free-text search
- **New Appointment** button opens a modal – fill in customer, stylist, service, date/time
  - A confirmation SMS + email is sent automatically when you save
- **Bell icon** (🔔) on any row sends a manual reminder to the customer
- **Edit icon** opens the same modal pre-filled for updates
  - Changing status to *cancelled* automatically fires a cancellation notification
- **Trash icon** permanently deletes the appointment
- The **Notified** column shows envelope/SMS icons in green if the last notification was delivered successfully

### Services tab
- View all services as cards showing name, description, duration, and price
- Add, edit, or delete services

### Customers tab
- Searchable list (name, email, or phone)
- **History icon** opens a panel showing all past visits and lifetime spend
- Add, edit, or delete customers
- Customer phone and email are the addresses used for all notifications

### Staff tab
- Staff cards with initials avatar, role, contact details, and active status
- Add, edit (including toggling active/inactive), or remove staff

---

## 6. Building the Windows Installer

### Step 1 – Create the executable

From the `hairsalon/` directory:

```bash
pip install pyinstaller
python build_windows.py
```

This produces `dist/GlamourSalon/` containing `GlamourSalon.exe` and all dependencies.

### Step 2 – Create the installer package

1. Install **NSIS 3.x** from https://nsis.sourceforge.io/Download
2. Right-click `installer.nsi` → *Compile NSIS Script*
   **or** run from a terminal:
   ```
   makensis installer.nsi
   ```
3. The output is `GlamourSalonSetup-1.0.0.exe` – a standard Windows installer

### What the installer does
- Copies all files to `C:\Program Files\GlamourHairSalon\`
- Creates a Desktop shortcut
- Creates a Start Menu folder
- Registers the app in Add/Remove Programs (so it can be cleanly uninstalled)

### Running the installed app
Double-click the desktop shortcut. The app starts a local web server and you open **http://localhost:5000** in your browser.

> **Tip:** To have the browser open automatically on launch, you can add a small launcher script (e.g., a `.bat` file that runs the exe and then calls `start http://localhost:5000`).

---

## 7. File Overview

```
hairsalon/
├── app.py              Flask application & all API routes
├── database.py         SQLite connection helpers
├── schema.sql          Database schema (tables & columns)
├── notifications.py    SMS (Twilio) and email (smtplib) logic
├── seed_data.py        Sample data loader
├── requirements.txt    Python package dependencies
├── .env.example        Template for environment variables
├── build_windows.py    PyInstaller build script
├── installer.nsi       NSIS Windows installer script
├── templates/
│   └── index.html      Single-page frontend (TailwindCSS)
└── static/
    └── js/
        └── app.js      Frontend API calls & UI logic
```

### API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/dashboard/stats` | Summary stats + upcoming appointments |
| GET / POST | `/api/appointments` | List (with filters) / create appointment |
| GET / PUT / DELETE | `/api/appointments/<id>` | Get, update, or delete one appointment |
| POST | `/api/appointments/<id>/remind` | Send manual reminder notification |
| GET / POST | `/api/services` | List / create services |
| PUT / DELETE | `/api/services/<id>` | Update or delete a service |
| GET / POST | `/api/staff` | List / create staff |
| PUT / DELETE | `/api/staff/<id>` | Update or delete a staff member |
| GET / POST | `/api/customers` | List (searchable) / create customers |
| GET / PUT / DELETE | `/api/customers/<id>` | Get (with history), update, or delete |

---

## 8. Troubleshooting

**App won't start**
- Make sure Python 3.10+ is installed: `python --version`
- Run `pip install -r requirements.txt` again

**"No module named flask" error**
- Your virtual environment may not be active. Try `pip install flask flask-cors python-dotenv`

**SMS not sending**
- Check `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_FROM_NUMBER` in `.env`
- Trial accounts can only message verified numbers
- Check the terminal output for error details

**Email not sending**
- For Gmail, make sure you are using an **App Password**, not your account password
- Check that `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, and `SMTP_PASSWORD` are all set
- Try `SMTP_USE_TLS=1` (default) – some servers require `SMTP_USE_TLS=0`

**Database errors after upgrade**
- If you see column-not-found errors, delete `salon.db` and restart – it will be recreated with the latest schema

**Port already in use**
- Set a different port in `.env`: `PORT=8080`
- Or kill the process using port 5000: `lsof -ti:5000 | xargs kill` (macOS/Linux)
