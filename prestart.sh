#!/bin/bash
# Redirect all output to Python logging system

# Create FIFO pipe to capture output
PIPE=/tmp/pipe
mkfifo $PIPE

# Start logger process
python -c "
import sys, logging, os
logging.basicConfig(
    level=os.getenv('LOGGING_LEVEL', 'INFO'),
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger()
while True:
    line = sys.stdin.readline()
    if not line: break
    logger.info(line.strip())
" < $PIPE &

# Redirect all outputs to the pipe
exec > $PIPE 2>&1

# Start FastAPI with original command
uvicorn employee_attrition.api.fast:app \
    --host 0.0.0.0 \
    --port 8080 \
    --no-access-log  # Prevent duplicate logs

# Cleanup (optional)
rm -f $PIPE
