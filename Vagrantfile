# -*- mode: ruby -*-
# vi: set ft=ruby :
require 'json'

ENV['VAGRANT_DEFAULT_PROVIDER'] = 'vmware_fusion'

def error(message)
  puts "\033[0;31m#{message}\033[0m"
end

SSH_KEY = File.expand_path(ENV.fetch('VAGRANT_SSH_KEY', '~/.ssh/id_rsa'))
if !File.exist?(SSH_KEY)
  error "ERROR: Please create an ssh key at the path #{SSH_KEY}"
  exit 1
end

if File.readlines(SSH_KEY).grep(/ENCRYPTED/).size > 0
  error "ERROR: GitHub SSH Key at #{SSH_KEY} contains a passphrase."
  error 'You need to generate a new key without a passphrase manually.'
  error 'See the vm documentation for more details.'
  error 'You can also override it\'s location with the environment variable VAGRANT_SSH_KEY'
  exit 1
end

git_name = %x(git config --get user.name).strip!
git_email = %x(git config --get user.email).strip!
github_user = %x(git config --get github.user).strip!

raise 'Invalid user.name in ~/.gitconfig' unless git_name
raise 'Invalid user.email in ~/.gitconfig' unless git_email
raise 'Invalid github.user in ~/.gitconfig' unless github_user

$script = <<-SCRIPT
echo "- updating deb repository"
apt-get update > /dev/null

echo "- installing base requirements"
export DEBIAN_FRONTEND=noninteractive
apt-get install -qq -y --force-yes git-core > /dev/null

echo "- ensuring proper git config"
su - vagrant -c 'git config --global user.name "#{git_name}"'
su - vagrant -c 'git config --global user.email "#{git_email}"'
su - vagrant -c 'git config --global github.user "#{github_user}"'

if ! grep -q cd-to-directory "/home/vagrant/.bashrc"; then
  echo "- setting up auto chdir on ssh"
  echo "\n[ -n \\"\\$SSH_CONNECTION\\" ] && cd /vagrant # cd-to-directory" >> "/home/vagrant/.bashrc"
fi

echo "- configuring .ssh/config file"
cat > /home/vagrant/.ssh/config <<'EOF'
Host *
  CheckHostIP yes
  ControlMaster auto
  ControlPath ~/.ssh/master-%r@%h:%p
  SendEnv LANG LC_*
  HashKnownHosts yes
  GSSAPIAuthentication no
  GSSAPIDelegateCredentials no
  RSAAuthentication yes
  PasswordAuthentication yes
  StrictHostKeyChecking no
EOF

mkdir -p /root/.ssh
cat > /root/.ssh/config <<'EOF'
Host *
  CheckHostIP yes
  ControlMaster auto
  ControlPath ~/.ssh/master-%r@%h:%p
  SendEnv LANG LC_*
  HashKnownHosts yes
  GSSAPIAuthentication no
  GSSAPIDelegateCredentials no
  RSAAuthentication yes
  PasswordAuthentication yes
  StrictHostKeyChecking no
EOF

cat > /root/.gemrc << 'EOF'
gem: --no-ri --no-rdoc
EOF

cd /vagrant

echo "- installing the service"
make install

echo "- running tests"
source .env.test && make test

echo -e "\n- ALL CLEAR! SSH access via 'vagrant ssh'."
echo "  Perform all git work on your local box. This box has no access to the nodes, outside of bootstrapping."

SCRIPT

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.ssh.forward_agent = true
  config.vm.box = "bento/ubuntu-14.04"
  config.vm.synced_folder ".", "/vagrant", type: "nfs", mount_options: ['actimeo=2']
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.hostname = "haldane.service.seatgeek.dev"

  if Vagrant.has_plugin?('vagrant-hostmanager')
    config.hostmanager.enabled = true
    config.hostmanager.ignore_private_ip = false
    config.hostmanager.include_offline = true
    config.hostmanager.manage_guest = true
    config.hostmanager.manage_host = true
    config.vm.network "private_network", ip: "10.254.0.18"
  end

  config.vm.provider "virtualbox" do |v, override|
    v.customize ["modifyvm", :id, "--rtcuseutc", "on"]
    v.customize ["modifyvm", :id, "--cpuexecutioncap", "90"]
    v.customize ["modifyvm", :id, "--memory", "1024"]
    v.customize ["modifyvm", :id, "--cpus", 2]
  end

  config.vm.provider :vmware_fusion do |v, override|
    v.vmx["memsize"] = "1024"
    v.vmx["numvcpus"] = "2"
  end

  if File.exists?(SSH_KEY)
    ssh_key = File.read(SSH_KEY)
    config.vm.provision :shell, :inline => "echo 'Copying local GitHub SSH Key to VM for provisioning...' && mkdir -p /root/.ssh && echo '#{ssh_key}' > /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa"
    config.vm.provision :shell, :inline => "echo 'Copying local GitHub SSH Key to VM for provisioning...' && mkdir -p /home/vagrant/.ssh && echo '#{ssh_key}' > /home/vagrant/.ssh/id_rsa && chmod 600 /home/vagrant/.ssh/id_rsa && chown vagrant:vagrant /home/vagrant/.ssh/id_rsa"
  else
    raise Vagrant::Errors::VagrantError, "\n\nERROR: GitHub SSH Key not found at ~/.ssh/id_rsa.\nYou can generate this key manually.\nYou can also override it with the environment variable VAGRANT_SSH_KEY\n\n"
  end

  config.vm.provision :shell do |shell|
    shell.inline = "echo 'Ensuring sudo commands have access to local SSH keys' && touch $1 && chmod 0440 $1 && echo $2 > $1"
    shell.args = %q{/etc/sudoers.d/root_ssh_agent "Defaults    env_keep += \"SSH_AUTH_SOCK\""}
  end

  config.vm.provision :shell, inline: $script
end
