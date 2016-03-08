output "asg.id" { 
	value = "${aws_autoscaling_group.docker-ecs.id}" 
}
output "asg.availability_zones" { 
	value = "${join(",", aws_autoscaling_group.docker-ecs.availability_zones)}" 
}
output "asg.min_size" { 
	value = "${aws_autoscaling_group.docker-ecs.min_size}" 
}
output "asg.max_size" { 
	value = "${aws_autoscaling_group.docker-ecs.max_size}" 
}
output "asg.default_cooldown" { 
	value = "${aws_autoscaling_group.docker-ecs.default_cooldown}" 
}
output "asg.name" { 
	value = "${aws_autoscaling_group.docker-ecs.name}" 
}
output "asg.health_check_grace_period" { 
	value = "${aws_autoscaling_group.docker-ecs.health_check_grace_period}" 
}
output "asg.health_check_type" { 
	value = "${aws_autoscaling_group.docker-ecs.health_check_type}" 
}
output "asg.desired_capacity" { 
	value = "${aws_autoscaling_group.docker-ecs.desired_capacity}" 
}
output "asg.launch_configuration" { 
	value = "${aws_autoscaling_group.docker-ecs.launch_configuration}" 
}
output "asg.load_balancers" { 
	value = "${join(",", aws_autoscaling_group.docker-ecs.load_balancers)}" 
}
output "launch_configuration.id" { 
	value = "${aws_launch_configuration.lc-docker-ecs.id}" 
}