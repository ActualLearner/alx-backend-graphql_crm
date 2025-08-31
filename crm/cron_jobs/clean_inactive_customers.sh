#!/bin/bash

# --- Configuration ---
PROJECT_ROOT="/home/pc/projects/alx-backend-graphql_crm/"
LOG_FILE="/tmp/customer_cleanup_log.txt"

# --- Main Script ---

cd "$PROJECT_ROOT" || {
  echo "Error: Project directory not found at $PROJECT_ROOT"
  exit 1
}

echo "Running inactive customer cleanup job..."

# The output of this block (the number printed by the Python script)
# will be captured in the DELETED_COUNT variable.
DELETED_COUNT=$(
  python manage.py shell <<EOF
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order  # Make sure to import your actual models

one_year_ago = timezone.now() - timedelta(days=365)

active_customer_ids = Customer.objects.filter(
    order__created_at__gte=one_year_ago
).values_list('id', flat=True).distinct()

inactive_customers = Customer.objects.exclude(id__in=active_customer_ids)

count_to_delete = inactive_customers.count()

if count_to_delete > 0:
    inactive_customers.delete()

print(count_to_delete)
EOF
)

# Check if the command executed successfully
if [ $? -eq 0 ]; then
  # Get the current timestamp in a nice format
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

  # Log the result by appending to the log file
  echo "$TIMESTAMP: Successfully deleted $DELETED_COUNT inactive customers." >>"$LOG_FILE"
  echo "Job finished. Logged to $LOG_FILE"
else
  # Log an error if the Django command failed
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
  echo "$TIMESTAMP: Error executing Django customer cleanup command." >>"$LOG_FILE"
  echo "Job failed. Check the log for details: $LOG_FILE"
fi
