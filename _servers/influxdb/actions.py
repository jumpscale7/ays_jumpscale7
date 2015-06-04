from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):
    def configure(self, service):
        fname = '$(service.param.base)/cfg/influxdb/config.toml'
        cfg = j.system.fs.fileGetContents(fname)

        cfg = j.dirs.replaceTxtDirVars(cfg, additionalArgs={})
        j.system.fs.writeFile(fname, cfg)
