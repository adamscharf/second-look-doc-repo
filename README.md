# Second Look: A Simple Document Repository

Document repository application built using SAM CLI

## Description

API Gateway -> AWS Lambda -> DynamoDB -> Client -> S3

When an HTTP POST request is made to the Amazon API Gateway endpoint, the AWS Lambda function is invoked which generates a pre-signed S3 POST URL and inserts a placeholder item into the Amazon DynamoDB table. It then returns the pre-signed URL for the client to use to upload a file to S3.

Inspiration and code snippets were taken from several Serverless Land Patterns. Learn more about the used patterns and more here:

- [apigw-lambda-dynamodb](https://serverlessland.com/patterns/apigw-lambda-dynamodb)

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

When an HTTP POST request is sent to the Amazon API Gateway endpoint, the AWS Lambda function is invoked and creates a presigned URL which is returned to the client. It also inserts a placeholder item into the Amazon DynamoDB table with a contentUrl link to the future upload location. The client is then able to use the pre-signed URL to upload their file to the S3 bucket.

## Cleanup

1. Delete the stack
    ```bash
    aws cloudformation delete-stack --stack-name STACK_NAME
    ```
1. Confirm the stack has been deleted
    ```bash
    aws cloudformation list-stacks --query "StackSummaries[?contains(StackName,'STACK_NAME')].StackStatus"
    ```
