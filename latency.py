import json
import os
import numpy as np

def add_cors(headers):
    headers["Access-Control-Allow-Origin"] = "*"
    headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    headers["Access-Control-Allow-Headers"] = "Content-Type"
    return headers

def handler(request):

    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": add_cors({}),
            "body": ""
        }

    body = request.get_json()

    regions = body["regions"]
    threshold = body["threshold_ms"]

    data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "telemetry.json"
    )

    with open(data_path, "r", encoding="utf-8") as f:
        rows = json.load(f)

    result = {}

    for region in regions:
        subset = [r for r in rows if r["region"] == region]

        latencies = [r["latency_ms"] for r in subset]
        uptimes = [r["uptime_pct"] for r in subset]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 3),
            "breaches": sum(
                1 for x in latencies if x > threshold
            )
        }

    return {
        "statusCode": 200,
        "headers": add_cors({
            "Content-Type": "application/json"
        }),
        "body": json.dumps(result)
    }