variable "openstack_auth_url" {
  description = "Leaf Cloud OpenStack auth URL"
  default     = "https://create.leaf.cloud:5000/v3"
}

variable "openstack_region" {
  description = "Leaf Cloud region"
  default     = "RegionOne"
}

variable "openstack_project_name" {
  description = "Your Leaf Cloud project name"
  type        = string
}

variable "openstack_user_name" {
  description = "Your Leaf Cloud username"
  type        = string
}

variable "openstack_password" {
  description = "Your Leaf Cloud password"
  type        = string
  sensitive   = true
}

variable "openstack_user_domain" {
  default = "Default"
}

variable "openstack_project_domain" {
  default = "Default"
}

variable "vm_flavor" {
  description = "GPU VM flavor"
  default     = "eg1.a100x1.V12-84"
}

variable "vm_image" {
  description = "Ubuntu image name"
  default     = "Ubuntu 22.04 LTS"
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

variable "cidr_whitelist" {
  description = "CIDR block allowed to access the VM"
  type        = string
  default     = "0.0.0.0/0"
}
