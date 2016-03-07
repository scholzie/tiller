#! /usr/bin/env bash
# Bootstraps a host to run its first chef run

set -e
[[ $DEBUG_PROVISION_SCRIPT ]] && set -x

LOGPATH=/tmp/provision.$(date +%s).log

function help {
	echo "USAGE: ${0} <aws_region> <s3_bucket>"
	echo ""
	echo "This script is meant to run from packer. Please don't run it directly."
#	echo "Expects the following arguments (in this order):"
#	echo "\taws_region: The region in which the secrets bucket resides"
#	echo "\ts3_bucket: The bucket where the secrects exist"
	echo "Additionally, AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables must be set appropriately."
	echo ""
	exit 1
}

function teestamp {
	while IFS= read -r line; do
	    DATETIME=`date '+%b %d %H:%M:%S'`
    	echo "${DATETIME} BOOTSTRAP: ${line}"
    done | tee -a $LOGPATH
}

if [[ -z "$AWS_ACCESS_KEY_ID" ]]; then
    echo "\$AWS_ACCESS_KEY_ID is not set. Bailing." | teestamp
    exit 1
elif [[ -z "$AWS_SECRET_ACCESS_KEY" ]]; then
    echo "\$AWS_SECRET_ACCESS_KEY is not set. Bailing." | teestamp
    exit 1
elif [[ -z "$SECRET_BUCKET" ]]; then
    echo "\$SECRET_BUCKET is not set. Bailing." | teestamp
    exit 1
fi

echo "=== Starting Provisioning ===" | teestamp
echo "Writing log to $LOGPATH." | teestamp

echo "Creating /etc/chef..." | teestamp
sudo mkdir -p /etc/chef 2>&1 | teestamp

echo "apt-get update..." | teestamp
sudo apt-get update -y 2>&1 | teestamp

echo "Installing python-pip..." | teestamp
sudo apt-get install python-pip -y 2>&1 | teestamp

echo "Installing awscli..." | teestamp
sudo pip install awscli 2>&1 | teestamp

echo "Retrieving chef credentials from ${SECRET_BUCKET}..." | teestamp
aws s3 cp s3://${SECRET_BUCKET}/blueapron-validator.pem /tmp/blueapron-validator.pem 2>&1 | teestamp
sudo cp /tmp/blueapron-validator.pem /etc/chef/validation.pem 2>&1 | teestamp

echo "=== Finished ===" | teestamp
sudo mv "$LOGPATH" /root/
