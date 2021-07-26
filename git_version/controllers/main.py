# Copyright (C) 2021-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import subprocess

import odoo.addons.web.controllers.main as main
from odoo import http
from odoo.service.common import exp_version
import odoo.tools as tools


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
            output = str(proc.communicate()[0].decode("utf-8"))
            # Check if it is a git repo and hide standard saas repos
            if proc.returncode == 0 and output and 'saas' not in output:
                versions.append((addon_path.split('/')[-1],
                                 output.rstrip('\n')))
        vinfo = exp_version()
        git_vinfo = "<br/>".join(': '.join(item) for item in versions)
        vinfo['git_version_info'] = git_vinfo
        return vinfo
