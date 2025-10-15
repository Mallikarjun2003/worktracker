Work Hours Tracker - Minimal Django App
=======================================
Run:
  python -m venv venv
  source venv/bin/activate  (or venv\Scripts\activate on Windows)
  pip install -r requirements.txt
  python manage.py migrate
  python manage.py runserver

Features:
- Minimal UI with three buttons: IN, OUT, TRACK.
- Create swipe events (IN/OUT) for a card number (or username).
- Track view computes per-day, per-month worked hours and debt time (expected 8 hrs/day).
- Pairing and lunch-adjusted duration logic implemented in tracker/utils.py (follows the SQL logic you provided).
