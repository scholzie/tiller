# Discrete Service Config

variable "service_name" {
}

variable "vpc_id" {
}

variable "subnet_id" {
}

variable "key_name" {
}

variable "policy_name" {
}

variable "ami" {
}

variable "host_environment" {
}

variable "access_key" {
}

variable "secret_key" {
}

variable "region" {
}

variable "instance_type" {
  default = "t2.micro"
}

variable "public" {
  default = true
}

provider "aws" {
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region     = "${var.region}"
}

resource "aws_security_group" "discrete_service" {
  name   = "${var.service_name}-service-sg"
  vpc_id = "${var.vpc_id}"
}

# TODO: should move this to a module, or something similar and share the rules
resource "aws_security_group_rule" "allow_ssh" {
  type      = "ingress"
  from_port = 22
  to_port   = 22
  protocol  = "tcp"

  # TODO: move to only whitelist office ip?
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.discrete_service.id}"
}

resource "aws_security_group_rule" "allow_icmp" {
  type              = "ingress"
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = -1
  to_port           = -1
  protocol          = "icmp"
  security_group_id = "${aws_security_group.discrete_service.id}"
}

resource "aws_security_group_rule" "allow_HTTP" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.discrete_service.id}"
}

resource "aws_security_group_rule" "allow_HTTPS" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.discrete_service.id}"
}

resource "aws_security_group_rule" "allow_ALL_egress" {
  type              = "egress"
  from_port         = 0
  to_port           = -1
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.discrete_service.id}"
}

resource "template_file" "first-boot" {
  template = "${file("${path.cwd}/../templates/discrete-service/user-data.tpl")}"

  vars {
    host_environment = "${var.host_environment}"
    policy_name      = "${var.policy_name}"
  }
}

resource "aws_instance" "service" {
  subnet_id                   = "${var.subnet_id}"
  key_name                    = "${var.key_name}"
  monitoring                  = true
  ami                         = "${var.ami}"
  instance_type               = "${var.instance_type}"
  associate_public_ip_address = "${var.public}"
  vpc_security_group_ids      = ["${aws_security_group.discrete_service.id}"]
  depends_on                  = ["aws_security_group.discrete_service"]

  user_data = "${template_file.first-boot.rendered}"

  tags {
    Name = "${var.service_name}-service"
  }
}

output "public_dns" {
  value = "${aws_instance.service.public_dns}"
}

output "host_environment" {
  value = "${var.host_environment}"
}

output "policy_name" {
  value = "${var.policy_name}"
}
