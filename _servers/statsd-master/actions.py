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
        after this step the system will try to start the ays if anything needs to be started
        """
        influx_instance = serviceObj.hrd.get('instance.param.influxdb.connection')
        hrd = j.application.getAppInstanceHRD('influxdb_client', influx_instance)
        template = {
            'host' : hrd.get('instance.param.influxdb.client.address'),
            'port': hrd.get('instance.param.influxdb.client.port'),
            'login' : hrd.get('instance.param.influxdb.client.login'),
            'passwd' : hrd.get('instance.param.influxdb.client.passwd'),
            'dbname' : hrd.get('instance.param.influxdb.client.dbname')

        }

        configsamplepath = j.system.fs.joinPaths('/opt/', 'statsd-master', 'MasterConfig.js')
        configpath = j.system.fs.joinPaths('/opt/', 'statsd-master', 'statsd.master.conf.js')
        if not j.system.fs.exists(configpath):
            j.system.fs.createEmptyFile(configpath)

        j.system.fs.copyFile(configsamplepath, configpath)
        hrd.applyOnFile(configpath, template)
