# -*- coding: utf-8 -*-
# Copyright Onestein (https://www.onestein.eu).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import openerp.tools as tools
import subprocess

import openerp.addons.web.controllers.main as main
from openerp import http
from openerp.service.common import exp_version


class WebClient(main.WebClient):

    @http.route('/web/webclient/version_info', type='json', auth="none")
    def version_info(self):
        """Get Git release tags for repositories in the addons path."""
        versions = []
        # Get addons path
        for addon_path in tools.config['addons_path'].split(','):
            # Get version number
            cmd = ["git", "describe", "--tags"]
            proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    cwd=addon_path)
            output = proc.communicate()[0]
            # Check if it is a git repo and hide standard saas repos
            if proc.returncode == 0 and output and 'saas' not in output:
                versions.append((addon_path.split('/')[-1],
                                 output.rstrip('\n')))
        vinfo = exp_version()
        git_vinfo = "<br/>".join(': '.join(item) for item in versions)
        vinfo['git_version_info'] = git_vinfo
        return vinfo
