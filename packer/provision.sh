#! /usr/bin/env bash
# Bootstraps a host to run its first chef run

function help {
	echo "USAGE: ${0} <aws_region> <s3_bucket>"
	echo ""
	echo "This script is meant to run from packer. Please don't run it directly."
	echo "Expects the following arguments (in this order):"
	echo "\taws_region: The region in which the secrets bucket resides"
	echo "\ts3_bucket: The bucket where the secrects exist"
	echo "Additionally, AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables must be set appropriately."
	echo ""
	exit 1
}

# TODO: get region and bucket from terraform output. For now, just require it as input
if [ $# -ne 2 ]; then 
	echo "Invalid number of arugments."
	help
fi
AWS_REGION="$1" 
S3_BUCKET="$2"

function teestamp {
	while IFS= read -r line; do
	    DATETIME=`date '+%b %d %H:%M:%S'`
    	echo "${DATETIME} BOOTSTRAP: ${line}"
    done | tee -a /tmp/provision.log
}

echo "=== Starting Provisioning ==="  2>&1 | teestamp

echo "Creating /etc/chef..."  2>&1 | teestamp
sudo mkdir -p /etc/chef 2>&1 | teestamp

echo "apt-get update..."  2>&1 | teestamp
sudo apt-get update -y 2>&1 | teestamp

echo "Installing python-pip..."  2>&1 | teestamp
sudo apt-get install python-pip -y 2>&1 | teestamp

echo "Installing awscli..."  2>&1 | teestamp
sudo pip install awscli 2>&1 | teestamp

echo "Retrieving chef credentials from ${BUCKET}:${S3_BUCKET}..."  2>&1 | teestamp
aws s3 cp s3://${BUCKET}/blueapron-validator.pem /tmp/blueapron-validator.pem 2>&1 | teestamp
sudo cp /tmp/blueapron-validator.pem /etc/chef/validation.pem 2>&1 | teestamp

echo "=== Finished ===" 2>&1 | teestamp  2>&1 | teestamp