import datetime
import logging
import asyncio
import azure.functions as func

from .make_call import make_call

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    
    logging.info("Dispatching outbound call...")
    asyncio.run(make_call())
    logging.info("Call dispatch finished.")