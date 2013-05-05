# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import logging
from mediagoblin.tools import pluginapi
import os

_log = logging.getLogger(__name__)

PLUGIN_DIR = os.path.dirname(__file__)

def setup_plugin():

    _log.info('Setting up Dogma extra data...')

    routes = [
       ('mediagoblin.plugins.dogma.add_tracks',
        '/dogma/add_tracks',
        'mediagoblin.plugins.dogma.views:addTracks',
       ),
       ('mediagoblin.plugins.dogma.add_album',
        '/dogma/add_album',
        'mediagoblin.plugins.dogma.views:addAlbum',
       ),
       ('mediagoblin.plugins.dogma.add_band',
        '/dogma/add_band',
        'mediagoblin.plugins.dogma.views:addBand',
       ),
       ('mediagoblin.plugins.dogma.add_members',
        '/dogma/add_members',
        'mediagoblin.plugins.dogma.views:addMembers',
       ),
       ('mediagoblin.plugins.dogma.dashboard',
        '/dogma/dashboard',
        'mediagoblin.plugins.dogma.views:dashboard',
       ),
       ('mediagoblin.user_pages.user_collection',
        '/dogma/u/<string:user>/album/<string:collection>/',
        'mediagoblin.plugins.dogma.views:user_album')
       ]

    pluginapi.register_routes(routes)
    pluginapi.register_template_path(os.path.join(PLUGIN_DIR, 'templates'))

    pluginapi.register_template_hooks(
        {"extra_sideinfo": "dogma/display_extra_data.html"})

hooks = {
    'setup': setup_plugin
    }