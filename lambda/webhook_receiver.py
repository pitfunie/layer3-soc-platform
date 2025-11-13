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

### Affected Resource
- **Type:** {finding['resource']['resourceType']}
- **Details:** {json.dumps(finding['resource'], indent=2)}

### Finding Details
```json
{json.dumps(finding['service'], indent=2)}

