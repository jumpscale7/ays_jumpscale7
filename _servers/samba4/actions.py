from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):
    """
    process for install
    -------------------
    step1: prepare actions
    step2: check_requirements action
    step3: download files & copy on right location (hrd info is used)
    step4: configure action
    step5: check_uptime_local to see if process stops  (uses timeout $process.stop.timeout)
    step5b: if check uptime was true will do stop action and retry the check_uptime_local check
    step5c: if check uptime was true even after stop will do halt action and retry the check_uptime_local check
    step6: use the info in the hrd to start the application
    step7: do check_uptime_local to see if process starts
    step7b: do monitor_local to see if package healthy installed & running
    step7c: do monitor_remote to see if package healthy installed & running, but this time test is done from central location
    """
    def prepare(self,serviceObj):
        """
        this gets executed before the files are downloaded & installed on appropriate spots
        """
	# Download keyring for sernet repository
	j.system.net.download('http://ftp.sernet.de/pub/sernet-samba-keyring_1.4_all.deb', '/tmp/')
        return True

    def configure(self,serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """
	# Install sernet repository on system
        j.system.process.run("dpkg -i /tmp/sernet-samba-keyring_1.4_all.deb", True, False)

	# Check if sources.list contains sernet packages server
	if 'download.sernet.de/packages/samba/4.2/ubuntu' not in open('/etc/apt/sources.list').read():
		print 'Adding sources.list sernet repository'
		with open('/etc/apt/sources.list', 'a') as sourceslist:
			sourceslist.write("\n")
			sourceslist.write("# Samba sernet\n")
			sourceslist.write("deb https://sernet-samba-public:Noo1oxe4zo@download.sernet.de/packages/samba/4.2/ubuntu trusty main\n")

	# Update packages list
	j.system.process.run("apt-get update", True, False)

	# Install samba
	j.system.process.run("apt-get install -y sernet-samba-client sernet-samba-ad", True, False)
	j.system.fs.createDir('/var/run/samba/')

	# Loading hrd settings
	domain = serviceObj.hrd.get('instance.param.ad.domain')
	realm  = serviceObj.hrd.get('instance.param.ad.realm')
	passwd = serviceObj.hrd.get('instance.param.ad.adminpwd')
        
	# Skipping AD if no domain is set
	if not domain == '*':
		print 'Setting up Active Directory:', realm, '/', domain
		# Removing old files
		j.system.fs.moveFile('/etc/samba/smb.conf', '/etc/samba/smb.conf.bak')

		# Provision AD
		options = "--domain " + domain + " --realm " + realm + " --adminpass " + passwd
		j.system.process.run("samba-tool domain provision --use-rfc2307 " + options, True, False)
		
		# Update resolv.conf
		with open('/etc/resolv.conf', 'w') as resolv:
			resolv.write("domain " + realm + "\n")
			resolv.write("nameserver 127.0.0.1\n")
			
	else:
		print 'Active Directory not enabled, skipping'
	
	return True
