from datetime import datetime, timedelta
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from ..core.auth import get_current_user_from_cookie
from ..core.mongo import col_predictions, DESCENDING
from ..core.disease_colors import disease_color_map
import traceback

router = APIRouter()

CONFIDENCE_THRESHOLD = 0.45  # แสดงผลเฉพาะรายการที่ confidence >= 0.45




@router.get("/admin/dashboard")
async def admin_dashboard_json(request: Request):
    try:
        # payload = get_current_user_from_cookie(request)
        # if payload.get("role") not in ("admin", "researcher"):
        #     return JSONResponse({"detail": "Forbidden"}, status_code=403)
        pass

        selected_date = request.query_params.get("date") or datetime.now().strftime("%Y-%m-%d")
        selected_lat = request.query_params.get("lat") or "13.10"
        selected_lon = request.query_params.get("lon") or "100.10"
        page = int(request.query_params.get("page", 1))
        per_page = 5
        skip = (page - 1) * per_page
        max_date = (datetime.now() + timedelta(days=126)).strftime("%Y-%m-%d")



        cursor = col_predictions.find({"confidence": {"$gte": CONFIDENCE_THRESHOLD}},
            {
                "_id": 1,
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
        # Convert ObjectId to string for JSON serialization
        for record in records:
            if "_id" in record:
                record["_id"] = str(record["_id"])

        total_records = col_predictions.count_documents({"confidence": {"$gte": CONFIDENCE_THRESHOLD}})
        total_pages = (total_records + per_page - 1) // per_page

        pipeline_disease = [
            {"$match": {"confidence": {"$gte": CONFIDENCE_THRESHOLD}, "disease": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": "$disease", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        disease_counts_list = list(col_predictions.aggregate(pipeline_disease))
        disease_counts_dict = {(x["_id"] or "Unknown"): x["count"] for x in disease_counts_list}

        pipeline_timeseries = [
            {"$match": {"date": {"$exists": True, "$ne": None}, "disease": {"$exists": True, "$ne": None}, "confidence": {"$gte": CONFIDENCE_THRESHOLD}}},
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
        # รวมจุดพิกัดให้เป็นกลุ่ม (ปัดทศนิยม) เพื่อให้ heatmap แสดงความหนาแน่นได้ถูกต้อง
        pipeline_heat = [
            {"$match": {"confidence": {"$gte": CONFIDENCE_THRESHOLD}, "latitude": {"$ne": None}, "longitude": {"$ne": None}}},
            {"$project": {"lat": {"$round": ["$latitude", 4]}, "lon": {"$round": ["$longitude", 4]}}},
            {"$group": {"_id": {"lat": "$lat", "lon": "$lon"}, "count": {"$sum": 1}}},
        ]
        for r in col_predictions.aggregate(pipeline_heat):
            try:
                heat_points.append([float(r["_id"]["lat"]), float(r["_id"]["lon"]), float(r["count"])])
            except Exception:
                pass

        pipeline_grouped = [
            {"$match": {"address": {"$exists": True}, "disease": {"$exists": True}, "confidence": {"$gte": CONFIDENCE_THRESHOLD}}},
            {"$group": {"_id": {"address": "$address", "disease": "$disease"}, "count": {"$sum": 1}}},
            {"$sort": {"_id.address": 1}},
        ]
        gb_rows = list(col_predictions.aggregate(pipeline_grouped))
        addresses_set, diseases2_set, gb_map = set(), set(), {}
        for row in gb_rows:
            addr = row["_id"]["address"] or "ไม่ระบุสถานที่"
            dz = row["_id"]["disease"] or "Unknown"
            addresses_set.add(addr)
            diseases2_set.add(dz)
            gb_map[(addr, dz)] = row["count"]
        grouped_locations = sorted(addresses_set)
        grouped_datasets = [{"label": dz, "data": [gb_map.get((addr, dz), 0) for addr in grouped_locations]} for dz in sorted(diseases2_set)]

        pipeline_bubble = [
            {"$match": {"latitude": {"$ne": None}, "longitude": {"$ne": None}, "disease": {"$ne": None}, "confidence": {"$gte": CONFIDENCE_THRESHOLD}}},
            {"$project": {"lat": {"$round": ["$latitude", 5]}, "lon": {"$round": ["$longitude", 5]}, "disease": 1}},
            {"$group": {"_id": {"lat": "$lat", "lon": "$lon", "disease": "$disease"}, "count": {"$sum": 1}}},
        ]
        bubble_rows = list(col_predictions.aggregate(pipeline_bubble))
        bubble_points = [{"lat": float(r["_id"]["lat"]), "lon": float(r["_id"]["lon"]), "count": int(r["count"]), "disease": r["_id"]["disease"]} for r in bubble_rows]

        confidence_values = []
        for x in col_predictions.find({"confidence": {"$gte": CONFIDENCE_THRESHOLD}}, {"_id": 0, "confidence": 1}):
            try:
                confidence_values.append(float(x["confidence"]))
            except Exception:
                pass

        loc_top = list(
            col_predictions.aggregate(
                [
                    {"$match": {"confidence": {"$gte": CONFIDENCE_THRESHOLD}}},
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

        all_diseases = set()

        for k in (disease_counts_dict or {}).keys():
            all_diseases.add(k or "Unknown")

        for ds in (time_series_datasets or []):
            all_diseases.add(ds.get("label") or "Unknown")

        for ds in (grouped_datasets or []):
            all_diseases.add(ds.get("label") or "Unknown")
        for p in (bubble_points or []):
            all_diseases.add(p.get("disease") or "Unknown")

        for r in (records or []):
            all_diseases.add(r.get("disease") or "Unknown")
        disease_colors = disease_color_map(sorted(all_diseases))
        
        return {
            "selected_date": selected_date,
            "selected_lat": selected_lat,
            "selected_lon": selected_lon,
            "max_date": max_date,
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
            "records": records,
            "page": page,
            "total_pages": total_pages,
            "disease_colors": disease_colors,
        }
    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse({"detail": str(e), "trace": traceback.format_exc()}, status_code=500)

@router.delete("/admin/history/{record_id}")
async def delete_history_record(record_id: str, request: Request):
    payload = get_current_user_from_cookie(request)
    if payload.get("role") != "admin":
        return JSONResponse({"detail": "Admin only"}, status_code=403)

    try:
        from bson import ObjectId
        res = col_predictions.delete_one({"_id": ObjectId(record_id)})
        if res.deleted_count == 0:
            return JSONResponse({"detail": "Record not found"}, status_code=404)
        return {"ok": True}
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=400)
