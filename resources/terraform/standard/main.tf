# main.tf - brings up an ECS cluster

provider "aws" {
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region     = "${var.region}"
}

# Create a VPC
resource "aws_vpc" "ecs" {
  cidr_block           = "${var.vpc_cidr}"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags {
    Name = "${var.cluster_name} ECS VPC"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Create the ECS cluster
resource "aws_ecs_cluster" "default" {
  name = "${var.cluster_name}"
}

# Create an IGW for the VPC
resource "aws_internet_gateway" "ecs" {
  vpc_id = "${aws_vpc.ecs.id}"

  lifecycle {
    create_before_destroy = true
  }
}

# Let the VPC access the internet via the gateway
resource "aws_route" "ecs-internet" {
  route_table_id         = "${aws_vpc.ecs.main_route_table_id}"
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = "${aws_internet_gateway.ecs.id}"

  lifecycle {
    create_before_destroy = true
  }
}

# Create one subnet per availability zone
resource "aws_subnet" "ecs" {
  vpc_id = "${aws_vpc.ecs.id}"

  # Onr-per-AZ magic
  count             = "${length(split(",", var.azs))}"               # one per AZ
  cidr_block        = "${cidrsubnet(var.vpc_cidr, 8, count.index)}"
  availability_zone = "${element(split(",", var.azs), count.index)}"

  map_public_ip_on_launch = false

  lifecycle {
    create_before_destroy = true
  }
}

# ELB for the ASG
resource "aws_security_group" "ecs-elb" {
  name        = "${var.cluster_name} ELB"
  description = "SG for ${var.cluster_name} ELB"
  vpc_id      = "${aws_vpc.ecs.id}"

  # HTTP
  ingress {
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 80
    to_port     = 80
  }

  # HTTPS
  ingress {
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 443
    to_port     = 443
  }

  # Outbound internet
  egress {
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 0
    to_port     = 0
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Default security group for instance access
resource "aws_security_group" "ecs_instance_sg" {
  name        = "${var.cluster_name} EC2"
  description = "SG for ${var.cluster_name} EC2 instances"
  vpc_id      = "${aws_vpc.ecs.id}"

  # SSH inbound
  ingress {
    protocol    = "tcp"
    cidr_blocks = ["${split(",", var.inbound_ssh_cidrs)}"]
    from_port   = 22
    to_port     = 22
  }

  # HTTPS inbound
  ingress {
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 443
    to_port     = 443
  }

  # HTTP inbound
  ingress {
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 80
    to_port     = 80
  }

  # Internet Out
  egress {
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 0
    to_port     = 0
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Create an ELB for the ASG
resource "aws_elb" "ecs" {
  name            = "elb-${var.environment_name}-ecs"
  subnets         = ["${aws_subnet.ecs.*.id}"]
  security_groups = ["${aws_security_group.ecs-elb.id}"]

  listener {
    instance_port     = 80
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }

  security_groups = ["${aws_security_group.ecs-elb.id}"]

  tags {
    Environment = "${var.environment_name}"
    role        = "standard"
    project     = "devops"
  }
}

resource "aws_autoscaling_group" "ecs-cluster" {
  name = "${var.cluster_name}"

  availability_zones        = ["${split(",", var.azs)}"]
  vpc_zone_identifier       = ["${aws_subnet.ecs.*.id}"]
  min_size                  = "${var.min_size}"
  max_size                  = "${var.max_size}"
  desired_capacity          = "${var.desired_capacity}"
  health_check_type         = "EC2"
  launch_configuration      = "${aws_launch_configuration.ecs.name}"
  health_check_grace_period = "${var.health_check_grace_period}"
  load_balancers            = ["elb-${var.environment_name}-ecs"]

  tag {
    key                 = "Environment"
    value               = "${var.environment_name}"
    propagate_at_launch = true
  }

  tag {
    key                 = "Name"
    value               = "ECS ${var.cluster_name}"
    propagate_at_launch = true
  }

  #	lifecycle { create_before_destroy = true }
}

resource "aws_launch_configuration" "ecs" {
  name                 = "ECS ${var.cluster_name}"
  image_id             = "${var.ami}"
  instance_type        = "${var.instance_type}"
  iam_instance_profile = "${var.iam_instance_profile}"
  key_name             = "${var.key_name}"
  security_groups      = ["${aws_security_group.ecs_instance_sg.id}"]

  user_data = <<EOL
#! /bin/bash
echo ECS_CLUSTER=${var.cluster_name} >> /etc/ecs/ecs.config
echo ECS_ENGINE_AUTH_TYPE=dockercfg >> /etc/ecs/ecs.config
# echo ECS_ENGINE_AUTH_DATA='{\"${var.registry_url}\":{\"auth\":\"${var.registry_auth}\",\"email\":\"${var.registry_email}\"}}' >> /etc/ecs/ecs.config
EOL

  enable_monitoring = true

  #	lifecycle { create_before_destroy = true }
}
