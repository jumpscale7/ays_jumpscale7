import unittest
from JumpScale import j

descr = """
@ys node.docker tests
"""

organization = "jumpscale"
author = "christophe@incubaid.com"
license = "bsd"
version = "1.0"
category = "@ys.node_docker"
enable=True
priority=1
send2osis=False


class TEST(unittest.TestCase):

    def setUp(self):
        """
        executed before each test method.
        """
        pass

    def tearDown(self):
        """
        executed after each test method.
        """
        pass

    def test_templateExists(self):
        """
        test method example
        """
        tmpls = j.atyourservice.findTemplates(name='node.docker')
        print("should have only and only one @ys called node.docker")
        assert len(tmpls) == 1

        dockerTmpl = tmpls[0]

        actionsFile = j.system.fs.joinPaths(dockerTmpl.metapath, "actions.py")
        print "actions.py should exists"
        assert j.system.fs.exists(actionsFile)

        serviceHRD = j.system.fs.joinPaths(dockerTmpl.metapath, "service.hrd")
        print "service.hrd should exists"
        assert j.system.fs.exists(serviceHRD)

        instanceHRD = j.system.fs.joinPaths(dockerTmpl.metapath, "instance.hrd")
        print "instance.hrd should exists"
        assert j.system.fs.exists(instanceHRD)