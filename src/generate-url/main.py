import uuid
import os
import json

import boto3
from botocore.exceptions import ClientError
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools import Tracer
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricUnit

app = APIGatewayRestResolver()
logger = Logger()
tracer = Tracer()
logger = Logger()
metrics = Metrics(namespace="PowertoolsSample")

dynamodb_client = boto3.client("dynamodb")
s3_client = boto3.client("s3")

s3_bucket_name = os.environ.get("QuarantineBucketName")
dynamodb_table_name = os.environ.get("DynamoDBTableName")


def create_presigned_post(
    bucket_name: str,
    object_name: str,
    fields: dict = None,
    conditions: list = None,
    expiration: int = 600,
):
    """Generate a presigned URL S3 POST request to upload a file

    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    try:
        response = s3_client.generate_presigned_post(
            bucket_name,
            object_name,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logger.error(e)
        return None

    # The response contains the presigned URL and required fields
    return response


@app.post("/")
@tracer.capture_method
def create_url():
    # adding custom metrics
    # See: https://docs.powertools.aws.dev/lambda-python/latest/core/metrics/
    metrics.add_metric(
        name="GeneratePresignedUrlInvocations", unit=MetricUnit.Count, value=1
    )

    id: str = str(uuid.uuid4())

    logger.info(f"Generated id: {id}")

    object_name: str = f"quarantine/{id}/{id}.bin"
    s3_response = create_presigned_post(s3_bucket_name, object_name)

    if s3_response is not None:
        try:
            logger.info(
                f"Creating an entry in the DynamoDB table: {dynamodb_table_name}"
            )
            dynamodb_response = dynamodb_client.put_item(
                TableName=dynamodb_table_name,
                Item={
                    "id": {"S": id},
                    "ContentUrl": {"S": f"s3://{s3_bucket_name}/{object_name}"},
                    "Status": {"S": "PendingUserUpload"},
                    "Properties": {"M": {}},
                },
            )
        except ClientError as e:
            logger.error(e)
            dynamodb_response = None

        if dynamodb_response is not None:
            logger.info(
                "HTTP 202 - Created presigned URL and returning it to the user."
            )

            return {
                "statusCode": 202,
                "body": {
                    "id": id,
                    "text": "Presigned URL created. Please proceed with your upload.",
                    "presignedUrlDetails": {
                        "url": s3_response.get("url"),
                        "fields": s3_response.get("fields"),
                    },
                },
            }
        else:
            logger.error(
                "HTTP Status: 500 - Something went wrong while updating the DB."
            )
            return {
                "statusCode": 500,
                "body": "Something went wrong while updating the database. Please try again later.",
            }
    else:
        logger.error(
            "HTTP Status: 500 - Something went wrong while generating the presigned URL."
        )
        return {
            "statusCode": 500,
            "body": "Something went wrong while generating the presigned URL. Please try again later.",
        }


# Enrich logging with contextual information from Lambda
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
# Adding tracer
# See: https://docs.powertools.aws.dev/lambda-python/latest/core/tracer/
@tracer.capture_lambda_handler
# ensures metrics are flushed upon request completion/failure and capturing ColdStart metric
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
