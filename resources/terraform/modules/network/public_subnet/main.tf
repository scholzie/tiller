variable "name" {
  default = "public-sn"
}

variable "vpc_id" {
}

variable "cidr_seed" {
}

variable "azs" {
}

resource "aws_internet_gateway" "public" {
  vpc_id = "${var.vpc_id}"

  tags {
    Name = "${var.name}"
    role = "global"
  }
}

# Create the subnet
resource "aws_subnet" "public" {
  vpc_id = "${var.vpc_id}"

  cidr_block        = "${cidrsubnet(var.cidr_seed, 8, count.index)}"
  availability_zone = "${element(split(",", var.azs), count.index)}"
  count             = "${length(split(",", var.azs))}"

  tags {
    Name = "${var.name}.${element(split(",", var.azs), count.index)}-public"
    role = "global"
  }

  lifecycle {
    create_before_destroy = true
  }

  map_public_ip_on_launch = true
}

# Assign a route table
resource "aws_route_table" "public" {
  vpc_id = "${var.vpc_id}"

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.public.id}"
  }

  tags {
    Name = "${var.name}.${element(split(",", var.azs), count.index)}-public"
    role = "global"
  }
}

# Associate route table and subnets
resource "aws_route_table_association" "public" {
  count          = "${length(split(",", var.azs))}"
  subnet_id      = "${element(aws_subnet.public.*.id, count.index)}"
  route_table_id = "${aws_route_table.public.id}"
}

output "subnet_ids" {
  value = "${join(",", aws_subnet.public.*.id)}"
}

output "cidr_blocks" {
  value = "${join(",", aws_subnet.public.*.cidr_block)}"
}
