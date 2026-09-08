from datetime import datetime

def log_event(node_name: str, action: str, details: str):
    """
    Logs an event in the format:
    [TIMESTAMP] [NODE_NAME] [ACTION] -> Details
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{node_name.upper()}] [{action.upper()}] -> {details}")
