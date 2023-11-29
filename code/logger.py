import os
import logging
from dotenv import load_dotenv
from datetime import datetime
from cloudwatch import cloudwatch

load_dotenv()

logger_scraper = logging.getLogger()
logger_scraper.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger_scraper.addHandler(console_handler)

now = datetime.now()
current_time = now.strftime("%Y_%m_%d")
log_stream_name = f"{current_time}_logs"

# CloudWatch Handler
cloudwatch_handler = cloudwatch.CloudwatchHandler(
    region='us-east-1',
    log_group = 'scraper_logs',
    log_stream= log_stream_name,
    access_id = os.getenv("AWS_ACCESS_ID"), 
    access_key = os.getenv("AWS_ACCESS_PASSWORD")
)
cloudwatch_handler.setLevel(logging.DEBUG)
cloudwatch_handler.setFormatter(formatter)
logger_scraper.addHandler(cloudwatch_handler)
