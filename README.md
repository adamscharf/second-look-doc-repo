# Second Look: A Simple Document Repository

Document repository application built using SAM CLI

## Description

API Gateway -> AWS Lambda -> DynamoDB -> Client -> S3

When an HTTP POST request is made to the Amazon API Gateway endpoint, the AWS Lambda function is invoked which generates a pre-signed S3 POST URL and inserts a placeholder item into the Amazon DynamoDB table. It then returns the pre-signed URL for the client to use to upload a file to S3.

Inspiration and code snippets were taken from several Serverless Land Patterns. Learn more about the used patterns and more here:

- [apigw-lambda-dynamodb](https://serverlessland.com/patterns/apigw-lambda-dynamodb)
- [s3-eventbridge-sfn](https://serverlessland.com/patterns/s3-eventbridge-sfn)

> **Important**: This application uses various AWS services and there are costs associated with these services after the Free Tier usage - please see the [AWS Pricing page](https://aws.amazon.com/pricing/) for details. You are responsible for any AWS costs incurred. No warranty is implied in this example.

## Requirements

* [Create an AWS account](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html) if you do not already have one and log in. The IAM user that you use must have sufficient permissions to make necessary AWS service calls and manage AWS resources.
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed and configured
* [Git Installed](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* [AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) (AWS SAM) installed

## Deployment Instructions

1. Create a new directory, navigate to that directory in a terminal and clone the GitHub repository:
    ```bash
    git clone https://github.com/adamscharf/second-look-doc-repo
    ```
1. Change directory to the pattern directory:
    ```bash
    cd second-look-doc-repo/
    ```
1. From the command line, use AWS SAM to deploy the AWS resources for the pattern as specified in the template.yml file:
    ```bash
    sam deploy --guided
    ```
1. During the prompts:
    * Enter a stack name
    * Enter the desired AWS Region
    * Allow SAM CLI to create IAM roles with the required permissions.

    Once you have run `sam deploy --guided` mode once and saved arguments to a configuration file (samconfig.toml), you can use `sam deploy` in future to use these defaults.

1. Note the outputs from the SAM deployment process. These contain the resource names and/or ARNs which are used for testing.

## How it works

### Working

- An HTTP POST request is sent to the Amazon API Gateway endpoint
- The AWS Lambda function is invoked and does two things:
    1. Creates a presigned URL for an S3 POST which is returned to the client
    1. Inserts a placeholder item into the Amazon DynamoDB table with a contentUrl link to the future upload location
- The client is then able to use the pre-signed URL to upload their file to the S3 bucket

### ToDo

- The Amazon S3 bucket is configured to send any events regarding its content, such as an `Object created` event that is emitted when an object is uploaded to the bucket, to Amazon EventBridge.
- An Amazon EventBridge rule that triggers a Step Functions workflow if a new `Object created` event is emitted by the S3 bucket. The workflow receives an [EventBridge event message](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ev-events.html) as its input which contains information such as the name of the S3 bucket and the key of the uploaded image.
- A sample AWS Step Functions workflow is called which invokes a Lambda Function which simulates calling a Malware Detection API, updates the DynamoDB, moves the file to a permenant folder and updates the DynamoDB again.

## Cleanup

Delete the stack:

```bash
sam delete
```
