variable "name" {
  default = "nat"
}

variable "azs" {
}

variable "public_subnet_ids" {
}

resource "aws_eip" "nat" {
  vpc   = true
  count = "${length(split(",", var.azs))}"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_nat_gateway" "nat" {
  count         = "${length(split(",", var.azs))}"
  allocation_id = "${element(aws_eip.nat.*.id, count.index)}"
  subnet_id     = "${element(split(",", var.public_subnet_ids), count.index)}"

  lifecycle {
    create_before_destroy = true
  }
}

output "nat_gateway_ids" {
  value = "${join(",", aws_nat_gateway.nat.*.id)}"
}

output "nat_eip_public_ips" {
  value = "${join(",", aws_eip.nat.*.public_ip)}"
}

output "nat_eip_private_ips" {
  value = "${join(",", aws_eip.nat.*.private_ip)}"
}
