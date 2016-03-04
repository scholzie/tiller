# ba-base box
The ba-base box will provision an AMI from the base ubuntu 14.04 image and
bootstrap it to communicate with our hosted Chef server.

## Environment Variables
The following variables must be passed to packer:
- `aws_access_key`: Self-explanatory. **Default:** `$PACKER_AWS_ACCESS_KEY_ID`
- `aws_secret_key`: Self-explanator. **Default:** `$PACKER_SECRET_ACCESS_KEY`
- `vpc_id`: (Currently unused) The VPC where the build instance will be spun up.
  **Default:** `$PACKER_VPC_ID`
- `subnet_id`: (Currenlty unused) The subnet where the build instance will be
  spun up. **Default:** `$PACKER_SUBNET_ID`
- `s3_bucket`: Bucket containing the chef validation.pem. **Default:** `$PACKER_S3_BUCKET`
- `aws_region`: The region in which the ami will be built. **Default:** `us-east-1`
- `source_ami`: **Default: ** `ami-fce3c696`, the Ubuntu 14.04 image in us-east-1
