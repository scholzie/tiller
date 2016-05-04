variable "access_key" {
}

variable "secret_key" {
}

variable "cluster_name" {
  description = "The name of the ECS Cluster"
}

variable "ami" {
  description = "AMI id to launch, must be in the region specified by the region variable"
}

variable "inbound_ssh_cidrs" {
  default     = "10.0.0.0/24"
  description = "Where SSH ingress will be allowed from"
}

variable "key_name" {
  description = "SSH key name in your AWS account for AWS instances."
}

variable "region" {
  default     = "us-east-1"
  description = "The region of AWS"
}

variable "azs" {
  description = "Comma separated list of EC2 availability zones to launch instances, must be within region"
}

# variable "security_group_ids" {

#     description = "Comma separated list of security group ids"

#     default = ""

# }

variable "instance_type" {
  default     = "m3.medium"
  description = "Name of the AWS instance type"
}

variable "min_size" {
  default     = "1"
  description = "Minimum number of instances to run in the group"
}

variable "max_size" {
  default     = "5"
  description = "Maximum number of instances to run in the group"
}

variable "desired_capacity" {
  default     = "1"
  description = "Desired number of instances to run in the group"
}

variable "health_check_grace_period" {
  default     = "300"
  description = "Time after instance comes into service before checking health"
}

variable "iam_instance_profile" {
  description = "The IAM Instance Profile (e.g. right side of Name=AmazonECSContainerInstanceRole)"
}

variable "registry_url" {
  default     = "https://index.docker.io/v1/"
  description = "Docker private registry URL, defaults to Docker index"
}

variable "registry_email" {
  default     = ""
  description = "Docker private registry login email address"
}

variable "registry_auth" {
  default     = ""
  description = "Docker private registry login auth token (from ~/.dockercgf)"
}

variable "ecs_host_chef_role" {
  default     = "ec2_docker_host"
  description = "Chef role to add to first-boot runlist when an ECS host is spawned."
}

variable "environment_name" {
  description = "Environment name (dev, etc.)"
}

variable "subnets" {
  description = "Subnets to launch the cluster into."
}

variable "vpc_id" {
  desc = "VPC to launch cluster into"
}
