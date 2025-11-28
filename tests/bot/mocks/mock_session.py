class MockSession:
    async def execute(self, *_, **__):
        pass

    async def commit(self):
        pass
