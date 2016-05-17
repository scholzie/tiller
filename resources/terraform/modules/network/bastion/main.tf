# A module for all resources related to a Bastion host within the global config

variable "name" {
  default = "bastion"
}

variable "vpc_id" {
}

variable "vpc_cidr" {
}

variable "region" {
}

variable "public_subnet_ids" {
}

variable "key_name" {
}

variable "instance_type" {
}

variable "ami" {
}

resource "aws_security_group" "bastion" {
  name        = "${var.name}"
  vpc_id      = "${var.vpc_id}"
  description = "Bastion SG"

  tags {
    Name = "${var.name}"
    role = "global"
  }

  lifecycle {
    create_before_destroy = true
  }

  # Allow all inbound traffic within the VPC, egress to anywhere, and SSH from anywhere
  ingress {
    protocol    = "-1"
    cidr_blocks = ["${var.vpc_cidr}"]
    from_port   = 0
    to_port     = 0
  }

  ingress {
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 22
    to_port     = 22
  }

  egress {
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 0
    to_port     = 0
  }
}

resource "aws_instance" "bastion" {
  ami                         = "${var.ami}"
  instance_type               = "${var.instance_type}"
  subnet_id                   = "${element(split(",", var.public_subnet_ids), count.index)}"
  key_name                    = "${var.key_name}"
  vpc_security_group_ids      = ["${aws_security_group.bastion.id}"]
  associate_public_ip_address = true

  tags {
    Name = "${var.name}"
    role = "global"
  }

  lifecycle {
    create_before_destroy = true
  }
}

output "user" {
  value = "ubuntu"
}

output "private_ip" {
  value = "${aws_instance.bastion.private_ip}"
}

output "public_ip" {
  value = "${aws_instance.bastion.public_ip}"
}

output "public_dns" {
  value = "${aws_instance.bastion.public_dns}"
}

output "key_name" {
  value = "${aws_instance.bastion.key_name}"
}
