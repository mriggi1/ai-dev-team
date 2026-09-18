"""Exercise tool boundaries and the developer loop without a running LLM."""

import tempfile
import subprocess
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

from ollama import Message

from ai_dev_team.agents.developer import DeveloperAgent
from ai_dev_team.tools.workspace import GeneratedWorkspace


def call(name, **arguments):
    return Message(role='assistant', tool_calls=[
        {'function': {'name': name, 'arguments': arguments}}])


class DeveloperToolsTests(unittest.TestCase):
    def test_failed_write_blocks_completion_with_valid_old_file(self):
        with tempfile.TemporaryDirectory() as directory:
            provider = Mock()
            provider.chat.side_effect = [
                call('write_file', path='app.py'),
                Message(role='assistant', content='Finished'),
            ]
            agent = DeveloperAgent(provider, Path(directory), max_iterations=2)
            agent.workspace.write_file('app.py', 'value = 1\n')
            with redirect_stdout(StringIO()), self.assertRaises(RuntimeError):
                agent.run('Revise app.py')
            self.assertEqual(agent.workspace.read_file('app.py'), 'value = 1\n')
            feedback = provider.chat.call_args.args[0][-1]['content']
            self.assertIn('pending_writes', feedback)
            self.assertIn('content', feedback)

    def test_successful_retry_resolves_pending_write(self):
        with tempfile.TemporaryDirectory() as directory:
            provider = Mock()
            provider.chat.side_effect = [
                call('write_file', path='app.py'),
                Message(role='assistant', content='Finished'),
                call('write_file', path='app.py', content='value = 2\n'),
                Message(role='assistant', content='Finished'),
            ]
            agent = DeveloperAgent(provider, Path(directory), max_iterations=4)
            agent.workspace.write_file('app.py', 'value = 1\n')
            with redirect_stdout(StringIO()):
                result = agent.run('Revise app.py')
            self.assertIn('value = 2', result)
            self.assertEqual(provider.chat.call_count, 4)

    def test_other_file_write_does_not_resolve_pending_write(self):
        with tempfile.TemporaryDirectory() as directory:
            provider = Mock()
            provider.chat.side_effect = [
                call('write_file', path='app.py'),
                call('write_file', path='other.py', content='value = 2\n'),
                Message(role='assistant', content='Finished'),
            ]
            agent = DeveloperAgent(provider, Path(directory), max_iterations=3)
            agent.workspace.write_file('app.py', 'value = 1\n')
            with redirect_stdout(StringIO()), self.assertRaises(RuntimeError):
                agent.run('Revise app.py')
            self.assertIn('app.py', provider.chat.call_args.args[0][-1]['content'])

    def test_static_analysis_detects_errors_without_modifying_source(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = GeneratedWorkspace(Path(directory))
            code = ('counter = 1\ndef create():\n    counter += 1  # noqa: F823\n'
                    'def identify():\n    return uuid.uuid4()\n')
            workspace.write_file('app.py', code)
            self.assertTrue(workspace.check_syntax()['ok'])
            result = workspace.check_static_analysis()
            self.assertFalse(result['ok'])
            self.assertEqual({issue['rule'] for issue in result['issues']}, {'F821', 'F823'})
            self.assertEqual(workspace.read_file('app.py'), code)
            workspace.write_file('app.py', 'import uuid\nraise RuntimeError("not executed")\n')
            self.assertTrue(workspace.check_static_analysis()['ok'])

    def test_static_analysis_failures_do_not_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = GeneratedWorkspace(Path(directory))
            self.assertFalse(workspace.check_static_analysis()['ok'])
            workspace.write_file('app.py', 'x = 1\n')
            for failure in (OSError('missing executable'), subprocess.TimeoutExpired('ruff', 30)):
                with patch('ai_dev_team.tools.workspace.subprocess.run', side_effect=failure):
                    result = workspace.check_static_analysis()
                    self.assertFalse(result['ok'])
                    self.assertTrue(result['errors'])
            for status, output in ((2, ''), (0, 'not json')):
                response = Mock(returncode=status, stdout=output, stderr='Ruff failed')
                with patch('ai_dev_team.tools.workspace.subprocess.run', return_value=response):
                    self.assertFalse(workspace.check_static_analysis()['ok'])

    def test_final_gate_requires_static_fix_even_without_tool_request(self):
        with tempfile.TemporaryDirectory() as directory:
            provider = Mock()
            provider.chat.side_effect = [
                call('write_file', path='app.py', content='counter = 1\ndef f():\n    counter += 1\n'),
                Message(role='assistant', content='Done'),
                call('write_file', path='app.py', content='counter = 1\ndef f():\n    global counter\n    counter += 1\n'),
                Message(role='assistant', content='Done'),
            ]
            agent = DeveloperAgent(provider, Path(directory))
            with redirect_stdout(StringIO()):
                result = agent.run('Implement a counter')
            self.assertIn('global counter', result)
            self.assertEqual(provider.chat.call_count, 4)
            self.assertTrue(any('F823' in m.get('content', '')
                                for m in provider.chat.call_args.args[0] if isinstance(m, dict)))

    def test_paths_and_no_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = GeneratedWorkspace(Path(directory) / 'generated')
            for path in ('../outside.py', str(Path(directory) / 'outside.py'), 'data.txt'):
                with self.assertRaises(ValueError):
                    workspace.write_file(path, 'x = 1')
            workspace.write_file('app.py', 'raise RuntimeError("must not execute")')
            self.assertTrue(workspace.check_syntax()['ok'])
            workspace.write_file('app.py', 'def broken(:')
            self.assertFalse(workspace.check_syntax()['ok'])

    def test_corrects_reported_syntax_error(self):
        with tempfile.TemporaryDirectory() as directory:
            provider = Mock()
            provider.chat.side_effect = [
                call('write_file', path='app.py', content='def f():\n    x = next_id\n    global next_id\n'),
                call('check_syntax'),
                call('write_file', path='app.py', content='next_id = 1\ndef f():\n    global next_id\n    next_id += 1\n'),
                call('check_syntax'),
                Message(role='assistant', content='Done'),
            ]
            agent = DeveloperAgent(provider, Path(directory))
            with redirect_stdout(StringIO()):
                source = agent.run('Implement the plan')
            self.assertIn('global next_id', source)
            self.assertTrue(agent.workspace.check_syntax()['ok'])
            messages = provider.chat.call_args.args[0]
            self.assertTrue(any('prior to global declaration' in m.get('content', '')
                                for m in messages if isinstance(m, dict)))
            # A subsequent revision operates on the same files.
            provider.chat.side_effect = [call('read_file', path='app.py'),
                                         Message(role='assistant', content='No changes')]
            with redirect_stdout(StringIO()):
                self.assertEqual(agent.run('Review requires no changes'), source)

    def test_empty_completion_is_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            provider = Mock()
            provider.chat.return_value = Message(role='assistant', content='Done')
            agent = DeveloperAgent(provider, Path(directory), max_iterations=2)
            with redirect_stdout(StringIO()), self.assertRaises(RuntimeError):
                agent.run('Create an application')
            self.assertEqual(provider.chat.call_count, 2)

    def test_unknown_tool_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            provider = Mock()
            provider.chat.return_value = call('run_shell', command='anything')
            agent = DeveloperAgent(provider, Path(directory), max_iterations=1)
            with redirect_stdout(StringIO()), self.assertRaises(RuntimeError):
                agent.run('Create an application')
            self.assertIn('Unknown tool', provider.chat.call_args.args[0][-1]['content'])


if __name__ == '__main__':
    unittest.main()
