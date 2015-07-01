import unittest
from JumpScale import j

descr = """
docker tool tests
"""

organization = "jumpscale"
author = "christophe@incubaid.com"
license = "bsd"
version = "1.0"
category = "@ys.node.docker"
enable=True
priority=1
send2osis=False

class CreateContainer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        executed before each test method.
        """
        cls.containerName = "test_jumpscale_image"
        cls.image = "zerocomp/base:latest"

    @classmethod
    def tearDownClass(cls):
        """
        executed after each test method.
        """
        j.tools.docker.destroy(cls.containerName)

    def test_create(self):
        j.tools.docker.create(name=self.containerName,ports="",vols="",volsro="",stdout=True,base=self.image,nameserver="8.8.8.8",replace=True,cpu=None,mem=0,jumpscale=False,ssh=True,myinit=True)

        containers = j.tools.docker.list()
        self.assertTrue(len(containers) > 0,"container should exists")
        self.assertTrue(self.containerName.lower() in containers,"container should exists")

        infos = j.tools.docker.getInfo(self.containerName)
        self.assertEqual(infos['Image'], self.image, "image\nexpected: %s\nactual:%s\n" % (self.image,infos['Image']))

        self.assertTrue(infos['Status'].find('Up') != -1, "container should be up and running")

class SSHConnection(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        def createFile():
            dir = "/tmp/test-docker"
            j.system.fs.createDir(dir)
            path = j.system.fs.joinPaths(dir, 'test.txt')
            content = "Hello world"
            j.system.fs.writeFile(path, content)
            return (path, content)

        cls.fileLoc, cls.fileContent = createFile()

        cls.containerName = "test_jumpscale_image"
        cls.image = "zerocomp/base:latest"
        j.tools.docker.create(name=cls.containerName,ports="",vols="",volsro="",stdout=True,base=cls.image,nameserver="8.8.8.8",replace=True,cpu=None,mem=0,jumpscale=False,ssh=True,myinit=True)

    @classmethod
    def tearDownClass(cls):
        j.tools.docker.destroy(cls.containerName)
        j.system.fs.remove(cls.fileLoc)
        dir = j.system.fs.getBaseName(cls.fileLoc)
        j.system.fs.removeDirTree(dir)


    def test_sshConnection(self):
        conn = j.tools.docker.getSSH(self.containerName)
        self.assertIsNotNone(conn, "should return a cuisine connection")
        # cuisine use lazy connection,
        # send command to force connection
        conn.run('ls /')

    def test_uploadFileToContainer(self):
        j.tools.docker.uploadFile(self.containerName, self.fileLoc, self.fileLoc)
        conn = j.tools.docker.getSSH(self.containerName)
        content = conn.file_read(self.fileLoc)
        self.assertEqual(content, self.fileContent, "remote file should have same content as locale file\nexpected:%s\nactuel:%s" % (self.fileContent, content))
        j.system.fs.remove(self.fileLoc)

    def test_downloadFileFromContainer(self):
        conn = j.tools.docker.getSSH(self.containerName)
        ddir = j.system.fs.getDirName(self.fileLoc)
        conn.run("mkdir -p %s" % ddir)
        conn.file_write(self.fileLoc, self.fileContent)

        j.tools.docker.downloadFile(self.containerName, self.fileLoc, self.fileLoc)
        content = j.system.fs.fileGetContents(self.fileLoc)
        self.assertEqual(content, self.fileContent, "local file should have same content as remote file\nexpected:%s\nactuel:%s" % (self.fileContent, content))

        conn.run("rm -r %s" % ddir)