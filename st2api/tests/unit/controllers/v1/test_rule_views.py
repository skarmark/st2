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

import six

from st2common.models.system.common import ResourceReference
from st2tests.fixturesloader import FixturesLoader
from tests import FunctionalTest

http_client = six.moves.http_client

TEST_FIXTURES = {
    'runners': ['testrunner1.yaml'],
    'actions': ['action1.yaml', 'action2.yaml'],
    'triggers': ['trigger1.yaml'],
    'triggertypes': ['triggertype1.yaml']
}

TEST_FIXTURES_RULES = {
    'rules': ['rule1.yaml', 'rule4.yaml', 'rule5.yaml']
}

FIXTURES_PACK = 'generic'


class TestRuleViewController(FunctionalTest):

    fixtures_loader = FixturesLoader()

    @classmethod
    def setUpClass(cls):
        super(TestRuleViewController, cls).setUpClass()
        models = TestRuleViewController.fixtures_loader.save_fixtures_to_db(
            fixtures_pack=FIXTURES_PACK, fixtures_dict=TEST_FIXTURES)
        TestRuleViewController.ACTION_1 = models['actions']['action1.yaml']
        TestRuleViewController.TRIGGER_TYPE_1 = models['triggertypes']['triggertype1.yaml']

        file_name = 'rule1.yaml'
        rules = TestRuleViewController.fixtures_loader.save_fixtures_to_db(
            fixtures_pack=FIXTURES_PACK, fixtures_dict=TEST_FIXTURES_RULES)['rules']
        TestRuleViewController.RULE_1 = rules[file_name]

    def test_get_all(self):
        resp = self.app.get('/v1/rules/views')
        self.assertEqual(resp.status_int, http_client.OK)
        self.assertEqual(len(resp.json), 3)

    def test_get_one_by_id(self):
        rule_id = str(TestRuleViewController.RULE_1.id)
        get_resp = self.__do_get_one(rule_id)
        self.assertEqual(get_resp.status_int, http_client.OK)
        self.assertEqual(self.__get_rule_id(get_resp), rule_id)
        self.assertEqual(get_resp.json['action']['description'],
                         TestRuleViewController.ACTION_1.description)
        self.assertEqual(get_resp.json['trigger']['description'],
                         TestRuleViewController.TRIGGER_TYPE_1.description)

    def test_get_one_by_ref(self):
        rule_name = TestRuleViewController.RULE_1.name
        rule_pack = TestRuleViewController.RULE_1.pack
        ref = ResourceReference.to_string_reference(name=rule_name, pack=rule_pack)
        get_resp = self.__do_get_one(ref)
        self.assertEqual(get_resp.json['name'], rule_name)
        self.assertEqual(get_resp.status_int, http_client.OK)

    def test_get_one_fail(self):
        resp = self.app.get('/v1/rules/1', expect_errors=True)
        self.assertEqual(resp.status_int, http_client.NOT_FOUND)

    @staticmethod
    def __get_rule_id(resp):
        return resp.json['id']

    def __do_get_one(self, rule_id):
        return self.app.get('/v1/rules/views/%s' % rule_id, expect_errors=True)
