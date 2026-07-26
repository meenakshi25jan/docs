terraform {
  required_version = ">= 1.5"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90"
    }
  }

  backend "azurerm" {
    resource_group_name  = "tfstate-rg"
    storage_account_name = "tfstateaiteacher"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "location" {
  type    = string
  default = "eastus"
}

variable "project" {
  type    = string
  default = "ai-english-teacher"
}

locals {
  tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "${var.project}-${var.environment}-rg"
  location = var.location
  tags     = local.tags
}

# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "${var.project}-vnet"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = ["10.0.0.0/16"]
  tags                = local.tags
}

resource "azurerm_subnet" "aks" {
  name                 = "aks-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_subnet" "postgres" {
  name                 = "postgres-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
  service_endpoints    = ["Microsoft.Storage"]
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "main" {
  name                = "${var.project}-aks"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = var.project
  tags                = local.tags

  default_node_pool {
    name           = "system"
    vm_size        = "Standard_D2s_v5"
    vnet_subnet_id = azurerm_subnet.aks.id
    min_count      = 2
    max_count      = 3
    node_count     = 2
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin = "azure"
    service_cidr   = "10.1.0.0/16"
    dns_service_ip = "10.1.0.10"
  }

  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  }
}

# App Node Pool
resource "azurerm_kubernetes_cluster_node_pool" "app" {
  name                  = "app"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = "Standard_D4s_v5"
  vnet_subnet_id        = azurerm_subnet.aks.id
  min_count             = 3
  max_count             = 20
  node_count            = 3
  tags                  = local.tags
}

# AI Worker Node Pool (Spot)
resource "azurerm_kubernetes_cluster_node_pool" "ai_workers" {
  name                  = "aiworkers"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = "Standard_D4s_v5"
  vnet_subnet_id        = azurerm_subnet.aks.id
  min_count             = 0
  max_count             = 15
  node_count            = 1
  priority              = "Spot"
  eviction_policy       = "Delete"
  spot_max_price        = -1
  node_taints           = ["workload=ai:NoSchedule"]
  tags                  = local.tags
}

# PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "main" {
  name                          = "${var.project}-pg"
  location                      = azurerm_resource_group.main.location
  resource_group_name           = azurerm_resource_group.main.name
  version                       = "16"
  sku_name                      = "GP_Standard_D4s_v3"
  storage_mb                    = 262144
  backup_retention_days         = 35
  geo_redundant_backup_enabled  = true
  administrator_login           = "pgadmin"
  administrator_password        = var.postgres_password
  zone                          = "1"
  tags                          = local.tags
}

resource "azurerm_postgresql_flexible_server_configuration" "pgvector" {
  name      = "azure.extensions"
  server_id = azurerm_postgresql_flexible_server.main.id
  value     = "VECTOR"
}

# Redis Cache
resource "azurerm_redis_cache" "main" {
  name                = "${var.project}-redis"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = 1
  family              = "P"
  sku_name            = "Premium"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"
  tags                = local.tags
}

# Container Registry
resource "azurerm_container_registry" "main" {
  name                = replace("${var.project}acr", "-", "")
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Premium"
  admin_enabled       = false
  tags                = local.tags
}

# Key Vault
resource "azurerm_key_vault" "main" {
  name                       = "${var.project}-kv"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 90
  purge_protection_enabled   = true
  tags                       = local.tags
}

# Log Analytics / Application Insights
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.project}-logs"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 90
  tags                = local.tags
}

resource "azurerm_application_insights" "main" {
  name                = "${var.project}-insights"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  tags                = local.tags
}

# Storage Account
resource "azurerm_storage_account" "main" {
  name                     = replace("${var.project}storage", "-", "")
  location                 = azurerm_resource_group.main.location
  resource_group_name      = azurerm_resource_group.main.name
  account_tier             = "Standard"
  account_replication_type = "GRS"
  tags                     = local.tags
}

data "azurerm_client_config" "current" {}

variable "postgres_password" {
  type      = string
  sensitive = true
}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.main.name
}

output "postgres_fqdn" {
  value = azurerm_postgresql_flexible_server.main.fqdn
}

output "redis_hostname" {
  value = azurerm_redis_cache.main.hostname
}

output "acr_login_server" {
  value = azurerm_container_registry.main.login_server
}

output "app_insights_key" {
  value     = azurerm_application_insights.main.instrumentation_key
  sensitive = true
}
