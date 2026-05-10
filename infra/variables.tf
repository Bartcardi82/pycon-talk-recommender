variable "openstack_auth_url" {
  description = "Leaf Cloud OpenStack auth URL"
  default     = "https://create.leaf.cloud:5000"
}

variable "openstack_region" {
  description = "Leaf Cloud region"
  default     = "europe-nl"
}

variable "application_credential_id" {
  description = "Leaf Cloud application credential ID"
  type        = string
}

variable "application_credential_secret" {
  description = "Leaf Cloud application credential secret"
  type        = string
  sensitive   = true
}

variable "vm_flavor" {
  description = "GPU VM flavor"
  default     = "eg1.a100x1.V12-84"
}

variable "vm_image" {
  description = "Ubuntu image name"
  default     = "Ubuntu-22.04"
}

variable "ssh_key_name" {
  description = "Name of your SSH keypair in Leaf Cloud"
  type        = string
}

variable "api_key" {
  description = "API key for vLLM access via Caddy"
  type        = string
  sensitive   = true
}

variable "huggingface_token" {
  description = "HuggingFace token (if model is gated)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "root_volume_size" {
  description = "Root volume size in GB (needs ~200 for vLLM + 32B model)"
  type        = number
  default     = 200
}

variable "cidr_whitelist" {
  description = "CIDR block allowed to access the VM"
  type        = string
  default     = "0.0.0.0/0"
}
