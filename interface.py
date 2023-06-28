# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from sqlalchemy import create_engine

from config import comunity_token, acces_token
from core import VkTools
from data_story import check_user, add_user


class BotInterface:

    def __init__(self, comm_token, acc_token, engine):
        self.vk_interface = vk_api.VkApi(token=comm_token)
        self.api = VkTools(acc_token)
        self.db_engine = engine
        self.params = None
        self.offset = 0

    def message_send(self, user_id, message, attachment=None):
        self.vk_interface.method(
            'messages.send', {
                'user_id': user_id,
                'message': message,
                'attachment': attachment,
                'random_id': get_random_id()})
        
    def event_handler(self):
        longpoll = VkLongPoll(self.vk_interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id,
                                      f'здравствуй {self.params["name"]}')
                elif command == 'поиск':
                    users_to_show = []
                    users = self.api.serch_users(self.params, self.offset)
                    for user in users:
                        if not check_user(engine=self.db_engine,
                                          user_id=user['id'],
                                          profile_id=event.user_id):
                            add_user(engine=self.db_engine,
                                     user_id=user['id'],
                                     profile_id=event.user_id)
                            users_to_show.append(user)

                    # проверить есть-ли пользователь
                    # в БД в соответствии с event.user_id

                    for user in users_to_show:
                        photos_user = self.api.get_photos(user['id'])
                    
                        attachment = ''
                        for num, photo in enumerate(photos_user):
                            attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
                            if num == 2:
                                break

                        self.message_send(
                            event.user_id,
                            f'Встречайте '
                            f'{user["name"]} ссылка: vk.com/{user["id"]}',
                            attachment=attachment)
                    self.offset += 10
                    # добавить анкеты в БД в соответствии с event.user_id
                 
                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token, engine=create_engine())
    bot.event_handler()