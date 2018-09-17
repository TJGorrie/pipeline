import datetime
import os
import filecmp

import luigi
from paramiko import SSHClient
from scp import SCPClient

import setup_django

setup_django.setup_django()

from .config_classes import VerneConfig
from xchem_db.models import *


class TransferDirectory(luigi.Task):
    username = VerneConfig().username
    hostname = VerneConfig().hostname
    remote_directory = luigi.Parameter()
    local_directory = luigi.Parameter()
    remote_root = VerneConfig().remote_root

    def run(self):
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(self.hostname, username=self.username)
        sftp = ssh.open_sftp()
        try:
            sftp.stat(self.remote_directory)
        except FileNotFoundError:
            f_path = ''
            for f in self.remote_directory.replace(self.remote_root, '').split('/'):
                f_path += str('/' + f)
                try:
                    sftp.stat(str(self.remote_root + f_path))
                except FileNotFoundError:
                    sftp.mkdir(str(self.remote_root + f_path))
            scp = SCPClient(ssh.get_transport())
            scp.put(self.local_directory, recursive=True, remote_path=self.remote_directory)
            scp.close()


class GetTransferDirectories(luigi.Task):
    remote_root = VerneConfig().remote_root
    timestamp = luigi.Parameter(default=datetime.datetime.now().strftime('%Y-%m-%dT%H'))

    def requires(self):
        proasis_out = ProasisOut.objects.all()
        paths = list(set([os.path.join(o.root, o.start) for o in proasis_out if o.root and o.start]))
        transfer_checks = []

        for p in paths:
            if os.path.isdir(p):
                transfer_checks.append(p)

        return [TransferDirectory(remote_directory=os.path.join(self.remote_root, self.timestamp,
                                                                '/'.join(p.split('/')[-3:])), local_directory=p)
                for p in transfer_checks]



