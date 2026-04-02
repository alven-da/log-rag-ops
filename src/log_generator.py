import json
import random
import uuid
from datetime import datetime, timedelta

services = ["auth-service", "order-service", "payment-service", "shipping-worker"]
levels = ["INFO", "WARN", "ERROR"]
messages = {
    "INFO": ["User session started", "Cache hit for key: <HEX>", "API request completed in <DURATION>"],
    "WARN": ["High memory usage: 85%", "Slow query detected in <SERVICE>", "Rate limit approaching for IP <IP>"],
    "ERROR": ["Connection timeout at <IP>", "Failed to process payment for <UUID>", "UNCAUGHT_EXCEPTION: NullPointer at line <PID>"]
}

logs = []
start_time = datetime.utcnow()

for i in range(512):
    lvl = random.choices(levels, weights=[70, 20, 10])[0]
    svc = random.choice(services)
    msg = random.choice(messages[lvl])
    
    # Inject high-cardinality noise for your Regex parser to clean later
    msg = msg.replace("<IP>", f"192.168.1.{random.randint(1, 254)}")
    msg = msg.replace("<UUID>", str(uuid.uuid4()))
    msg = msg.replace("<HEX>", hex(random.getrandbits(16)))
    msg = msg.replace("<DURATION>", f"{random.randint(100, 5000)}ms")
    msg = msg.replace("<SERVICE>", svc)
    msg = msg.replace("<PID>", str(random.randint(1000, 9999)))

    logs.append({
        "timestamp": (start_time + timedelta(seconds=i)).isoformat() + "Z",
        "service": svc,
        "level": lvl,
        "message": msg,
        "request_id": f"req-{str(uuid.uuid4())[:8]}",
        "trace_id": str(uuid.uuid4())
    })

with open('src/data/raw_logs/logs.json', 'w') as f:
    json.dump(logs, f, indent=2)

print(f"Successfully generated 512 logs in logs.json")