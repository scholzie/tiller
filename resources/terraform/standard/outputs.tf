output "asg.id" {
  value = "${aws_autoscaling_group.ecs-cluster.id}"
}

output "asg.availability_zones" {
  value = "${join(",", aws_autoscaling_group.ecs-cluster.availability_zones)}"
}

output "asg.min_size" {
  value = "${aws_autoscaling_group.ecs-cluster.min_size}"
}

output "asg.max_size" {
  value = "${aws_autoscaling_group.ecs-cluster.max_size}"
}

output "asg.default_cooldown" {
  value = "${aws_autoscaling_group.ecs-cluster.default_cooldown}"
}

output "asg.name" {
  value = "${aws_autoscaling_group.ecs-cluster.name}"
}

output "asg.health_check_grace_period" {
  value = "${aws_autoscaling_group.ecs-cluster.health_check_grace_period}"
}

output "asg.health_check_type" {
  value = "${aws_autoscaling_group.ecs-cluster.health_check_type}"
}

output "asg.desired_capacity" {
  value = "${aws_autoscaling_group.ecs-cluster.desired_capacity}"
}

output "asg.launch_configuration" {
  value = "${aws_autoscaling_group.ecs-cluster.launch_configuration}"
}

output "asg.load_balancers" {
  value = "${join(",", aws_autoscaling_group.ecs-cluster.load_balancers)}"
}

output "launch_configuration.id" {
  value = "${aws_launch_configuration.ecs.id}"
}

output "vpc_id" {
  value = "${aws_vpc.ecs.id}"
}

output "vpc_cidr" {
  value = "${aws_vpc.ecs.cidr_block}"
}

output "subnet_ids" {
  value = "${join(",", aws_subnet.ecs.*.id)}"
}
