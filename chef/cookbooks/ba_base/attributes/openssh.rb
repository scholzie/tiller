override["openssh"]["server"] = {
  "port" => "22",
  "address_family" => 'any',
  "listen_address" => [ '0.0.0.0', '::' ],
  "password_authentication" => "no",
  "protocol" => "2",
  "x11_forwarding" => "no",
  "permit_root_login" => "no",
  "strict_modes" => "yes",
  "host_based_authentication" => "no",
  "permit_empty_passwords" => "no",
  "G_s_s_a_p_i_authentication" => "no",
  "_use_d_n_s" => "no"
}

override["openssh"]["client"]["*"]["_use_roaming"] = "no"
