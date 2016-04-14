# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pecan import expose

__all__ = [
    'BaseRootController'
]


class BaseRootController(object):
    logger = None
    controllers = None
    default_controller = None

    @expose()
    def _lookup(self, *remainder):
        version = ''
        if len(remainder) > 0:
            version = remainder[0]

            if remainder[len(remainder) - 1] == '':
                # If the url has a trailing '/' remainder will contain an empty string.
                # In order for further pecan routing to work this method needs to remove
                # the empty string from end of the tuple.
                remainder = remainder[:len(remainder) - 1]
        versioned_controller = self.controllers.get(version, None)
        if versioned_controller:
            return versioned_controller, remainder[1:]
        self.logger.debug('No version specified in URL. Will use default controller.')
        return self.default_controller, remainder
