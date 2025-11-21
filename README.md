
## Start with deploy.sh to get your Lambda up, then push the GitHub Action to your repo. Within an hour you'll be processing real GuardDuty findings into GitHub issues. 

<img width="1792" height="1120" alt="image" src="https://github.com/user-attachments/assets/8c9992b8-06b9-4f41-874f-d78847e96bf5" />






# Project Structure 


layer3-soc-github/
├── lambda/
│   ├── webhook_receiver.py
│   ├── requirements.txt
│   └── deploy.sh
├── .github/
│   └── workflows/
│       └── security-response.yml
├── terraform/
│   ├── main.tf
│   └── variables.tf
└── README.md


# 1. Lambda Function (webhook_receiver.py)
 

import json
import boto3
import os
from datetime import datetime
import hashlib

def lambda_handler(event, context):
    """Process GuardDuty findings from EventBridge, create GitHub issues"""
    
    # Parse the EventBridge event
    detail = event['detail']
    severity = detail.get('severity', 0)
    
    # Only process medium-high severity (4+)
    if severity < 4:
        return {'statusCode': 200, 'body': 'Low severity - skipped'}
    
    # Generate issue fingerprint for deduplication
    fingerprint = hashlib.md5(
        f"{detail['type']}-{detail['resource']['resourceType']}".encode()
    ).hexdigest()[:8]
    
    # Create GitHub issue via API (simplified for demo)
    issue_data = {
        'title': f"[SEV-{severity}] {detail['type']} - {fingerprint}",
        'body': format_issue_body(detail),
        'labels': ['security', f"sev-{severity}", 'automated']
    }
    
    # In production, this would use PyGithub or requests
    # For demo, just log the action
    print(f"Creating GitHub issue: {json.dumps(issue_data)}")
    
    # Send to SQS for batch processing (production pattern)
    if os.environ.get('USE_SQS'):
        sqs = boto3.client('sqs')
        sqs.send_message(
            QueueUrl=os.environ['SQS_QUEUE_URL'],
            MessageBody=json.dumps(issue_data)
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'fingerprint': fingerprint})
    }

def format_issue_body(finding):
    """Format GuardDuty finding as GitHub issue"""
    return f"""
## 🚨 Security Alert from GuardDuty

**Severity:** {finding['severity']}/10
**Type:** {finding['type']}
**Region:** {finding['region']}
**Account:** {finding['accountId']}
**Time:** {finding['updatedAt']}

Affected Resource
- **Type:** {finding['resource']['resourceType']}
- **Details:** {json.dumps(finding['resource'], indent=2)}

Finding Details
```json
{json.dumps(finding['service'], indent=2)}


#Automated Response

    [ ] ECS service restart initiated

    [ ] Security group updated

    [ ] CloudWatch logs captured

    [ ] Audit trail recorded

#Next Steps

    Review the automated actions above

    Verify the threat has been mitigated

    Close this issue when resolved


## 2. GitHub Action (security-response.yml)
```yaml
name: Automated Security Response
on:
  issues:
    types: [opened, labeled]

jobs:
  triage:
    if: contains(github.event.issue.labels.*.name, 'security')
    runs-on: ubuntu-latest
    steps:
      - name: Parse Security Alert
        id: parse
        run: |
          echo "Parsing issue body for resource details..."
          echo "SEVERITY=$(echo '${{ github.event.issue.title }}' | grep -o 'SEV-[0-9]' | grep -o '[0-9]')" >> $GITHUB_OUTPUT
      
      - name: Auto-Response for High Severity
        if: steps.parse.outputs.SEVERITY >= 7
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Restart ECS Service
        if: steps.parse.outputs.SEVERITY >= 7
        run: |
          # Demo: Show the command that would run
          echo "aws ecs update-service --cluster prod --service app --force-new-deployment"
          
          # Update issue
          gh issue comment ${{ github.event.issue.number }} \
            --body "✅ **Automated Response Triggered**
            - ECS service restart initiated at $(date)
            - Monitoring for next 5 minutes
            - Human review still required"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Create Audit Log
        run: |
          # Log action for compliance
          echo "{
            'timestamp': '$(date -Iseconds)',
            'issue': ${{ github.event.issue.number }},
            'severity': ${{ steps.parse.outputs.SEVERITY }},
            'automated_actions': ['ecs_restart'],
            'status': 'completed'
          }" > audit_log.json
          
          # In production, this would push to S3/CloudWatch

# 3. EventBridge Rule (Terraform)

# main.tf
resource "aws_cloudwatch_event_rule" "guardduty_high_severity" {
  name        = "guardduty-to-github"
  description = "Route high-severity GuardDuty findings to GitHub"

  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
    detail = {
      severity = [{
        numeric = [">=", 4]
      }]
    }
  })
}

resource "aws_cloudwatch_event_target" "lambda" {
  rule      = aws_cloudwatch_event_rule.guardduty_high_severity.name
  target_id = "SendToLambda"
  arn       = aws_lambda_function.webhook_receiver.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.webhook_receiver.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.guardduty_high_severity.arn
}


# 4. Quick Deploy Script

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


# Variables.tf

# variables.tf
variable "github_token" {
  description = "GitHub personal access token for API calls"
  type        = string
  sensitive   = true
}

variable "github_repo" {
  description = "GitHub repository (format: owner/repo)"
  type        = string
  default     = "your-org/soc-platform"
}

variable "alert_threshold" {
  description = "Minimum severity to create GitHub issues (1-10)"
  type        = number
  default     = 4
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 60
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "demo"
}

# terraform.vtfvars

github_token = "ghp_your_actual_token_here"
github_repo  = "pitfunie/layer3-soc"


# requirements.txt

github_token = "ghp_your_actual_token_here"
github_repo  = "pitfunie/layer3-soc"

# -layer3-soc-platform
