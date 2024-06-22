from poe_api.config.config_model import Api_Metrics
import uvicorn
from poe_api.util.logging import logger


# run rest api server with defined router and api-metrics
def rest_server(metrics:Api_Metrics):
    logger.info(f'Initiating Server {metrics.host}:{metrics.port}/{metrics.version} workers={metrics.num_workers}')
    uvicorn.run(f"poe_api.api.{metrics.version}:app",host=metrics.host, port=metrics.port, workers=metrics.num_workers,log_level=metrics.loglevel,timeout_keep_alive=15,timeout_graceful_shutdown=20)
