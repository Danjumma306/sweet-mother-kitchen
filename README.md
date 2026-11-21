# Sweet Mother's Kitchen: Daily Sales Report System

A web application that records restaurant sales and produces accurate daily
sales reports, replacing handwritten exercise books.

> **Status:** Core features complete. Built for the COSC361 / BIT301
> "Code for Community" project. Uses test data only; no real customer or
> personal information is stored.

## The Problem

Sweet Mother's Kitchen prepares its daily sales report by hand. Totals are
often wrong, payments from different methods (cash, mobile money, card) get
mixed up, and past reports are hard to find. The owner cannot trust the
figures or easily compare one day with another.

## Features

| Feature | Description | Status |
|---|---|---|
| Sales Entry | Record each sale: items grouped by category, quantity, unit price, live totals, payment method | Done |
| Login and roles | Staff login with Cashier, Kitchen, Manager and Owner roles | Done |
| Void handling | Managers void mistaken sales with a recorded reason; voided sales are excluded from totals | Done |
| Daily Sales Report | Gross, voids and net sales, sales by payment method and category, best sellers, previous-day comparison | Done |
| Report Archive | Search past days by date range, view each day's report and export to CSV | Done |
| Kitchen Production Log | Kitchen staff record how much of each menu item was prepared that day | Done |
| Shop Closing Report | Cashiers record leftovers, sold-out items, and cash counted against expected cash sales | Done |
| Staff POS UI | Role-based sidebar navigation and refreshed staff screens for day-to-day use | Done |

## Users

- **Cashiers / waitresses:** record each sale and complete the shop closing report
- **Kitchen staff:** record daily production quantities
- **Manager:** reviews sales, voids mistakes, views reports, and can use kitchen and closing screens
- **Owner:** reads daily reports and compares days

## Tech Stack

- **Backend:** Python, Django 5.0
- **Database:** MySQL (MariaDB, via XAMPP) by default; SQLite available via `DB_ENGINE=sqlite`
- **Frontend:** HTML, CSS and JavaScript (Django templates)
- **Config:** Environment variables for `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` and database settings
- **Version control:** Git and GitHub (issues and a Projects board)

> Django is pinned to 5.0 in `requirements.txt` because XAMPP's MariaDB 10.4
> is too old for newer Django versions.

## Project Structure

```
sweet-mother-kitchen/
├── config/                  Django project settings and main URLs
├── sales/                   The main app
│   ├── management/commands/
│   │   ├── seed_menu.py     Loads test menu items
│   │   └── setup_roles.py   Creates Cashier, Kitchen, Manager and Owner groups
│   ├── migrations/          Database migrations
│   ├── static/sales/        CSS and JavaScript for the staff UI
│   ├── templates/
│   │   ├── registration/    Login page
│   │   └── sales/           Base layout, home, sales, kitchen, closing, reports
│   ├── constants.py         Brand, nav and UI constants
│   ├── context_processors.py Role-based navigation helpers
│   ├── models.py            Category, MenuItem, Sale, SaleLine, KitchenEntry,
│   │                        ClosingEntry, CashCount
│   ├── views.py             Page logic
│   └── urls.py              Sales URLs
├── manage.py
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or newer
- Git
- [XAMPP](https://www.apachefriends.org/) with MySQL (MariaDB 10.4 or newer),
  unless you use SQLite (see below)

### Installation

1. Clone the repository and open the folder:
   ```bash
   git clone https://github.com/Danjumma306/sweet-mother-kitchen.git
   cd sweet-mother-kitchen
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
   Your prompt should start with `(venv)`. On macOS or Linux, use
   `source venv/bin/activate`.

3. Install the packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Choose a database:

   **MySQL (default):** Start MySQL in the XAMPP Control Panel. Then open
   `http://localhost/phpmyadmin`, click the **SQL** tab, and run:
   ```sql
   CREATE DATABASE smk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

   Defaults are user `root`, empty password, host `127.0.0.1` and port `3306`.
   Override with `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` and `DB_PORT`
   if needed.

   **SQLite (local/dev alternative):**
   ```bash
   set DB_ENGINE=sqlite
   ```
   On macOS or Linux: `export DB_ENGINE=sqlite`.

5. Create the tables, test data and roles:
   ```bash
   python manage.py migrate
   python manage.py seed_menu
   python manage.py setup_roles
   ```

6. Create an admin account:
   ```bash
   python manage.py createsuperuser
   ```

### Running the app

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` and log in. The `/admin/` site is for managing
users and menu items. Assign each user to the right group (Cashier, Kitchen,
Manager or Owner) in the admin.

