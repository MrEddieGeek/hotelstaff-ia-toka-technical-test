from __future__ import annotations


def build_mongo_client(uri: str, use_mock: bool):
    if use_mock:
        from mongomock_motor import AsyncMongoMockClient

        return AsyncMongoMockClient()
    from motor.motor_asyncio import AsyncIOMotorClient

    return AsyncIOMotorClient(uri)
