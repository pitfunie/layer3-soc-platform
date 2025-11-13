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

