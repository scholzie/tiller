variable "access_key" {
}

variable "secret_key" {
}

variable "aws_credentials" {
  default     = "default"
  description = "Credential set from ~/.aws/credentials"
}

variable "environment_name" {
  default     = ""
  description = "Environment name to tag EC2 resources with (tag=environment)"
}

variable "vpc_cidr" {
  default     = "10.0.0.0/16"
  description = "CIDR block for the VPC to use"
}

variable "inbound_ssh_cidrs" {
  default     = "10.0.0.0/16"
  description = "Where SSH ingress will be allowed from"
}

variable "region" {
  default     = "us-east-1"
  description = "The region of AWS"
}

variable "azs" {
  description = "Comma separated list of EC2 availability zones to launch instances, must be within region"
}

variable "bastion_instance_type" {
  default = "t2.micro"
}

variable "key_name" {
  description = "Key name to use on the bastion host"
}
