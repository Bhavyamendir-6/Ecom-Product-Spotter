class FakeToolContext:
    """Mimics google.adk.tools.ToolContext for direct tool invocation.

    The existing tools only access tool_context.state as a dict,
    so this minimal adapter is sufficient.
    """

    def __init__(self, initial_state: dict | None = None):
        self.state: dict = initial_state or {}
