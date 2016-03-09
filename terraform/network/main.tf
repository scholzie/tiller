# Global Network Configuration

provider "aws" {
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region 	 = "${var.region}"
}

module "vpc" {
	# Source the module:
	source = "../modules/vpc"

	# Set module parameters here:
	name = "${var.environment_name}-vpc"
	cidr = "${var.vpc_cidr}"
}


# TODO: Add ephemeral subnets for ECS insatnces

# Create public subnet
module "public_subnet" {
	# Source the module:
	source = "../modules/public_subnet"

	# Set module parameters here:
	name 		= "${var.environment_name}-public"
	vpc_id 		= "${module.vpc.vpc_id}"
	cidr_seed 	= "${var.vpc_cidr}"
	azs 		= "${var.azs}"
}

# Create NAT gateways
module "nat" {
	# Source the module:
	source = "../modules/nat"

	# Set module parameters here:
	name 			  = "${var.environment_name}-nat"
	azs 			  = "${var.azs}"
	public_subnet_ids = "${module.public_subnet.subnet_ids}"
}

# Create private subnets and associate with NAT gateways
module "private_subnet" {
	# Source the module:
	source = "../modules/private_subnet"

	# Set module parameters here:
	name 		= "${var.environment_name}-private"
	vpc_id 		= "${module.vpc.vpc_id}"
	cidr_seed 	= "${var.vpc_cidr}"
	azs 		= "${var.azs}"

	nat_gateway_ids = "${module.nat.nat_gateway_ids}"
}