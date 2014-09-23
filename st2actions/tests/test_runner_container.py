import datetime
import mock

from st2common.models.db.action import (ActionDB, ActionExecutionDB)
from st2common.models.api.action import RunnerTypeAPI
from st2common.models.api.actionrunner import LiveActionAPI
from st2common.persistence.action import (Action, ActionExecution, RunnerType)
from st2common.transport.publishers import PoolPublisher
from st2tests.base import DbTestCase

import tests.config as tests_config
tests_config.parse_args()

# XXX: There is dependency on config being setup before importing
# RunnerContainer. Do not move this until you fix config
# dependencies.
from st2actions.container.base import RunnerContainer


@mock.patch.object(PoolPublisher, 'publish', mock.MagicMock())
class RunnerContainerTest(DbTestCase):
    action_db = None
    runnertype_db = None

    @classmethod
    def setUpClass(cls):
        super(DbTestCase, cls).setUpClass()
        RunnerContainerTest._setup_test_models()

    def test_get_runner_module(self):
        runnertype_db = RunnerContainerTest.runnertype_db
        runner_container = RunnerContainer()
        runner = runner_container._get_runner(runnertype_db)
        self.assertTrue(runner is not None, 'TestRunner must be valid.')

    def test_dispatch(self):
        runner_container = RunnerContainer()
        params = {
            'actionstr': 'bar'
        }
        actionexec_db = self._get_action_exec_db_model(params)
        actionexec_db = ActionExecution.add_or_update(actionexec_db)
        # Assert that execution ran successfully.
        self.assertTrue(runner_container.dispatch(actionexec_db))
        actionexec_db = ActionExecution.get_by_id(actionexec_db.id)
        result = actionexec_db.result
        self.assertTrue(result.get('action_params').get('actionint') == 10)
        self.assertTrue(result.get('action_params').get('actionstr') == 'bar')

    def test_dispatch_override_default_action_params(self):
        runner_container = RunnerContainer()
        params = {
            'actionstr': 'foo',
            'actionint': 20
        }
        actionexec_db = self._get_action_exec_db_model(params)
        actionexec_db = ActionExecution.add_or_update(actionexec_db)

        # Assert that execution ran successfully.
        self.assertTrue(runner_container.dispatch(actionexec_db))
        actionexec_db = ActionExecution.get_by_id(actionexec_db.id)
        result = actionexec_db.result
        self.assertTrue(result.get('action_params').get('actionint') == 20)
        self.assertTrue(result.get('action_params').get('actionstr') == 'foo')

    def _get_action_exec_db_model(self, params):
        actionexec_db = ActionExecutionDB()
        actionexec_db.status = 'initializing'
        actionexec_db.start_timestamp = datetime.datetime.now()
        actionexec_db.action = {'name': RunnerContainerTest.action_db.name}
        actionexec_db.parameters = params
        return actionexec_db

    def _get_live_action_db_model(self, actionexec_id):
        liveactionapi = LiveActionAPI(**{'actionexecution_id': actionexec_id})
        liveaction_db = LiveActionAPI.to_model(liveactionapi)
        return liveaction_db

    @classmethod
    def _setup_test_models(cls):
        RunnerContainerTest.setup_runner()
        RunnerContainerTest.setup_action_models()

    @classmethod
    def setup_runner(cls):
        test_runner = {
            'name': 'test-runner',
            'description': 'A test runner.',
            'enabled': True,
            'runner_parameters': {
                'runnerstr': {
                    'description': 'Foo str param.',
                    'type': 'string',
                    'default': 'defaultfoo'
                },
                'runnerint': {
                    'description': 'Foo int param.',
                    'type': 'number'
                }
            },
            'runner_module': 'tests.test_runner'
        }
        runnertype_api = RunnerTypeAPI(**test_runner)
        RunnerContainerTest.runnertype_db = RunnerType.add_or_update(
            RunnerTypeAPI.to_model(runnertype_api))

    @classmethod
    def setup_action_models(cls):
        action_db = ActionDB()
        action_db.name = 'action-1'
        action_db.description = 'awesomeness'
        action_db.enabled = True
        action_db.content_pack = 'wolfpack'
        action_db.entry_point = ''
        action_db.runner_type = {'name': 'test-runner'}
        action_db.parameters = {
            'actionstr': {'type': 'string'},
            'actionint': {'type': 'number', 'default': 10},
        }
        action_db.required_parameters = ['actionstr']
        RunnerContainerTest.action_db = Action.add_or_update(action_db)