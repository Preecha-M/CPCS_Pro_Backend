from datetime import datetime, timedelta

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..core.templates import templates
from ..core.mongo import col_predictions, DESCENDING


router = APIRouter()

@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    selected_date = request.query_params.get("date") or datetime.now().strftime("%Y-%m-%d")
    selected_lat = request.query_params.get("lat") or "13.10"
    selected_lon = request.query_params.get("lon") or "100.10"
    page = int(request.query_params.get("page", 1))
    per_page = 5
    skip = (page - 1) * per_page
    max_date = (datetime.now() + timedelta(days=126)).strftime("%Y-%m-%d")



    cursor = col_predictions.find(
        {},
        {
            "_id": 0,
            "user_id": 1,
            "display_name": 1,
            "image_url": 1,
            "prediction": 1,
            "timestamp": 1,
            "address": 1,
            "latitude": 1,
            "longitude": 1,
            "disease": 1,
            "confidence": 1,
        },
    ).sort("timestamp", DESCENDING).skip(skip).limit(per_page)

    records = list(cursor)
    for r in records:
        if "image_url" in r and "image_path" not in r:
            r["image_path"] = r["image_url"]

    total_records = col_predictions.count_documents({})
    total_pages = (total_records + per_page - 1) // per_page

    pipeline_disease = [
        {"$group": {"_id": "$disease", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    disease_counts_list = list(col_predictions.aggregate(pipeline_disease))
    disease_counts_dict = {(x["_id"] or "Unknown"): x["count"] for x in disease_counts_list}

    pipeline_timeseries = [
        {"$match": {"date": {"$exists": True, "$ne": None}, "disease": {"$exists": True, "$ne": None}}},
        {"$group": {"_id": {"date": "$date", "disease": "$disease"}, "count": {"$sum": 1}}},
        {"$sort": {"_id.date": 1}},
    ]
    ts_rows = list(col_predictions.aggregate(pipeline_timeseries))
    dates_set, diseases_set, ts_map = set(), set(), {}
    for row in ts_rows:
        d = row["_id"]["date"]
        dz = row["_id"]["disease"]
        dates_set.add(d)
        diseases_set.add(dz)
        ts_map[(d, dz)] = row["count"]
    sorted_dates = sorted(dates_set)
    sorted_diseases = sorted(diseases_set)
    time_series_datasets = [{"label": dz, "data": [ts_map.get((d, dz), 0) for d in sorted_dates]} for dz in sorted_diseases]

    heat_points = []
    for d in col_predictions.find({"latitude": {"$ne": None}, "longitude": {"$ne": None}}, {"_id": 0, "latitude": 1, "longitude": 1}):
        try:
            heat_points.append([float(d["latitude"]), float(d["longitude"]), 1])
        except Exception:
            pass

    pipeline_grouped = [
        {"$match": {"address": {"$exists": True}, "disease": {"$exists": True}}},
        {"$group": {"_id": {"address": "$address", "disease": "$disease"}, "count": {"$sum": 1}}},
        {"$sort": {"_id.address": 1}},
    ]
    gb_rows = list(col_predictions.aggregate(pipeline_grouped))
    addresses_set, diseases2_set, gb_map = set(), set(), {}
    for row in gb_rows:
        addr = row["_id"]["address"] or "ไม่ระบุสถานที่"
        dz = row["_id"]["disease"]
        addresses_set.add(addr)
        diseases2_set.add(dz)
        gb_map[(addr, dz)] = row["count"]
    grouped_locations = sorted(addresses_set)
    grouped_datasets = [{"label": dz, "data": [gb_map.get((addr, dz), 0) for addr in grouped_locations]} for dz in sorted(diseases2_set)]

    pipeline_bubble = [
        {"$match": {"latitude": {"$ne": None}, "longitude": {"$ne": None}, "disease": {"$ne": None}}},
        {"$project": {"lat": {"$round": ["$latitude", 5]}, "lon": {"$round": ["$longitude", 5]}, "disease": 1}},
        {"$group": {"_id": {"lat": "$lat", "lon": "$lon", "disease": "$disease"}, "count": {"$sum": 1}}},
    ]
    bubble_rows = list(col_predictions.aggregate(pipeline_bubble))
    bubble_points = [{"lat": float(r["_id"]["lat"]), "lon": float(r["_id"]["lon"]), "count": int(r["count"]), "disease": r["_id"]["disease"]} for r in bubble_rows]

    confidence_values = []
    for x in col_predictions.find({"confidence": {"$ne": None}}, {"_id": 0, "confidence": 1}):
        try:
            confidence_values.append(float(x["confidence"]))
        except Exception:
            pass

    loc_top = list(
        col_predictions.aggregate(
            [
                {"$group": {"_id": "$address", "total": {"$sum": 1}}},
                {"$sort": {"total": -1}},
                {"$limit": 1},
            ]
        )
    )
    most_common_location = (loc_top[0]["_id"] if loc_top else "ไม่พบข้อมูล") or "ไม่ระบุสถานที่"

    users_count_rows = list(col_predictions.aggregate([{"$group": {"_id": "$user_id"}}, {"$count": "num"}]))
    total_users = users_count_rows[0]["num"] if users_count_rows else 0

    summary = {"total_users": total_users, "most_common_location": most_common_location, "disease_summary": disease_counts_dict}

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "records": records,
            "page": page,
            "total_pages": total_pages,
            "summary": summary,
            "total_records": total_records,
            "disease_counts": disease_counts_dict,
            "time_series_labels": sorted_dates,
            "time_series_datasets": time_series_datasets,
            "heat_points": heat_points,
            "grouped_locations": grouped_locations,
            "grouped_datasets": grouped_datasets,
            "bubble_points": bubble_points,
            "confidence_values": confidence_values,

            "selected_date": selected_date,
            "selected_lat": selected_lat,
            "selected_lon": selected_lon,
            "max_date": max_date,

        },
    )
