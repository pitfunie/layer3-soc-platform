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


