# VPC
output "vpc_id"   { value = "${module.vpc.vpc_id}" }
output "vpc_cidr" { value = "${module.vpc.vpc_cidr}" }

# Subnets
output "public_subnet_ids"    { value = "${module.public_subnet.subnet_ids}" }
output "private_subnet_ids"   { value = "${module.private_subnet.subnet_ids}" }
#output "ephemeral_subnet_ids" { value = "${module.ephemeral_subnets.subnet_ids}" }

# NAT
output "nat_gateway_ids" { value = "${module.nat.nat_gateway_ids}" }
