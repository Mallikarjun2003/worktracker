from collections import defaultdict
from datetime import datetime, time
from typing import Dict, List, Tuple
from django.utils import timezone

from .models import Swipe


# ---------- Helpers ----------

def _ensure_aware(dt: datetime) -> datetime:
    tz = timezone.get_current_timezone()
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, tz)
    return dt


def minutes_between(a: datetime, b: datetime) -> int:
    """Whole minutes between a and b (b - a)."""
    a = _ensure_aware(a)
    b = _ensure_aware(b)
    return int((b - a).total_seconds() // 60)


def overlap_minutes(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> int:
    start = max(a_start, b_start)
    end = min(a_end, b_end)
    if end <= start:
        return 0
    return minutes_between(start, end)


def lunch_adjusted_minutes(in_dt: datetime, out_dt: datetime) -> int:
    """
    Subtract any overlap with local lunch window (13:00-14:00) from the interval.
    Both inputs may be naive or aware; we normalize using Django timezone.
    """
    in_dt = _ensure_aware(in_dt)
    out_dt = _ensure_aware(out_dt)

    local_in = timezone.localtime(in_dt)
    local_out = timezone.localtime(out_dt)

    work_date = local_in.date()
    tz = timezone.get_current_timezone()
    lunch_start = timezone.make_aware(datetime.combine(work_date, time(13, 0)), tz)
    lunch_end = timezone.make_aware(datetime.combine(work_date, time(14, 0)), tz)

    total = minutes_between(local_in, local_out)
    lunch_overlap = overlap_minutes(local_in, local_out, lunch_start, lunch_end)

    return max(0, total - lunch_overlap)


# ---------- Core: compute_stats_for_card ----------

def compute_stats_for_card(card_no: str) -> Dict[str, List[Dict]]:
    """
    Compute per-day and per-month worked minutes for a card.

    Pairing rule: pair by occurrence index per day:
      - Build list of IN timestamps and list of OUT timestamps for the day (ordered).
      - Pair IN[i] with OUT[i] for i = 0 .. min(len(INs), len(OUTs)) - 1.
      - Skip pairs where OUT <= IN.
      - Subtract lunch overlap per pair.
    """
    qs = Swipe.objects.filter(card_no=card_no).order_by('time')

    # Group events by local date
    grouped = defaultdict(list)  # date -> list of (local_dt, reader_name)
    for s in qs:
        local_dt = timezone.localtime(_ensure_aware(s.time))
        grouped[local_dt.date()].append((local_dt, s.reader_name))

    per_day = []
    expected_daily_minutes = 8 * 60
    total_month_minutes = defaultdict(int)

    for d in sorted(grouped.keys()):
        events = grouped[d]
        # Ensure chronological order (defensive)
        events.sort(key=lambda t: t[0])

        # Process events sequentially. An IN opens (or replaces) an open interval.
        # An OUT closes the currently open IN (if any). OUTs without an open IN
        # are ignored. Repeated INs before an OUT replace the previous IN (correction).
        open_in: datetime | None = None
        pairs: List[Tuple[datetime, datetime, int]] = []
        for evt_time, reader in events:
            name = (reader or '').upper()
            if name.endswith('IN'):
                # set or replace the current open IN
                open_in = evt_time
            elif name.endswith('OUT'):
                if open_in is None:
                    # unmatched OUT; ignore
                    continue
                out_t = evt_time
                if out_t <= open_in:
                    # invalid ordering; ignore this OUT
                    continue
                mins = minutes_between(open_in, out_t)
                pairs.append((open_in, out_t, int(mins or 0)))
                open_in = None
            else:
                # unknown reader type: ignore
                continue

        total_mins = sum(p[2] for p in pairs)
        if total_mins <= 0:
            # keep same behavior as SQL HAVING SUM(DurationMinutes) > 0 (optionally skip)
            per_day.append({
                'date': d.isoformat(),
                'worked_minutes': 0,
                'worked_human': "0 hrs 0 mins",
                'debt_minutes': expected_daily_minutes,
                'debt_human': f"{expected_daily_minutes//60} hrs {expected_daily_minutes%60} mins",
                'pairs': [],
            })
        else:
            debt = max(0, expected_daily_minutes - total_mins)
            # Build human readable pairs (e.g., '11:44 AM → 11:46 AM (2 mins)')
            human_pairs = []
            for in_t, out_t, mins in pairs:
                # localize times for display
                try:
                    local_in = timezone.localtime(in_t)
                    local_out = timezone.localtime(out_t)
                except Exception:
                    local_in = in_t
                    local_out = out_t
                in_str = local_in.strftime('%Y-%m-%d %I:%M %p')
                out_str = local_out.strftime('%Y-%m-%d %I:%M %p')
                human_pairs.append(f"{in_str} → {out_str} ({mins} mins)")

            per_day.append({
                'date': d.isoformat(),
                'worked_minutes': total_mins,
                'worked_human': f"{total_mins//60} hrs {total_mins%60} mins",
                'debt_minutes': debt,
                'debt_human': f"{debt//60} hrs {debt%60} mins",
                'pairs': [(p[0].isoformat(), p[1].isoformat(), p[2]) for p in pairs],
                'pairs_human': human_pairs,
            })

        key = f"{d.year}-{d.month:02d}"
        total_month_minutes[key] += total_mins

    months = []
    for k in sorted(total_month_minutes.keys()):
        mins = total_month_minutes[k]
        months.append({'month': k, 'minutes': mins, 'human': f"{mins//60} hrs {mins%60} mins"})

    return {'per_day': per_day, 'months': months}
