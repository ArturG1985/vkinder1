import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from sqlalchemy import create_engine
from config import comunity_token, acces_token
from core import VkTools
from data_story import BdTools


class BotInterface:

    def __init__(self, comunity_token, acces_token, engine):
        self.vk_interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.longpoll = VkLongPoll(self.vk_interface)
        self.bd_tools = BdTools(engine)       
        self.check_user = BdTools(engine) 
        self.params = {}
        self.users = []
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
                    if not self.params['city']:
                        self.event_city_input(event.user_id)
                    elif not self.params['sex']:
                        self.event_sex_input(event.user_id)
                    elif not self.params['year']:
                        self.event_year_input(event.user_id)

                elif command == 'поиск':
                    users = self.api.serch_users(self.params, self.offset)
                    user = users.pop()
                    
                    while self.bd_tools.check_user(event.user_id, user["id"]) is True: 
                        user = users.pop() 

                    if self.bd_tools.check_user(event.user_id, user["id"]) is False:
                        self.bd_tools.add_user(event.user_id, user["id"])   
               
                    photos_user = self.api.get_photos(user['id'])                  
                    attachment = ''
                    for num, photo in enumerate(photos_user):
                        attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
                        if num == 2:
                            break
                    self.offset += 10
                    
                    self.message_send(event.user_id,
                                      f'Встречайте {user["name"]} ссылка: vk.com/{user["id"]}',
                                      attachment=attachment) 
                 
                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')

    def event_city_input(self, user_id):
        self.message_send(user_id, 'Введите название вашего города проживания')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self.params['city'] = event.text.title()
                break
        if self.params['city']:
            self.message_send(user_id, 'ОК')
        
    def event_sex_input(self, user_id):
        self.message_send(user_id, 'Введите ваш пол м - мужской, ж - женский')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self.params['sex'] = 2 if event.text == 'м' else 1
                break
        if self.params['sex']:
            self.message_send(user_id, 'ОК')

    def event_year_input(self, user_id):
        self.message_send(user_id, 'Введите ваш возраст')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self.params['year'] = event.text
                break
        if self.params['year']:
            self.message_send(user_id, 'ОК')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token, engine=create_engine())
    bot.event_handler()