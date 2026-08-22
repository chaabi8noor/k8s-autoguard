terraform {
  required_version = ">= 1.15.0"

  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = "0.11.0"
    }
  }
}

provider "kind" {}

variable "cluster_name" {
  type    = string
  default = "k8s-autoguard"
}

variable "node_image" {
  type    = string
  default = "kindest/node:v1.34.3@sha256:08497ee19eace7b4b5348db5c6a1591d7752b164530a36f855cb0f2bdcbadd48"
}

resource "kind_cluster" "autoguard" {
  name           = var.cluster_name
  node_image     = var.node_image
  wait_for_ready = true

  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"

    networking {
      disable_default_cni = true
      ip_family           = "ipv4"
      pod_subnet          = "10.42.0.0/16"
      service_subnet      = "10.43.0.0/16"
    }

    node {
      role  = "control-plane"
      image = var.node_image

      extra_port_mappings {
        container_port = 30080
        host_port      = 8080
        listen_address = "127.0.0.1"
        protocol       = "TCP"
      }

      extra_port_mappings {
        container_port = 30443
        host_port      = 8443
        listen_address = "127.0.0.1"
        protocol       = "TCP"
      }
    }

    node {
      role  = "worker"
      image = var.node_image
    }
  }
}

output "kube_context" {
  value = "kind-${kind_cluster.autoguard.name}"
}
