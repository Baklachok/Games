import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from tic_tac_toe.models import Move


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_group_name = f'game_{self.game_id}'
        self.user_id = self.scope['query_string'].decode().split('=')[1]
        self.player = await self.get_user_from_id(self.user_id)

        # Join game group
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )

        await self.accept()

        # Notify other players about the new connection
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'player_join',
                'player_id': self.player.id
            }
        )


    async def disconnect(self, close_code):
        # Leave game group
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )

        # Notify other players about the disconnection
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'player_leave',
                'player_id': self.player.id
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        move_position = data.get('position')
        if move_position is not None:
            if 0 <= move_position < 9:
                # Асинхронно сохраняем ход в базу данных
                await self.save_move(move_position)
                # Отправляем сообщение о ходе всем игрокам в группе
                await self.channel_layer.group_send(
                    self.game_group_name,
                    {
                        'type': 'game_update',
                        'data': data,
                        'player_id': self.player.id
                    }
                )
            else:
                print('Invalid move position:', move_position)

    @sync_to_async
    def save_move(self, move_position):
        # Синхронная операция сохранения хода в базу данных
        Move.objects.create(game_id=self.game_id, player=self.player, position=move_position)

    async def player_join(self, event):
        # Handle player join event
        player_id = event['player_id']
        # Send appropriate message to the client
        await self.send(text_data=json.dumps({
            'type': 'player_join',
            'player_id': player_id
        }))

    async def player_leave(self, event):
        # Handle player leave event
        player_id = event['player_id']
        # Send appropriate message to the client
        await self.send(text_data=json.dumps({
            'type': 'player_leave',
            'player_id': player_id
        }))


    async def game_update(self, event):
        # Handle game update event
        data = event['data']
        player_id = event['player_id']
        # Send updated game state to the client
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            'data': data,
            'player_id': player_id
        }))

    async def get_user_from_id(self, user_id):
        try:
            user = await sync_to_async(User.objects.get)(pk=user_id)
            return user
        except User.DoesNotExist:
            return None

