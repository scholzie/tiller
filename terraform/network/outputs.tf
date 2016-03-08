output "vpc_id" { value = "${aws_vpc.ecs.id}" }
output "vpc_cidr" { value = "${aws_vpc.ecs.cidr_block}" }
output "subnet_ids" { value = "${join(",", aws_subnet.ecs.*.id)}" }