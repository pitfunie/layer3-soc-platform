#!/bin/bash
# deploy.sh

# Package Lambda
cd lambda
pip install -r requirements.txt -t .
zip -r function.zip .

# Deploy to AWS
aws lambda create-function \
  --function-name github-webhook-receiver \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-role \
  --handler webhook_receiver.lambda_handler \
  --zip-file fileb://function.zip \
  --environment Variables={GITHUB_TOKEN=your-token,GITHUB_REPO=your-org/your-repo}

# Create EventBridge rule
aws events put-rule \
  --name guardduty-to-github \
  --event-pattern file://event-pattern.json

echo "✅ Deployed! GuardDuty → GitHub integration ready"

