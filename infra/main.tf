terraform {
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 3.0"
    }
  }
}

provider "openstack" {
  auth_url                      = var.openstack_auth_url
  region                        = var.openstack_region
  application_credential_id     = var.application_credential_id
  application_credential_secret = var.application_credential_secret
}

resource "openstack_networking_secgroup_v2" "vllm" {
  name        = "vllm-demo"
  description = "Security group for vLLM demo"
}

resource "openstack_networking_secgroup_rule_v2" "ssh" {
  security_group_id = openstack_networking_secgroup_v2.vllm.id
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = var.cidr_whitelist
}

resource "openstack_networking_secgroup_rule_v2" "https" {
  security_group_id = openstack_networking_secgroup_v2.vllm.id
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 443
  port_range_max    = 443
  remote_ip_prefix  = var.cidr_whitelist
}

data "openstack_images_image_v2" "ubuntu" {
  name        = var.vm_image
  most_recent = true
}

resource "openstack_compute_instance_v2" "vllm" {
  name            = "vllm-xlam2-demo"
  flavor_name     = var.vm_flavor
  key_pair        = var.ssh_key_name
  security_groups = [openstack_networking_secgroup_v2.vllm.name]

  block_device {
    uuid                  = data.openstack_images_image_v2.ubuntu.id
    source_type           = "image"
    destination_type      = "volume"
    volume_size           = var.root_volume_size
    boot_index            = 0
    delete_on_termination = true
  }

  user_data = templatefile("${path.module}/cloud-init.yaml", {
    api_key           = var.api_key
    huggingface_token = var.huggingface_token
  })

  network {
    name = "external"
  }
}

output "vm_ip" {
  value = openstack_compute_instance_v2.vllm.access_ip_v4
}

output "vllm_endpoint" {
  value = "http://${openstack_compute_instance_v2.vllm.access_ip_v4}:443/v1"
}
