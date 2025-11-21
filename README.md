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









📖 Must Read

    SOC History and Facts

    Awesome SOC

    SOCLess: Netflix SOC Model

    MITRE: 11 Strategies for a World-Class SOC

    CMM SOCTOM

    LetsDefend SOC Analyst Interview Questions

    FIRST: Building a SOC

    NCSC: Building a SOC

    Gartner: Market Guide for NDR



Automated Response Workflow

    [ ] ECS service restart initiated
    [ ] Security group updated
    [ ] CloudWatch logs captured
    [ ] Audit trail recorded


Next Steps:

    Review automated actions above

    Verify threat mitigation

    Close issue when resolved

GitHub Action (security-response.yml)

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
              echo "Parsing issue body..."
              echo "SEVERITY=$(echo '${{ github.event.issue.title }}' | grep -o 'SEV-[0-9]' | grep -o '[0-9]')" >> $GITHUB_OUTPUT
      
      - name: Auto-Response for High Severity
        if: steps.parse.outputs.SEVERITY >= 7
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1


 EventBridge Rule (Terraform)

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

🚀 Quick Deploy Script

      #!/bin/bash
    # deploy.sh
    
    cd lambda
    pip install -r requirements.txt -t .
    zip -r function.zip .
    
    aws lambda create-function \
      --function-name github-webhook-receiver \
      --runtime python3.9 \
      --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-role \
      --handler webhook_receiver.lambda_handler \
      --zip-file fileb://function.zip \
      --environment Variables={GITHUB_TOKEN=your-token,GITHUB_REPO=pitfunie/layer3-soc}


📦 Variables
    
    variable "github_token" {
      description = "GitHub personal access token"
      type        = string
      sensitive   = true
    }
    
    variable "github_repo" {
      description = "GitHub repository (owner/repo)"
      type        = string
      default     = "pitfunie/layer3-soc"
    }
    
    variable "alert_threshold" {
      description = "Minimum severity to create GitHub issues (1-10)"
      type        = number
      default     = 4
    }

Requirements

    github_token = "ghp_your_actual_token_here"
    github_repo  = "pitfunie/layer3-soc"


🎯 Purpose

This README anchors the Layer 3 SOC automation demo with:

    Explicit integration examples (GitHub Actions, AWS EventBridge, Terraform)

    Hands-on workflows for automated detection and response

    Clear operational steps for analysts and engineers

    

  Michael WyCliff Williams GNC  
