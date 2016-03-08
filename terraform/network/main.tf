# Global Network Configuration

provider "aws" {
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region = "${var.region}"
}

# Create a VPC
resource "aws_vpc" "ecs" {
	
	cidr_block 				= "${var.vpc_cidr}"
	enable_dns_support 		= true
	enable_dns_hostnames	= true

	tags		{ Name = "${var.cluster_name} ECS VPC" }
	lifecycle 	{ create_before_destroy = true }
}

# Create an IGW for the VPC
resource "aws_internet_gateway" "ecs" {
	vpc_id = "${aws_vpc.ecs.id}"

	lifecycle { create_before_destroy = true }
}

# Let the VPC access the internet via the gateway
resource "aws_route" "ecs-internet" {
	route_table_id = "${aws_vpc.ecs.main_route_table_id}"
	destination_cidr_block = "0.0.0.0/0"
	gateway_id = "${aws_internet_gateway.ecs.id}"

	lifecycle { create_before_destroy = true }
}

# Create one subnet per availability zone
# TODO: Add public/private/ephemeral subnets - modularize
resource "aws_subnet" "ecs" {
	vpc_id = "${aws_vpc.ecs.id}"

	# Onr-per-AZ magic
	count 				= "${length(split(",", var.azs))}" # one per AZ
	cidr_block 			= "${cidrsubnet(var.vpc_cidr, 8, count.index)}"
	availability_zone 	= "${element(split(",", var.azs), count.index)}"

	map_public_ip_on_launch = false

	lifecycle { create_before_destroy = true }
}

