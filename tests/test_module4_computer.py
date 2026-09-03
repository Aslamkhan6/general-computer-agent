import os
import shutil
import unittest

from app.computer import (
    ScreenManager,
    MouseController,
    KeyboardController,
    WindowManager,
    AccessibilityInspector,
    BrowserGUIController,
    VisionGroundingEngine,
    ComputerController,
)
from app.core.enums import ActionStatus
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry, register_all_default_tools
from app.tools.request import ToolRequest


class TestModule4Computer(unittest.TestCase):

    def setUp(self):
        self.computer = ComputerController()
        self.registry = ToolRegistry()
        register_all_default_tools(self.registry)
        self.executor = ToolExecutor(self.registry)

    def test_screen_manager(self):
        dims = self.computer.screen.get_screen_dimensions()
        self.assertIn("width", dims)
        self.assertIn("height", dims)

        shot_path = self.computer.screen.capture_screenshot("./workspace/test_m4_shot.png")
        self.assertTrue(os.path.exists(shot_path))
        if os.path.exists(shot_path):
            os.remove(shot_path)

    def test_mouse_and_keyboard(self):
        m_res = self.computer.mouse.move(100, 100)
        self.assertTrue(m_res["success"])

        c_res = self.computer.mouse.click(100, 100)
        self.assertTrue(c_res["success"])

        k_res = self.computer.keyboard.type_text("Hello Agent")
        self.assertTrue(k_res["success"])

    def test_windows_manager(self):
        windows = self.computer.windows.enumerate_windows()
        self.assertIsInstance(windows, list)

    def test_accessibility_inspector(self):
        tree = self.computer.accessibility.inspect_ui_tree(max_depth=2)
        self.assertIn("children", tree)

        found = self.computer.accessibility.find_elements(name="Button")
        self.assertIsInstance(found, list)

    def test_browser_gui_controller(self):
        loc = self.computer.browser.locate_element("#submit-btn")
        self.assertTrue(loc["found"])

        type_res = self.computer.browser.type_into_element("#search-input", "Query text")
        self.assertTrue(type_res["success"])

    def test_vision_grounding_engine(self):
        grounded = self.computer.vision.ground_element("Submit button")
        self.assertIsNotNone(grounded)
        self.assertTrue("submit button" in grounded.label.lower())

        v_res = self.computer.vision.execute_visual_click("Submit button")
        self.assertTrue(v_res["success"])


    def test_unified_computer_controller(self):
        state = self.computer.get_state()
        self.assertIn("screen", state)

        res = self.computer.execute_gui_action("click", x=200, y=200)
        self.assertTrue(res["success"])

    def test_gui_tools_in_registry(self):
        tools = [t["name"] for t in self.registry.list_tools()]
        self.assertIn("screen_capture", tools)
        self.assertIn("mouse_click", tools)
        self.assertIn("keyboard_type", tools)
        self.assertIn("window_action", tools)
        self.assertIn("inspect_ui_tree", tools)
        self.assertIn("visual_grounding_click", tools)

        res = self.executor.execute(ToolRequest(tool_name="screen_capture", arguments={"output_path": "./workspace/shot_tool.png"}))
        self.assertEqual(res.status, ActionStatus.SUCCESS)
        if os.path.exists("./workspace/shot_tool.png"):
            os.remove("./workspace/shot_tool.png")


if __name__ == "__main__":
    unittest.main()
