import os
import logging
from dotenv import load_dotenv
from datetime import datetime
from cloudwatch import cloudwatch

load_dotenv()

logging.addLevelName(25, "METADATA")

logger_metadata = logging.getLogger(__name__)
logger_metadata.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger_metadata.addHandler(console_handler)

now = datetime.now()
current_time = now.strftime("%Y_%m")
log_stream_name = f"{current_time}_metadata"

cloudwatch_handler_metadata = cloudwatch.CloudwatchHandler(
    region='us-east-1',
    log_group = 'scraper_metadata',
    log_stream= log_stream_name,
    access_id = os.getenv("AWS_ACCESS_ID"), 
    access_key = os.getenv("AWS_ACCESS_PASSWORD")
)
cloudwatch_handler_metadata.setLevel(logging.DEBUG)
cloudwatch_handler_metadata.setFormatter(formatter)
logger_metadata.addHandler(cloudwatch_handler_metadata)

