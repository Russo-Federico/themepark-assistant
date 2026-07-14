_WAIT_TIMES = [
    {"attraction": "Peak Assault", "area": "adventure_world", "wait_minutes": 70},
    {"attraction": "Neon Circuit", "area": "future_world", "wait_minutes": 65},
    {"attraction": "Thunder Rapids", "area": "adventure_world", "wait_minutes": 35},
    {"attraction": "Orbit Station", "area": "future_world", "wait_minutes": 30},
    {"attraction": "Dragon Flight", "area": "fable_world", "wait_minutes": 25},
    {"attraction": "Jungle Trek", "area": "adventure_world", "wait_minutes": 10},
    {"attraction": "Data Dive", "area": "future_world", "wait_minutes": 8},
]


def get_all_wait_times() -> list[dict]:
    return [row.copy() for row in _WAIT_TIMES]
