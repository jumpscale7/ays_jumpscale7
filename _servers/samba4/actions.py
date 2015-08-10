from JumpScale import j
import signal

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
        return True

    def configure(self,serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """
        base = j.application.config.get('system.paths.base')
        base = base + '/apps/samba4'
        
        # Install sernet repository on system
        j.system.process.run("dpkg -i " + base + "/sernet-samba-keyring_1.4_all.deb", True, False)

        # Check if sources.list contains sernet packages server
        if 'download.sernet.de/packages/samba/4.2/ubuntu' not in open('/etc/apt/sources.list').read():
            print 'Adding sources.list sernet repository'
            j.system.fs.writeFile('/etc/apt/sources.list', "\n", True)
            j.system.fs.writeFile('/etc/apt/sources.list', "# Samba sernet\n", True)
            j.system.fs.writeFile('/etc/apt/sources.list', "deb https://sernet-samba-public:Noo1oxe4zo@download.sernet.de/packages/samba/4.2/ubuntu trusty main\n", True)

            # Update packages list
            j.system.platform.ubuntu.updatePackageMetadata()

        # Install samba
        j.system.platform.ubuntu.install("sernet-samba-client sernet-samba-ad")
        j.system.fs.createDir('/var/run/samba/')

        # Loading hrd settings
        myaddr = serviceObj.hrd.get('instance.param.ad.ipaddr')
        domain = serviceObj.hrd.get('instance.param.ad.domain')
        realm  = serviceObj.hrd.get('instance.param.ad.realm')
        remote = serviceObj.hrd.get('instance.param.ad.remote')
        passwd = serviceObj.hrd.get('instance.param.ad.adminpwd')
        
        # Saving old files
        if j.system.fs.exists('/etc/samba/smb.conf'):
            j.system.fs.moveFile('/etc/samba/smb.conf', '/etc/samba/smb.conf.bak')

        # Skipping AD if no domain is set
        if not remote == '':
            print 'Joining Active Directory', realm, '/', myaddr
            
            # Update resolv.conf
            j.system.fs.writeFile('/etc/resolv.conf', "domain " + realm + "\n", False)
            j.system.fs.writeFile('/etc/resolv.conf', "nameserver " + remote + "\n", True)
            
            # Setup /etc/hosts
            
            
            # Building smb.conf file
            j.system.fs.copyFile(base + '/smb.member.conf', '/etc/samba/smb.conf')
            
            data = {
                'hostname': j.system.net.getHostname(),
                'workgroup': domain,
                'realm': realm
            }
            
            hrd = j.core.hrd.getHRDFromDict(data)
            hrd.applyOnFile('/etc/samba/smb.conf')
            
            # Reload config
            j.system.process.killProcessByName('smbd', signal.SIGHUP)
            j.system.process.killProcessByName('nmbd', signal.SIGHUP)
            
            # Joining domain
            j.system.process.run("net ads join -U Administrator%" + passwd, True, False, 10, False)
            
            # Enable remote auth with nsswitch.conf
            
            
            
        else:
            print 'Setting up new Active Directory:', realm, '/', domain

            # Provision AD
            options = "--domain " + domain + " --realm " + realm + " --adminpass " + passwd
            j.system.process.run("samba-tool domain provision --use-rfc2307 " + options, True, False)

            # Update resolv.conf
            j.system.fs.writeFile('/etc/resolv.conf', "domain " + realm + "\n", False)
            j.system.fs.writeFile('/etc/resolv.conf', "nameserver 127.0.0.1\n", True)

        return True
