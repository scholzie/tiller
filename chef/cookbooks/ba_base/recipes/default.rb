#
# Cookbook Name:: ba_base
# Recipe:: default

# Copyright (c) 2015 Blue Apron, All Rights Reserved.

Chef::Log.warn("ENVIRONMENT: #{node.chef_environment}")

include_recipe 'apt'
include_recipe 'openssh'
include_recipe 'users::sysadmins'
include_recipe 'sudo'
include_recipe 'ba_base::filebeat_client'

if node[:etc][:passwd][:vagrant] and not %w(production staging).include? node.chef_environment
  Chef::Log.warn("Patching vagrant user to be in sysadmin group")
  package ['vim', 'curl']
  %w(vagrant).each do |user|
    if node['etc']['passwd']["#{user}"]
      user "#{user}" do
        ignore_failure true
        action :modify
        gid 'sysadmin'
      end
    end
  end
end
