# VPC
output "vpc_id"   { value = "${module.vpc.vpc_id}" }
output "vpc_cidr" { value = "${module.vpc.vpc_cidr}" }

# Subnets
output "public_subnet_ids"    	{ value = "${module.public_subnet.subnet_ids}" }
output "public_subnet_cidrs" 	{ value = "${module.public_subnet.cidr_blocks}" }
output "private_subnet_ids"   	{ value = "${module.private_subnet.subnet_ids}" }
output "private_subnet_cidrs" 	{ value = "${module.private_subnet.cidr_blocks}" }
output "ephemeral_subnet_ids" 	{ value = "${module.ephemeral_subnet.subnet_ids}" }
output "ephemeral_subnet_cidrs"	{ value = "${module.ephemeral_subnet.cidr_blocks}" }

# NAT
output "nat_gateway_ids" 	 { value = "${module.nat.nat_gateway_ids}" }
output "nat_eip_public_ips"  { value = "${module.nat.nat_eip_public_ips}" }
output "nat_eip_private_ips" { value = "${module.nat.nat_eip_private_ips}" }

# AZs
# output "azs" { value = "${module.az.list_all}" }
output "azs" { value = "${var.azs}" }

# Bastion
output "bastion_user" { value = "${module.bastion.user}" }
output "bastion_private_ip" { value = "${module.bastion.private_ip}" }
output "bastion_public_ip" { value = "${module.bastion.public_ip}" }
output "bastion_public_dns" { value = "${module.bastion.public_dns}" }
output "bastion_key_name" { value = "${module.bastion.key_name}" }