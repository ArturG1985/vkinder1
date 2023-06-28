from datetime import datetime
import vk_api
from config import acces_token
from pprint import pprint


class VkTools:
    def __init__(self, acc_token):
        self.api = vk_api.VkApi(token=acc_token)

    def get_profile_info(self, user_id):
        info, = self.api.method('users.get', 
                            {'user_id': user_id,
                             'fields': 'city,bdate,sex,relation,home_town'})
        user_info = {'name': info['first_name'] + ' ' + info['last_name'],
                     'id':  info['id'],
                     'bdate': info.get('bdate'),
                     'home_town': info['home_town'],
                     'sex': info['sex'],
                     'city': info['city']['id']}
        return user_info
    
    def serch_users(self, params, offset, count=10):
        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        curent_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = curent_year - user_year
        age_from = age - 3
        age_to = age + 3

        users = self.api.method('users.search',
                                {'count': count,
                                 'offset': offset,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'city': city,
                                 'status': 6,
                                 'is_closed': False})

        res = []
        for user in users['items']:
            if not user['is_closed']:
                res.append({'id': user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']})
        return res

    def get_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1})
        res = []
        for photo in photos['items']:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count']})
        res.sort(key=lambda x: x['likes']+x['comments']*10, reverse=True)
        return res[:3]


if __name__ == '__main__':
    bot = VkTools(acces_token)
    params = bot.get_profile_info(788316919)
    users = bot.serch_users(params, 10)
    user = users.pop()
    photos = bot.get_photos(user['id'])
    pprint(photos)
