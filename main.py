from app.tools.filesystem import CreateDirectoryTool
from app.tools.registry import ToolRegistry


def main():
    registry = ToolRegistry()

    registry.register(CreateDirectoryTool())

    print("Available tools:")
    for tool in registry.list_tools():
        print(f"- {tool['name']}: {tool['description']}")

    tool = registry.get("create_directory")

    result = tool.execute(
        path="./workspace/test-project"
    )

    print("\nTool result:")
    print(result)


if __name__ == "__main__":
    main()