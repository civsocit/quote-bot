import typing

from aiogram.contrib.fsm_storage.memory import BaseStorage


class DynamoStorage(BaseStorage):
    """
    DynamoBD wrapper for Aiogram Storage
    """

    _table_name = "AiogramFSMTable"

    async def close(self):
        pass

    async def wait_closed(self):
        pass

    def _create_table(self):
        table = self._database.create_table(
            TableName=self._table_name,
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "chat_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "N"},
                {"AttributeName": "chat_id", "AttributeType": "N"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Wait until the table exists.
        self._table.meta.client.get_waiter("table_exists").wait(TableName=self._table_name)
        return table

    def __init__(self, database):
        """
        DynamoDB storage
        :param database: boto3.resource object
        """
        self._database = database

        tables = self._database.meta.client.list_tables()["TableNames"]
        if self._table_name not in tables:
            self._table = self._create_table()
        else:
            self._table = self._database.Table(self._table_name)

    async def _get_item(self, chat_id: int, user_id: int) -> typing.Optional[typing.Dict]:
        item = self._table.get_item(Key={"user_id": user_id, "chat_id": chat_id})
        return item.get("Item", None)

    async def get_state(
        self,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        default: typing.Optional[str] = None
    ) -> typing.Optional[str]:
        chat, user = self.check_address(chat=chat, user=user)
        item = await self._get_item(int(chat), int(user))
        if not item:
            return default
        return item.get("FSMState", default)

    async def set_state(
        self,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        state: typing.Optional[typing.AnyStr] = None
    ):
        chat, user = self.check_address(chat=chat, user=user)
        self._table.update_item(
            Key={"user_id": int(user), "chat_id": int(chat)},
            UpdateExpression="SET FSMData = :val1",
            ExpressionAttributeValues={":val1": state},
        )

    async def get_data(
        self,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        default: typing.Optional[str] = None
    ) -> typing.Dict:
        chat, user = self.check_address(chat=chat, user=user)
        item = await self._get_item(int(chat), int(user))
        if not item:
            return dict()
        return item.get("FSMData", dict())

    async def set_data(
        self,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        data: typing.Dict = None
    ):
        chat, user = self.check_address(chat=chat, user=user)
        self._table.update_item(
            Key={"user_id": int(user), "chat_id": int(chat)},
            UpdateExpression="SET FSMData = :val1",
            ExpressionAttributeValues={":val1": data},
        )

    async def update_data(
        self,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        data: typing.Dict = None,
        **kwargs
    ):
        r_data = await self.get_data(chat=chat, user=user)
        w_data = r_data.update(data) if r_data else data
        await self.set_data(chat=chat, user=user, data=w_data)

    async def get_bucket(
        self,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        default: typing.Optional[dict] = None
    ) -> typing.Dict:
        return dict()

    async def set_bucket(
        self,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        bucket: typing.Dict = None
    ):
        pass

    async def update_bucket(
        self,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        bucket: typing.Dict = None,
        **kwargs
    ):
        pass

    def has_bucket(self):
        return False
