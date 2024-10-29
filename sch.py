from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

"""Convert ISO string to a datetime object."""
def to_datetime(iso_str: str) -> datetime:
    return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))

"""Convert a datetime object back to ISO string."""
def to_iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

"""Flatten and sort all busy intervals by start time."""
def flatten_and_sort_intervals(schedules: List[List[Dict[str, str]]]) -> List[Tuple[datetime, datetime]]:
    intervals = [
        (to_datetime(interval['start']), to_datetime(interval['end']))
        for schedule in schedules for interval in schedule
    ]
    return sorted(intervals, key=lambda x: x[0])

"""Merge overlapping or adjacent intervals."""
def merge_intervals(busy_intervals: List[Tuple[datetime, datetime]]) -> List[Tuple[datetime, datetime]]:
    merged = []
    for start, end in busy_intervals:
        if merged and merged[-1][1] >= start:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged

"""Identify free intervals between merged busy intervals."""
def find_free_intervals(merged_intervals: List[Tuple[datetime, datetime]]) -> List[Tuple[datetime, datetime]]:
    free_intervals = []
    day_start = merged_intervals[0][0].replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    # Add free time before the first meeting
    if merged_intervals[0][0] > day_start:
        free_intervals.append((day_start, merged_intervals[0][0]))

    # Add free time between meetings
    for i in range(1, len(merged_intervals)):
        prev_end = merged_intervals[i - 1][1]
        curr_start = merged_intervals[i][0]
        if curr_start > prev_end:
            free_intervals.append((prev_end, curr_start))

    # Add free time after the last meeting
    if merged_intervals[-1][1] < day_end:
        free_intervals.append((merged_intervals[-1][1], day_end))

    return free_intervals

"""Filter free intervals to match the required duration."""
def filter_valid_slots(
    free_intervals: List[Tuple[datetime, datetime]], duration: int
) -> List[Dict[str, str]]:
    valid_slots = []
    for start, end in free_intervals:
        if (end - start).total_seconds() >= duration * 60:
            valid_slots.append({
                "start": to_iso(start),
                "end": to_iso(start + timedelta(minutes=duration))
            })
            if len(valid_slots) == 5:  # Stop after finding 5 slots
                break
    return valid_slots

"""Main function to find available slots."""
def findAvailableSlots(schedules: List[List[Dict[str, str]]], duration: int) -> Optional[List[Dict[str, str]]]:
    if not schedules or duration <= 0:
        return None

    busy_intervals = flatten_and_sort_intervals(schedules)
    merged_intervals = merge_intervals(busy_intervals)
    free_intervals = find_free_intervals(merged_intervals)
    valid_slots = filter_valid_slots(free_intervals, duration)

    return valid_slots if valid_slots else None

"""Test Suite."""
def test_findAvailableSlots():
    schedules = [
        [
            {"start": "2023-10-17T09:00:00Z", "end": "2023-10-17T10:30:00Z"},
            {"start": "2023-10-17T12:00:00Z", "end": "2023-10-17T13:00:00Z"},
            {"start": "2023-10-17T16:00:00Z", "end": "2023-10-17T18:00:00Z"}
        ],
        [
            {"start": "2023-10-17T10:00:00Z", "end": "2023-10-17T11:30:00Z"},
            {"start": "2023-10-17T12:30:00Z", "end": "2023-10-17T14:30:00Z"},
            {"start": "2023-10-17T14:30:00Z", "end": "2023-10-17T15:00:00Z"}
        ],
        [
            {"start": "2023-10-17T11:00:00Z", "end": "2023-10-17T11:30:00Z"},
            {"start": "2023-10-17T12:00:00Z", "end": "2023-10-17T13:30:00Z"},
            {"start": "2023-10-17T14:00:00Z", "end": "2023-10-17T16:30:00Z"}
        ]
    ]
    
    # Corrected expected output based on valid free intervals
    expected = [
        {'start': '2023-10-17T00:00:00Z', 'end': '2023-10-17T00:30:00Z'},
        {'start': '2023-10-17T11:30:00Z', 'end': '2023-10-17T12:00:00Z'},
        {'start': '2023-10-17T18:00:00Z', 'end': '2023-10-17T18:30:00Z'}
    ]
    
    result = findAvailableSlots(schedules, 30)
    assert result == expected, f"Unexpected result: {result}"

# Run the updated test
test_findAvailableSlots()
print("All tests in suite passed.")
