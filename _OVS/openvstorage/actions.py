from JumpScale import j
import time
import os
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
	j.do.execute('echo "deb http://apt-ovs.cloudfounders.com unstable/" > /etc/apt/sources.list.d/ovsaptrepo.list')
	j.system.fs.createEmptyFile('/tmp/openvstorage_preconfig.cfg')
	j.do.execute('apt-get update && apt-get install kvm libvirt0 python-libvirt virtinst')
	j.do.execute('apt-get install ntp')
        j.do.execute('apt-get install -y --force-yes openvstorage-hc')
	j.do.execute('apt-get install -y --force-yes openvstorage')
        

    def configure(self,serviceObj):
        j.do.execute('echo "" > /tmp/openvstorage_preconfig.cfg')	
        content = '[setup] \n target_ip = $ instance.param.targetip \n target_password = $ instance.param.targetpasswd \n cluster_name = $ instance.param.clustername \ncluster_ip = $ instance.param.clusterip \n master_ip = $ instance.param.masterip \n master_password = $ instance.param.masterpasswd \n join_cluster = False \n hypervisor_type = KVM \n hypervisor_name = kvm001 \n hypervisor_ip = $ instance.param.hvip  hypervisor_username = root  \n hypervisor_password = $ instance.param.hvpasswd \n arakoon_mountpoint = $ instance.param.db \n verbose = True \n disk_layout = {} \n auto_config = True '	
        j.do.writeFile('/tmp/openvstorage_preconfig.cfg',content)
        j.do.execute('ovs setup')    	
        return True


    def stop(self,serviceObj):
	pass