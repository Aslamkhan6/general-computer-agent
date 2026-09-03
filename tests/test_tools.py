import os
import shutil
import unittest

from app.core.enums import ActionStatus
from app.tools.registry import ToolRegistry, register_all_default_tools
from app.tools.executor import ToolExecutor
from app.tools.request import ToolRequest


class TestToolEcosystem(unittest.TestCase):

    def setUp(self):
        self.registry = ToolRegistry()
        register_all_default_tools(self.registry)
        self.executor = ToolExecutor(self.registry)
        self.workspace = "./workspace/test_tools_env"
        os.makedirs(self.workspace, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.workspace):
            shutil.rmtree(self.workspace, ignore_errors=True)

    def test_tool_discovery(self):
        tools_list = self.registry.list_tools()
        # Verify 40 tools registered across 5 domains
        self.assertGreaterEqual(len(tools_list), 40)
        tool_names = [t["name"] for t in tools_list]
        self.assertIn("create_directory", tool_names)
        self.assertIn("read_file", tool_names)
        self.assertIn("execute_command", tool_names)
        self.assertIn("git_status", tool_names)
        self.assertIn("extract_text", tool_names)
        self.assertIn("open_application", tool_names)

        # Check metadata fields (Section 3.6 Tool Discovery)
        first_tool = tools_list[0]
        self.assertIn("name", first_tool)
        self.assertIn("description", first_tool)
        self.assertIn("risk_level", first_tool)
        self.assertIn("parameters", first_tool)

    def test_filesystem_tools(self):
        dir_path = os.path.join(self.workspace, "sub_dir")
        file_path = os.path.join(dir_path, "sample.txt")

        # 1. create_directory
        res = self.executor.execute(ToolRequest(tool_name="create_directory", arguments={"path": dir_path}))
        self.assertEqual(res.status, ActionStatus.SUCCESS)
        self.assertTrue(os.path.exists(dir_path))

        # 2. write_file
        res = self.executor.execute(ToolRequest(tool_name="write_file", arguments={"path": file_path, "content": "Hello World"}))
        self.assertEqual(res.status, ActionStatus.SUCCESS)

        # 3. read_file
        res = self.executor.execute(ToolRequest(tool_name="read_file", arguments={"path": file_path}))
        self.assertEqual(res.status, ActionStatus.SUCCESS)
        self.assertEqual(res.output["content"], "Hello World")

        # 4. get_metadata
        res = self.executor.execute(ToolRequest(tool_name="get_metadata", arguments={"path": file_path}))
        self.assertEqual(res.status, ActionStatus.SUCCESS)
        self.assertTrue(res.output["is_file"])

        # 5. list_directory
        res = self.executor.execute(ToolRequest(tool_name="list_directory", arguments={"path": dir_path}))
        self.assertEqual(res.status, ActionStatus.SUCCESS)
        self.assertEqual(len(res.output["items"]), 1)

    def test_terminal_tools(self):
        res = self.executor.execute(ToolRequest(tool_name="execute_command", arguments={"command": "echo Hello Terminal"}))
        self.assertEqual(res.status, ActionStatus.SUCCESS)
        self.assertEqual(res.output["stdout"], "Hello Terminal")

    def test_git_tools(self):
        repo_path = os.path.join(self.workspace, "git_repo")
        os.makedirs(repo_path, exist_ok=True)

        # git_init
        res = self.executor.execute(ToolRequest(tool_name="git_init", arguments={"cwd": repo_path}))
        self.assertEqual(res.status, ActionStatus.SUCCESS)

        # git_status
        res = self.executor.execute(ToolRequest(tool_name="git_status", arguments={"cwd": repo_path}))
        self.assertEqual(res.status, ActionStatus.SUCCESS)

    def test_browser_tools(self):
        # take_screenshot
        img_path = os.path.join(self.workspace, "test_shot.png")
        res = self.executor.execute(ToolRequest(tool_name="take_screenshot", arguments={"output_path": img_path}))
        self.assertEqual(res.status, ActionStatus.SUCCESS)
        self.assertTrue(os.path.exists(img_path))

    def test_application_tools(self):
        res = self.executor.execute(ToolRequest(tool_name="get_active_window", arguments={}))
        self.assertEqual(res.status, ActionStatus.SUCCESS)
        self.assertIn("active_window", res.output)


if __name__ == "__main__":
    unittest.main()
