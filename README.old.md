# Synopsis
Tools to create an infrastructure for supporting dockerized applications.

## Contents:
| Directory | Description | 
| --- | --- |
| chef/ | Cookbooks for maintaning infrastructure. _This will almost certainly move to its own repository_ |
| packer/ | Configuration for creating the EC2 AMI for the EC2 Container Service |
| terraform/ | Configuration for creating all of the infrastructure in AWS |
| poutine | A wrapper script for executing terraform commands | 

# Requirements
To run these tools you will need a few things:
### An (empty) AWS account
- This tool will be creating tons of resources. Chances are, unless you have
  previously taken steps to avoid it, you will hit resource limits by running
  this against an account that is not already empty.
- Set up a non-root user with administrative privileges. Note the access key ID
  and secret access key.

### A bucket for secrets. A "secret bucket".
Create an S3 bucket (with versioning, preferably) to store secrets in. 

These secrets will include: 
- the active tfstate, to maintain state between terraform runs by different people
- a backup of tfstate, tagged with the user who created it, environment, and
  date. This is nice to have if the world explodes and the aforementioned tfstate can't
  be trusted to be the truth anymore.
- Chef's validation.pem file

*NB: Because of the sensitive nature of this data, access to this bucket should be
tighly controlled.* Open it for use to the user you created for this tool. 

### A good sense of humor
Because it probably won't work the first time.

# Use
To build any of the **Roles** in the terraform directory, you must first have a
working "global" network configuration. See README.md under the
[terraform](terraform)
directory for information on what this does, precisely.

### Create the network
- Enter the `terraform/network` directory and edit terraform.tfvars
  appropriately:
  - `cp terraform.tfvars.sample terraform.tfvars`
  - `access_key`: your AWS Access Key ID
  - `secret_key`: the Secret Access Key for the above ID
  - `environment_name`: will be overridden (as it's required input to run the
    script) - it's only there if you run terraform manually
  - `azs`: update this with the Availability Zones accessible by your account.
    You can find these by running `aws ec2   -describe-availability-zones`
- Plan it: `./poutine plan <env> network`, where `<env>` is something like
  `prod`, `staging`, or `dev`
- Examine the output and be sure it makes sense.
- Apply it: `./poutine apply <environment> network`
- Keep note of all the outputs! You will need some of these later.
  - *NB:* Due to either a bug with terraform or an AWS race condition,
   occasionally the NAT EIPs will not output (you will see ",,," if that happens).
   You can run another command like `refresh` or `apply` or `plan` to get these
   values to output. Or go look in your account later. You don't need them for 
   the next step.

### Test your bastion host
To make sure the network came up and the bastion host is properly provisioned,
test logging into your bastion host from your laptop.

`ssh -i <bastion_key> <bastion_user>@<bastion_public_ip>`

### Deploy an ECS cluster
Once you have an operating network, you can then deploy the docker ECS cluster.
- First, build the packer image:
  - RTFM in the packer directory, then:
  - `pushd packer && packer build ba-base.json && popd`
  - take note of the ami-id when the build is complete.
- RTFM in the terraform/docker-ecs directory
- `cd terraform/docker-ecs`
- `cp terraform.tfvars.sample terraform.tfvars`
- `vim terraform.tfvars`
  - Set `access_key` and `secret_key` as before
  - `secret_bucket`: the secrets bucket in s3
  - `key_name`: the key pair name you want to be applied to instances. This key
   must already exist.
  - `cluster_name`: the name you want to assign to your ECS cluster
  - `subnets`: comma-delimited list of subnet-ids (from network apply earlier)
  - `vpc_id`: vpc-id from the network setup
  - `ami`: The ami-id from the packer step above.
  - `registry_url`: Until the registry creation step is automated, replace this
   with the endpoint URI for the docker registry you are using.
  - adjust other variables as you see fit.
- `./poutine apply <env> docker-ecs`, where `<env>` is the same one you used
  earlier during network creation.

### Test connectivity to one of the ECS hosts
To make sure networking is working properly to your ECS hosts, pick one at
random and attempt to ssh into it from your bastion.
```bash
# Copy your ecs key to the bastion
cscholz@laptop$ scp -i <bastion_key> <ecs_key> <bastion_user>@<bastion_public_ip>:~
# SSH to the bastion
cscholz@laptop$ ssh -i <bastion_key> <bastion_user>@<bastion_public_ip>
# Use the key to attempt to connect to the ecs host
ubuntu@bastion$ ssh -i <ecs_key> ubuntu@<ec2_node_public_ip>
```

### Check that your ECS cluster has provisioned properly
If the ECS nodes came up correctly, they should have initilized ECS-agent and
auto-joined the cluster you created. To check this, go to the 
[Amazon ECS](https://console.aws.amazon.com/ecs) console, go to the cluster you
created, click the ECS Instances tab, and ensure that the instances listed are
indeed the ones that were created in the deployment step. 

# If something is broken :shit:
Blame @jackdwyer

# If everything works :sparkles:
Thank @scholzie

# To Do:
Task list - please claim, and/or update README with links to tasks or commits where appropriate.
- [ ] poutine/poutine: Add packer run functionality 
- [ ] poutine/poutine: Rename project "tiller", ./poutine -> ./till
- [ ] poutine/poutine: Capture output from network creation and pre-fill terraform.tfvars sample for other modules
- [ ] poutine/poutine: Add help system (see https://github.com/docopt/docopt)
- [ ] poutine/poutine: Make this a little nicer, if you feel like it.
- [ ] docker-ecs/main.tf: Investigate what SG rules are needed for apps to work
- [ ] docker-ecs/main.tf: Figure out subnets automatically. Either use a module, or pre-fill from network output
test
