from JumpScale import j
import time
import socket
import fcntl
import struct

ActionsBase = j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):
    

    def configure(self, serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """
        influx_instance = serviceObj.hrd.get('instance.param.influxdb.connection')
        hrd = j.application.getAppInstanceHRD('influxdb_client', influx_instance)
        host = hrd.get('instance.param.influxdb.client.address')

        if j.system.net.isIpLocal(host):
            host = 'window.location.hostname'
        else:
            host = "'%s'" % host

        configsamplepath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'portals', 'jslib', 'grafana', 'config.sample.js')
        configpath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'portals', 'jslib', 'grafana', 'config.js')
        if not j.system.fs.exists(configpath):
            j.system.fs.createEmptyFile(configpath)

        j.system.fs.copyFile(configsamplepath, configpath)
        hrd.applyOnFile(configpath)
