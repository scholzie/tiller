#
# Cookbook Name:: ba_base
# Recipe:: filebeat_client

# Copyright (c) 2015 Blue Apron, All Rights Reserved.

include_recipe 'filebeat'

s3_file node[:ba][:logstash][:ca_location] do
  remote_path node[:ba][:logstash][:aws][:key]
  bucket node[:ba][:logstash][:aws][:bucket]
  aws_access_key_id node[:ba][:logstash][:aws][:access_key]
  aws_secret_access_key node[:ba][:logstash][:aws][:secret_access_key]
  action :create
end

# rewriting config as first pass using node attributes is incorrect
template '/etc/filebeat/filebeat.yml' do
  source 'filebeat.yaml.erb'
  owner 'root'
  group 'root'
  mode '0755'
  variables({
    :logstash_host =>  node[:ba][:logstash][:host],
    :ca_location => node[:ba][:logstash][:ca_location]
  })
end

service 'filebeat' do
  action :restart
end
