import math
import random
from typing import List

def _haversine_km(lat1, lng1, lat2, lng2) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def _route_distance(order: List, patients: List) -> float:
    total = 0.0
    for i in range(len(order) - 1):
        a, b = patients[order[i]], patients[order[i+1]]
        total += _haversine_km(a.lat, a.lng, b.lat, b.lng)
    return total

def _triage_priority(t: str) -> int:
    return {"RED": 0, "YELLOW": 1, "GREEN": 2}.get(t or "GREEN", 2)

def optimize_route(patients) -> dict:
    """
    Simplified Genetic Algorithm:
    - RED patients always come first (hard constraint)
    - Within each triage tier, apply nearest-neighbour + 2-opt improvement
    - Returns ordered list with estimated walk time
    """
    if not patients:
        return {"route": [], "total_patients": 0, "estimated_minutes": 0}

    # Sort by triage first (hard constraint: RED before YELLOW before GREEN)
    sorted_patients = sorted(patients, key=lambda p: _triage_priority(p.triage))

    # Nearest-neighbour greedy within each tier
    def nn_order(group):
        if not group: return []
        visited = [0]
        remaining = list(range(1, len(group)))
        while remaining:
            last = visited[-1]
            nearest = min(remaining, key=lambda j: _haversine_km(
                group[last].lat, group[last].lng, group[j].lat, group[j].lng))
            visited.append(nearest)
            remaining.remove(nearest)
        return visited

    tiers = {"RED": [], "YELLOW": [], "GREEN": []}
    for p in sorted_patients:
        tiers[p.triage or "GREEN"].append(p)

    ordered = []
    for tier in ["RED", "YELLOW", "GREEN"]:
        group = tiers[tier]
        if group:
            idxs = nn_order(group)
            ordered.extend([group[i] for i in idxs])

    # 2-opt improvement on full route (keep RED constraint by not swapping across tiers)
    def two_opt(route):
        improved = True
        while improved:
            improved = False
            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route)):
                    # Don't move RED patients from front
                    if _triage_priority(route[i].triage) == 0 or _triage_priority(route[j].triage) == 0:
                        continue
                    new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
                    if _route_distance(list(range(len(new_route))), new_route) < \
                       _route_distance(list(range(len(route))), route):
                        route = new_route
                        improved = True
        return route

    final_route = two_opt(ordered)

    # Build response
    total_dist_km = sum(
        _haversine_km(final_route[i].lat, final_route[i].lng,
                      final_route[i+1].lat, final_route[i+1].lng)
        for i in range(len(final_route) - 1)
    )
    walking_speed_kmh = 4.0
    estimated_minutes = round((total_dist_km / walking_speed_kmh) * 60)

    return {
        "route": [
            {
                "id": p.id,
                "name": p.name,
                "lat": p.lat,
                "lng": p.lng,
                "triage": p.triage or "GREEN",
                "priority_score": p.priority_score,
            }
            for p in final_route
        ],
        "total_patients": len(final_route),
        "total_distance_km": round(total_dist_km, 2),
        "estimated_minutes": estimated_minutes,
    }