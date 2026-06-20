from alpenmechanik_data import run_pipeline
import logging

logger = logging.getLogger()


def lambda_handler(event, context):
    try:
        logger.info("Lambda invocation started")
        result = run_pipeline()

        logger.info("Lambda invocation successful")

        return {
            "statusCode": 200,
            "body": result
        }

    except Exception as exc:
        logger.exception("Lambda invocation failed")
        return {
            "statusCode": 500,
            "body": {
                "status": "failed",
                "error": str(exc)
            }
        }