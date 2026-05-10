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
  image_id        = data.openstack_images_image_v2.ubuntu.id
  flavor_name     = var.vm_flavor
  key_pair        = var.ssh_key_name
  security_groups = [openstack_networking_secgroup_v2.vllm.name]

  user_data = templatefile("${path.module}/cloud-init.yaml", {
    api_key           = var.api_key
    huggingface_token = var.huggingface_token
  })

  network {
    name = "external"
  }
}

resource "openstack_networking_floatingip_v2" "vllm" {
  pool = "external"
}

resource "openstack_networking_floatingip_associate_v2" "vllm" {
  floating_ip = openstack_networking_floatingip_v2.vllm.address
  port_id     = openstack_compute_instance_v2.vllm.network[0].port
}

output "vm_ip" {
  value = openstack_networking_floatingip_v2.vllm.address
}

output "vllm_endpoint" {
  value = "https://${openstack_networking_floatingip_v2.vllm.address}/v1"
}
