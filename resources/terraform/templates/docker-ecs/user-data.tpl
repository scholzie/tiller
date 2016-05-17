#!/bin/bash

mkdir /etc/blueapron
echo "${ecs_cluster}" > /etc/blueapron/ecs-cluster

cat <<CHEFCONFIG > /etc/chef/first-boot.json
{
	"ba-ecs-agent"	: {
		"cluster": "${ecs_cluster}"
	},
	"run_list": [ "role[${ecs_host_role}]" ]
}
CHEFCONFIG

chef-client --environment ${ecs_host_environment} -j /etc/chef/first-boot.json