import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_group_name = f'game_{self.game_id}'

        # Присоединяемся к группе комнаты игры
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Покидаем группу комнаты игры
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Обработка полученных данных, например, ход игрока
        # Отправка обновлений об игровом состоянии другим игрокам
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_update',
                'data': data,
            }
        )

    async def game_update(self, event):
        data = event['data']
        # Отправка обновления состояния игры клиенту
        await self.send(text_data=json.dumps(data))