import datetime
import logging
import azure.functions as func

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    logging.info(f"[mytimer] Timer triggered at {utc_timestamp}")