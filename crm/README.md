# CRM Celery Task Setup

This document outlines the steps to set up and run the scheduled Celery tasks for generating weekly CRM reports.

## 1. Setup and Installation

### Install Redis

Celery uses Redis as a message broker. If you don't have it installed, use your system's package manager.

For Debian/Ubuntu/WSL:
```bash
sudo apt update
sudo apt install redis-server
```

### Install Python Dependencies

Install all required Python packages, including Celery and its dependencies.

```bash
# Make sure your virtual environment is activated
pip install -r requirements.txt
```

### Run Database Migrations

`django-celery-beat` uses the database to store its schedule. You must run migrations after adding it to `INSTALLED_APPS`.

```bash
python manage.py migrate```

## 2. Running the Services

To run the automated report generation, you need to run your Django development server, a Celery worker, and the Celery Beat scheduler. **Each of these requires its own separate terminal.**

### Terminal 1: Start the Django Server

```bash
python manage.py runserver
```

### Terminal 2: Start the Celery Worker

The worker is the process that will actually execute your tasks.

```bash
# From your project's root directory (the one with manage.py)
celery -A crm worker -l info
```

### Terminal 3: Start the Celery Beat Scheduler

The "beat" is the process that sends tasks to the worker based on the schedule you defined in `settings.py`.

```bash
# From your project's root directory
celery -A crm beat -l info
```

## 3. Verifying the Logs

The report generation task is scheduled to run **every Monday at 6:00 AM**.

After the scheduled time, you can check the output log to verify that the task ran successfully.

```bash
# Use tail to watch the log file for new entries
tail -f /tmp/crm_report_log.txt
```

You should see entries formatted like this:
```
2025-09-08 06:00:00 - Report: 152 customers, 345 orders, 54321.50 revenue.
```
