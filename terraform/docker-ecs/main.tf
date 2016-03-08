# Docker Cluster Configuration

provider "aws" {
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region = "${var.region}"
}

# Cluster
resource "aws_ecs_cluster" "docker" {
	name = "${var.cluster_name}"
}

# ELB SG
resource "aws_security_group" "elb-docker-sg" {
	name = "elb-${var.environment_name}-docker-ecs-sg"
	description = "ELB security for docker cluster"
	# TODO: Investigate what we'll need for this
	ingress {
	    protocol   	= "tcp"
	    cidr_blocks = ["0.0.0.0/0"]
	    from_port  	= 80
	    to_port    	= 80
	}
	egress {
	    protocol   	= "-1"
	    cidr_blocks = ["0.0.0.0/0"]
	    from_port  	= 0
	    to_port    	= 0
	}
	lifecycle { create_before_destroy = true }
	tags {
		Environment = "${var.environment_name}"
		role = "docker-ecs"
	}
}

# EC2 SG
resource "aws_security_group" "ec2-docker-sg" {
	name = "ec2-{var.environment_name}-docker-ecs-sg"
	description = "EC2 security for docker cluster"
	# SSH Inbound
	ingress {
	    protocol   	= "tcp"
	    cidr_blocks = ["0.0.0.0/0"]
	    from_port  	= 22
	    to_port    	= 22
	}
	# HTTP Inbound
	ingress {
	    protocol   	= "tcp"
	    cidr_blocks = ["0.0.0.0/0"]
	    from_port  	= 80
	    to_port    	= 80
	}
	# HTTPS Inbound
	ingress {
	    protocol   	= "tcp"
	    cidr_blocks = ["0.0.0.0/0"]
	    from_port  	= 443
	    to_port    	= 443
	}
	# outbound access
	egress {
	    protocol   	= "-1"
	    cidr_blocks = ["0.0.0.0/0"]
	    from_port  	= 0
	    to_port    	= 0
	}

	lifecycle { create_before_destroy = true }
	
	tags {
		Environment = "${var.environment_name}"
		role 		= "docker-ecs"
	}
}

# ELB
resource "aws_elb" "elb-docker-ecs" {
	name = "elb-${var.environment_name}-docker-ecs"
	# Subnets will have been made during global config.
	# TODO: use a module to go get subnets
	subnets = ["${split(",", var.subnets)}"]
	listener {
		instance_port 		= 80
		instance_protocol 	= "tcp"
		lb_port 			= 80
		lb_protocol 		= "tcp"	
	}
	security_groups = [
		"${aws_security_group.elb-docker-sg.id}"
	]
	tags { 
		Environment = "${var.environment_name}"
		role = "docker-ecs"
	}
}

# Launch Config
resource "aws_launch_configuration" "lc-docker-ecs" {
	name = "lc-${var.environment_name}-docker-ecs"
	image_id = "${var.ami}"
	instance_type = "${var.instance_type}"
	iam_instance_profile = "${var.iam_instance_profile}"
	key_name = "${var.key_name}"
	security_groups = ["${aws_security_group.ec2-docker-sg}"]
	user_data = <<EOL
#! /bin/bash
echo ECS_CLUSTER=${var.cluster_name} >> /etc/ecs/ecs.config
echo ECS_ENGINE_AUTH_TYPE=dockercfg >> /etc/ecs/ecs.config
# echo ECS_ENGINE_AUTH_DATA='{\"${var.registry_url}\":{\"auth\":\"${var.registry_auth}\",\"email\":\"${var.registry_email}\"}}' >> /etc/ecs/ecs.config
EOL
	enable_monitoring = true
	lifecycle { create_before_destroy = true }
}

# ASG
resource "aws_autoscaling_group" "docker-ecs" {
	name = "asg-${var.environment_name}-docker-ecs"
	availability_zones = ["${split(",", var.azs)}"]
	vpc_zone_identifier = ["${split(",", var.subnets)}"]
	depends_on = ["aws_launch_configuration.lc-docker"]
	launch_configuration = "${aws_launch_configuration.lc-docker.id}"
	min_size = "${var.min_size}"
	max_size = "${var.max_size}"
	desired_capacity = "${var.desired_capacity}"
	health_check_type = "EC2"
	health_check_grace_period = "${var.health_check_grace_period}"
	load_balancers = ["elb-${var.environment_name}-docker-ecs"]
	tag {
		key = "Environment"
		value = "${var.environment_name}"
		propagate_at_launch = true
	}
	tag {
		key = "Name"
		value = "ECS ${var.cluster_name}"
		propagate_at_launch = true
	}
}
