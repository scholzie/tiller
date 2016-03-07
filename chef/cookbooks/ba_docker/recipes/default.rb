#
# Cookbook Name:: ba-docker
# Recipe:: default
#
# Copyright (c) 2016 The Authors, All Rights Reserved.
#

docker_service 'default' do
    action [:create, :start]
end
