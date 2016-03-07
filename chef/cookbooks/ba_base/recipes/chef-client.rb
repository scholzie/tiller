#
# Cookbook Name:: ba_base
# Recipe:: chef-client
# Description:
#   Sets up necessary components for chef to register a client node
#
# Copyright (c) 2016 Blue Apron, Inc. 

template '/etc/chef/client.rb' do
    source 'client.rb.erb'
    owner 'root'
    group 'root'
    mode '0755'
end
