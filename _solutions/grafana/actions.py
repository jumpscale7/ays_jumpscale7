from JumpScale import j
import requests
import json

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def prepare(self, serviceObj):
        j.system.fs.createDir("/opt/grafana")
        j.system.fs.createDir("/opt/grafana/conf")
        j.system.fs.createDir("/opt/grafana/public")

    def configure(self, serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """
        influx_instance = serviceObj.hrd.get('instance.param.influxdb.connection')
        hrd = j.application.getAppInstanceHRD('influxdb_client', influx_instance)
        host = hrd.getStr('instance.param.influxdb.client.address')
        port = hrd.getInt('instance.param.influxdb.client.port')
        login = hrd.getStr('instance.param.influxdb.client.login')
        passwd = hrd.getStr('instance.param.influxdb.client.passwd')
        dbname = hrd.getStr('instance.param.influxdb.client.dbname')

        data = {
          'type': 'influxdb',
          'access': 'proxy',
          'database': dbname,
          'name': 'influxdb_main',
          'url': 'http://%s:%u' % (host, port),
          'user': login,
          'password': passwd,
          'default': True,
        }

        # need to start the grafana backend server to enable http api
        serviceObj.start()

        # check if the datasource already exists
        grafanaAPI = 'http://admin:admin@localhost:%s/api/datasources' % serviceObj.hrd.get('instance.param.port')

        try:
            resp = requests.get(grafanaAPI)
        except Exception as e:
            from ipdb import set_trace;set_trace()
            j.events.opserror_critical(e.message)

        datasources = json.loads(resp.content)
        present = False
        for ds in datasources:
            if ds['url'] == data['url'] and ds['user'] == data['user'] and \
               ds['password'] == data['password'] and ds['access'] == data['access']:
               present = True

        if not present:

            # create the datasource for influxdb
            try:
                resp = requests.post(grafanaAPI, json=data,
                                     headers={'content-type': 'application/json'})
            except Exception as e:
                j.events.opserror_critical(e.message)