### Deployment notes

For production, set environment variables instead of editing code:

| Variable | Purpose | Example |
|---|---|---|
| `SECRET_KEY` | Django secret | a long random string |
| `DEBUG` | Debug mode (`True` / `False`) | `False` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `example.com,www.example.com` |
| `DB_ENGINE` | `mysql` (default) or `sqlite` | `mysql` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | MySQL connection | as for your host |

When `DEBUG` is `False`, secure session and CSRF cookies are enabled.

### Troubleshooting

| Problem | Fix |
|---|---|
| `Couldn't import Django` | Activate the virtual environment: `venv\Scripts\activate` |
| `ALLOWED_HOSTS` error | Set `ALLOWED_HOSTS` (and keep `DEBUG=True` only for local work) |
| Can't connect to MySQL | Start MySQL in XAMPP and check `DB_*` env vars or defaults |
| `MariaDB 10.11 or later is required` | Install the pinned Django: `pip install -r requirements.txt` |
| Empty item dropdown | Run `python manage.py seed_menu` |

## Usage Guide

### Roles

| Role | Can access | Can do |
|---|---|---|
| Cashier | New Sale, Shop Closing | Record sales; save leftovers, sold-out items and cash counted |
| Kitchen | Kitchen Log | Record quantities prepared for each menu item |
| Manager | New Sale, Sales List, Kitchen Log, Shop Closing, Daily Report, Report Archive | Record sales, void mistakes, kitchen/closing logs, view and export reports |
| Owner | Daily Report, Report Archive | View reports and export CSV |

### Recording a sale

1. Log in at `/login/` and open **New Sale**.
2. Choose an item from the dropdown (grouped by category) and set the quantity.
   The unit price and line total fill in automatically.
3. Click **+ Add item** for more lines.
4. Choose the payment method (Cash, Mobile Money or Card).
5. Click **Save sale**. A green message confirms the total.

### Voiding a sale (managers)

1. Open **Sales List** from the home page and pick a date.
2. Type a reason next to the sale and click **Void**, then confirm.
3. The sale stays in the records, marked **Voided** with the reason and the
   manager's name, and is left out of the day's total.

### Kitchen production log (kitchen staff and managers)

1. Open **Kitchen Log**.
2. Enter how many of each item were prepared today.
3. Click **Save**. Entries can be updated again on the same day.

### Shop closing report (cashiers and managers)

1. Open **Shop Closing** at the end of the day.
2. For each item, enter leftovers and tick **Sold out** when nothing remains.
   Sold quantities for the day are shown for reference.
3. Enter **Cash counted** and an optional note. Expected cash from cash sales
   and any difference are shown on the page.
4. Click **Save closing report**.

### Viewing reports (managers and owners)

1. Click **Daily Report** on the home page and choose a date. It shows gross
   sales, voids, net sales, sales by payment method and category, best sellers
   and the day's voided sales, with a comparison to the previous day.
2. Click **Report Archive** to see one row per day. Choose a start and end
   date and click **Search**, then **View** to open that day's full report.
3. Click **Export CSV** to download the rows in the chosen date range and open
   them in Excel.

Net sales are gross sales minus voided sales.

## Team

| Member | Role |
|---|---|
| Desmond Zambogunaa | Quality and Documentation Lead |
| Comfort Akorfa Yikpa | Product Owner |
| Mohammed Osman | Scrum Master |

## Roadmap

- [x] Database schema and data models
- [x] Seed test menu items
- [x] Sales Entry form with live totals
- [x] Payment method selector
- [x] Login page, navigation and user roles
- [x] Void handling for managers
- [x] Daily Sales Report
- [x] Report Archive with search and CSV export
- [x] Kitchen production log
- [x] Shop closing report (leftovers, sold-out, cash count)
- [x] Role-based staff UI refresh
- [x] Environment-based settings for deployment

## Contributing

1. Pick an issue and create a branch from an up-to-date `main`:
   ```bash
   git checkout main
   git pull
   git checkout -b feature/<issue-number>-short-name
   ```
2. Commit small, clear changes and push the branch.
3. Open a pull request into `main` and write `Closes #<issue-number>` in the
   description. Add steps for testing the change.
4. Another team member reviews and approves it. Nobody merges their own pull
   request without a review.
5. Merge with **Create a merge commit**, then run `git pull` on `main`.
