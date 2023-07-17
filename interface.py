# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import comunity_token, acces_token
from core import VkTools
from data_story import (check_user, add_user,
                        get_not_shown_users,
                        update_user_as_shown,
                        number_of_not_shown_users)
from config import db_url_object

engine = create_engine(db_url_object, echo=True)


class BotInterface:

    def __init__(self, comm_token, acc_token, engine):
        self.vk_interface = vk_api.VkApi(token=comm_token)
        self.api = VkTools(acc_token)
        self.db_engine = engine
        self.params = {}
        self.offset = 0
        self.expecting_fields = {
            'bdate': 'день рождения',
            'home_town': 'город',
            'sex': 'пол'
        }

    def message_send(self, user_id, message, attachment=None):
        self.vk_interface.method(
            'messages.send', {
                'user_id': user_id,
                'message': message,
                'attachment': attachment,
                'random_id': get_random_id()})

    def check_if_all_fields_filled(self, user_id):
        for field_code, field_name in self.expecting_fields.items():
            if not self.params.get(field_code):
                self.message_send(
                    user_id,
                    f'Укажите {field_name} в формате {field_name}: <xxx>')

    def get_new_users(self, user_id):
        users = self.api.serch_users(self.params, self.offset)
        with Session(self.db_engine) as session:
            for user in users:
                if not check_user(session=session, user_id=user['id'], profile_id=user_id):
                    add_user(session=self.db_engine,
                             user_id=user['id'],
                             profile_id=user_id,
                             name=user['id'],
                             bdate=user['bdate'],
                             home_town=user['home_town'])
            session.commit()
            self.offset += 10

    def event_handler(self):
        longpoll = VkLongPoll(self.vk_interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command: str = event.text.lower()
                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id,
                                      f'здравствуй {self.params["name"]}')
                    self.check_if_all_fields_filled(user_id=event.user_id)

                elif command.startswith('город'):
                    self.params['home_town'] = command.split(':')[1]
                    self.check_if_all_fields_filled(user_id=event.user_id)

                elif command.startswith('день рождения'):
                    self.params['bdate'] = command.split(':')[1]
                    self.check_if_all_fields_filled(user_id=event.user_id)

                elif command.startswith('пол'):
                    self.params['sex'] = command.split(':')[1]
                    self.check_if_all_fields_filled(user_id=event.user_id)

                elif command == 'поиск':
                    with Session(self.db_engine) as session:
                        if number_of_not_shown_users(
                                session=session, user_id=event.user_id) == 0:
                            self.get_new_users(user_id=event.user_id)
                            session.commit()

                        user_to_show = get_not_shown_users(
                            session=session, user_id=event.user_id)

                        if not user_to_show:
                            self.message_send(
                                event.user_id,
                                'Не удалось найти пользователей. Попробуйте снова')
                        else:
                            photos_user = self.api.get_photos(user_to_show['id'])

                            attachment = ''
                            for num, photo in enumerate(photos_user):
                                attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
                                if num == 2:
                                    break

                            self.message_send(
                                event.user_id,
                                f'Встречайте '
                                f'{user_to_show["name"]} ссылка: vk.com/{user_to_show["id"]}',
                                attachment=attachment)

                            update_user_as_shown(
                                session=session,
                                user_id=event.user_id,
                                profile_id=user_to_show["id"])

                            session.commit()

                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token, engine=create_engine())
    bot.event_handler()
