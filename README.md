# poutine
A library of tools for deploying Dockerized applications into AWS ECS clusters

Currently, running `terraform apply` will create the following resources in your AWS account:
- A new VPC
-- Internet Gateway and Routes for the VPC
- One subnet per Availability Zone
- A new ECS Cluster
- Security Groups
-- ELB SG
-- EC2 Instance SG
- Elastic Load Balancer
- Autoscaling Group
- Launch Configuration
-- Instaces spawned using this LC will automatically join the cluster created earlier

## Requirements
- An AMI which contains the ecs-agent. This will eventually be an AMI built
  with packer, but can either be the hand-built AMI we created or Amazon's ECS
  image.
- An AWS IAM Role with AmazonEC2ContainerServiceforEC2Role permissions
- A registry account for Docker images (you get one "for free" with AWS ECS.
  You will not need to set the `registry_*` variables if you use it.

## Directions
- `cp terraform.tfvars.example terraform.tfvars`
  Edit this file with appropriate values. Alternatively you may override any of
  these variables by settging environment variables prior to `terraform`
  execution, like so:
  `TF_<VARIABLE_NAME>="value"`
- Run `terraform apply` and inspect the proposed changes to your
  infrastructure.
- Run `terraform apply` to apply the changes.
