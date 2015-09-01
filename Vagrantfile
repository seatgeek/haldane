# -*- mode: ruby -*-
# vi: set ft=ruby :
require 'json'

ENV['VAGRANT_DEFAULT_PROVIDER'] = 'vmware_fusion'

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
apt-get install -qq -y --force-yes build-essential git-core curl > /dev/null
apt-get install -qq -y --force-yes python-dev python-pip python-crypto > /dev/null

command -v /usr/local/bin/pip > /dev/null || {
  echo "- installing proper version of pip"
  easy_install pip > /dev/null
  pip install pip==1.4.1 > /dev/null
}

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

echo "- installing server requirements for this service"
make requirements

echo "- installing external service dependencies"
make services

echo "- setting up databases"
make database

echo "- setting up the virtualenv"
make venv

echo "- running tests"
source .env.test && make test

echo "- starting services"
make restart_services

echo -e "\n- ALL CLEAR! SSH access via 'vagrant ssh'."
echo "  Perform all git work on your local box. This box has no access to the nodes, outside of bootstrapping."

SCRIPT

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "bento/ubuntu-14.04"
  config.vm.synced_folder ".", "/vagrant", type: "nfs", mount_options: ['actimeo=2']
  config.ssh.forward_agent = true

  config.vm.network "forwarded_port", guest: 5000, host: 5000

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

  if File.exists?(File.join(Dir.home, ".ssh", "id_rsa"))
    ssh_key = File.read(File.join(Dir.home, ".ssh", "id_rsa"))
    config.vm.provision :shell, :inline => "echo 'Copying local GitHub SSH Key to VM for provisioning...' && mkdir -p /root/.ssh && echo '#{ssh_key}' > /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa"
  else
    raise Vagrant::Errors::VagrantError, "\n\nERROR: GitHub SSH Key not found at ~/.ssh/id_rsa.\nYou can generate this key manually\n\n"
  end

  config.vm.provision :shell do |shell|
    shell.inline = "echo 'Ensuring sudo commands have access to local SSH keys' && touch $1 && chmod 0440 $1 && echo $2 > $1"
    shell.args = %q{/etc/sudoers.d/root_ssh_agent "Defaults    env_keep += \"SSH_AUTH_SOCK\""}
  end

  config.vm.provision :shell, inline: $script
end
