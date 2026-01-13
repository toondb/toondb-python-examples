
import time

# Scale
NUM_EVENTS = 50000 # Telemetry logs
NUM_MANUAL_CHUNKS = 500
DB_PATH = "./sochdb_data_manufacturing"
VECTOR_DIM = 1536

# Time
NOW = int(time.time())
ONE_DAY = 86400
START_TIME = NOW - ONE_DAY

# Device Data
DEVICE_ID = "device_007"
STATES = ["RUNNING", "IDLE", "ERROR", "MAINTENANCE"]
ERROR_CODES = {
    "E142": "Overheat shutdown triggered by thermal sensor.",
    "E200": "Power supply voltage fluctuation detected.",
    "E555": "Network latency exceeded threshold.",
    "E300": "Hydraulic pressure loss in main valve."
}
