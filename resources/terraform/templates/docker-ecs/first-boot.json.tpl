{
	"ecs-agent"	: {
		"cluster": "${ecs_cluster}"
	},
	"run_list": [ "role[${ecs_host_role}]" ]
}
