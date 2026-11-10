# Sweet Mother Kitchen: Daily Sales Report System

A web application that records restaurant sales and produces accurate daily
sales reports, replacing handwritten exercise books.

> **Status:** In development (Sprint 1). Built for the COSC361 / BIT301
> "Code for Community" project. Uses test data only; no real customer or
> personal information is stored.

## The Problem

Sweet Mother Kitchen prepares its daily sales report by hand. Totals are
often wrong, payments from different methods (cash, mobile money, card) get
mixed up, and past reports are hard to find. The owner cannot trust the
figures or easily compare one day with another.

## Features

| Feature | Description | Status |
|---|---|---|
| Sales Entry | Record each sale: items grouped by category, quantity, unit price, live totals, payment method | Done |
| Login and roles | Staff login with Cashier, Manager and Owner roles | Done |
| Void handling | Managers void mistaken sales with a recorded reason; voided sales are excluded from totals | Done |
| Daily Sales Report | Gross, voids and net sales, sales by payment method and category, best sellers, previous-day comparison | Done |
| Report Archive | Search past days by date range, view each day's report and export to CSV | Done |

## Users

- **Cashiers / waitresses:** record each sale
- - **Manager:** reviews sales and voids mistaken ones
- **Owner:** reads daily reports and compares days

## Tech Stack

- **Backend:** Python, Django 5.0
- **Database:** MySQL (MariaDB, via XAMPP)
- **Frontend:** HTML, CSS and JavaScript (Django templates)
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
│   │   └── setup_roles.py   Creates the Cashier, Manager and Owner groups
│   ├── migrations/          Database migrations
│   ├── templates/
│   │   ├── registration/    Login page
│   │   └── sales/           Base layout, home, sales entry, sales list, reports
│   ├── models.py            Category, MenuItem, Sale, SaleLine
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
- [XAMPP](https://www.apachefriends.org/) with MySQL (MariaDB 10.4 or newer)

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

4. Start **MySQL** in the XAMPP Control Panel. Then open
   `http://localhost/phpmyadmin`, click the **SQL** tab, and run:
   ```sql
   CREATE DATABASE smk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

5. Check the `DATABASES` block in `config/settings.py`. The defaults are user
   `root`, an empty password, host `127.0.0.1` and port `3306`. Change them
   if your XAMPP setup is different.

6. Create the tables, test data and roles:
   ```bash
   python manage.py migrate
   python manage.py seed_menu
   python manage.py setup_roles
   ```

7. Create an admin account:
   ```bash
   python manage.py createsuperuser
   ```

### Running the app

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` and log in. The `/admin/` site is for managing
users and menu items.

### Troubleshooting

| Problem | Fix |
|---|---|
| `Couldn't import Django` | Activate the virtual environment: `venv\Scripts\activate` |
| `ALLOWED_HOSTS` error | Make sure `DEBUG = True` in `config/settings.py` |
| Can't connect to MySQL | Start MySQL in XAMPP and check the port in `settings.py` |
| `MariaDB 10.11 or later is required` | Install the pinned Django: `pip install -r requirements.txt` |
| Empty item dropdown | Run `python manage.py seed_menu` |

## Usage Guide

### Roles

| Role | Signs in and sees | Can do |
|---|---|---|
| Cashier | Goes straight to the **New Sale** form | Record sales |
| Manager | Home page with **New Sale**, **Sales List**, **Daily Report** and **Report Archive** | Record sales, void mistakes, view reports |
| Owner | Home page with **New Sale**, **Daily Report** and **Report Archive** | View reports and export CSV |

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

## Team


| Member | Role |
|---|---|
| Desmond Zambogunaa | Quality and Documentation Lead |
| Comfort Akorfa Yikpa | Product Owner |
| Mohammed Osman | Scrum Master |


### Viewing reports (managers and owners)

1. Click **Daily Report** on the home page and choose a date. It shows gross
   sales, voids, net sales, sales by payment method and category, best sellers
   and the day's voided sales, with a comparison to the previous day.
2. Click **Report Archive** to see one row per day. Choose a start and end
   date and click **Search**, then **View** to open that day's full report.
3. Click **Export CSV** to download the rows in the chosen date range and open
   them in Excel.

Net sales are gross sales minus voided sales.

## Roadmap

- [x] Database schema and data models
- [x] Seed test menu items
- [x] Sales Entry form with live totals
- [x] Payment method selector
- [x] Login page, navigation and user roles
- [x] Void handling for managers
- [x] Daily Sales Report
- [x] Report Archive with search and CSV export
- [ ] Kitchen production log and shop closing report (to be confirmed with the client)

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
