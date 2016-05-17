# Global Network Configuration

provider "aws" {
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region     = "${var.region}"
}

# Find all the AZs!

# module "az" {

# 	# Source the module:

# 	source = "github.com/terraform-community-modules/tf_aws_availability_zones"

# 	# Set module parameters here:

# 	region = "${var.region}"

# 	account = "${var.aws_credentials}"

# }

module "vpc" {
  # Source the module:
  source = "../modules/network/vpc"

  # Set module parameters here:
  name = "${var.environment_name}-vpc"
  cidr = "${var.vpc_cidr}"
}

# Create public subnet
module "public_subnet" {
  # Source the module:
  source = "../modules/network/public_subnet"

  # Set module parameters here:
  name      = "${var.environment_name}-public"
  vpc_id    = "${module.vpc.vpc_id}"
  cidr_seed = "${var.vpc_cidr}"

  #azs 		= "${module.az.list_all}"
  azs = "${var.azs}"
}

# Create bastion host
module "bastion" {
  # Source the module:
  source = "../modules/network/bastion"

  # Set module parameters here:
  name              = "${var.environment_name}-bastion"
  vpc_id            = "${module.vpc.vpc_id}"
  vpc_cidr          = "${module.vpc.vpc_cidr}"
  region            = "${var.region}"
  public_subnet_ids = "${module.public_subnet.subnet_ids}"
  key_name          = "${var.key_name}"
  instance_type     = "${var.bastion_instance_type}"
  ami               = "${module.bastion_ami.ami_id}"
}

# Create NAT gateways
module "nat" {
  # Source the module:
  source = "../modules/network/nat"

  # Set module parameters here:
  name = "${var.environment_name}-nat"

  #azs 		= "${module.az.list_all}"
  azs               = "${var.azs}"
  public_subnet_ids = "${module.public_subnet.subnet_ids}"
}

# Create private subnets and associate with NAT gateways
module "private_subnet" {
  # Source the module:
  source = "../modules/network/private_subnet"

  # Set module parameters here:
  name        = "${var.environment_name}-private"
  vpc_id      = "${module.vpc.vpc_id}"
  cidr_blocks = "${replace(join(",", split(",", module.public_subnet.cidr_blocks)), "/10\\.0\\./", "10.0.1")}"

  #azs 		= "${module.az.list_all}"
  azs = "${var.azs}"

  nat_gateway_ids = "${module.nat.nat_gateway_ids}"
}

# Ephemeral subnets for nodes which refresh quickly
module "ephemeral_subnet" {
  # Source the module:
  source = "../modules/network/private_subnet"

  # Set module parameters here:
  name        = "${var.environment_name}-ephemeral"
  vpc_id      = "${module.vpc.vpc_id}"
  cidr_blocks = "${replace(join(",", split(",", module.public_subnet.cidr_blocks)), "/10\\.0\\./", "10.0.2")}"

  #azs 		= "${module.az.list_all}"
  azs = "${var.azs}"

  nat_gateway_ids = "${module.nat.nat_gateway_ids}"
}

resource "aws_network_acl" "default" {
  vpc_id     = "${module.vpc.vpc_id}"
  subnet_ids = ["${concat(split(",", module.public_subnet.subnet_ids), split(",", module.private_subnet.subnet_ids), split(",", module.ephemeral_subnet.subnet_ids))}"]

  ingress {
    protocol   = "-1"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
    rule_no    = 100
    action     = "allow"
  }

  egress {
    protocol   = "-1"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
    rule_no    = 100
    action     = "allow"
  }

  tags {
    Name = "${var.environment_name}-all"
    role = "global"
  }
}

## Supporting Matter:
# Get the latest "trusty" ubuntu ami
module "bastion_ami" {
  # Source the module:
  source = "github.com/terraform-community-modules/tf_aws_ubuntu_ami/ebs"

  # Set module parameters here:
  instance_type = "${var.bastion_instance_type}"
  region        = "${var.region}"
  distribution  = "trusty"
}
