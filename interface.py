import re
import psycopg2

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id

from core import VkTools


ACCES_TOKEN = 'vk1.a.WZoRoxgGXUjr0aWkhJIziHcRqOLgi-nTnN2T81R0oyYE1sRtG_UHltFol5J88db9nOFmIdHdide6OwlbMO0R-DDVG7nXrGsvyzuuCoGDzNeHdQsA0Nbe1xHRCmWcDdlgWSSImtHNMg5-8d_8LPsRdc51AgRD25ki0KmrVIOJmpDMYjQgwKsfHqijIXA3H0-YxXgGzQfKnEw1z2n4uQPgAg'
COMUNITY_TOKEN = 'vk1.a.5O23LtK2LnITpayOpaa0fgK391Uta6jZY4yYPh-Z_BCE9RaRRQEa5cvKp0PxRp5GVVa8_E6C5geaCVa5XZCAZSwspSFBBgFn2TUAWlEy_Yi_6I3O_PL3BmHPqK8MxHB44ER_6EeSobhLStVR2yvlVa87FJvpSF4zkGpSZ1mjO31fIxjxryLg2RzeJwj750iBX6rdBIz-TXc0zmLAA7bC0A'
RESULT_USERS_PHOTO = {}


class BotInterface:

    def __init__(self, token, user, password):
        self.bot = vk_api.VkApi(token=token)
        self.user = user
        self.password = password

    def create_db(self):
        conn = psycopg2.connect(database='listdb', user=self.user, password=self.password)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS anketa(
                    id SERIAL PRIMARY KEY, 
                    my_id INT NOT NULL, 
                    ankets_id INT NOT NULL
                );
                """)
        return conn, cur

    def message_send(self, user_id, message, attachment=None):
        self.bot.method('messages.send',
                        {'user_id': user_id,
                         'message': message,
                         'random_id': get_random_id(),
                         'attachment': attachment,
                        }
                        )

    def append_result_users_photo(self, event_user_id, params_search):
        tools = VkTools(ACCES_TOKEN)
        conn, cur = self.create_db()
        city_id, age_from, age_to, sex, relation = params_search.split(',')
        city_id = int(city_id)
        age_from = int(age_from)
        age_to = int(age_to)
        sex = int(sex)
        relation = int(relation)
        profiles = tools.user_serch(city_id, age_from, age_to, sex, relation)
        for profil in profiles:
            photo_the_user = []
            profile_info = tools.get_profile_info(profil['id'])
            if 'city' in profile_info[0]:
                if profile_info[0]['city']['id'] == city_id:
                    user_id = profile_info[0]['id']
                    cur.execute("SELECT * FROM anketa WHERE ankets_id = %s;", (user_id, ))
                    if not cur.fetchall():
                        cur.execute("INSERT INTO anketa (my_id, ankets_id) VALUES (%s, %s)", (event_user_id, user_id, ))                    
                        photos = tools.photos_get(user_id)
                        if photos:
                            for photo in photos:
                                media = f"?z=photo{photo['owner_id']}_{photo['id']}"
                                photo_the_user.append(media)
            if photo_the_user:
                RESULT_USERS_PHOTO[profil['id']] = photo_the_user
        conn.commit()
        cur.close()
        conn.close()
        self.message_send(event_user_id, 'Список фотографий собран. Для просмотра скажите "далее"')

    def handler(self):
        longpull = VkLongPoll(self.bot)
        for event in longpull.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                event_text = event.text.lower()
                match = re.match(r'поиск \d{1,3}\,\d{1,3}\,\d{1,3}\,[1|2]\,[0|1]', event_text)
                if event_text == 'привет':
                    self.message_send(event.user_id, 'Добрый день')
                    self.message_send(
                        event.user_id,
                        'Для нового поиска напишите "поиск" пробел и через запятую укажите параметры поиска: id города, возраст От, возраст До, пол(1 - женский, 2- мужской), семейное положение (0 - холост, 1 - в браке)'
                    )
                    self.message_send(event.user_id, 'Пример запроса:\nпоиск 99,20,40,2,1')
                elif match:
                    _, params_search = event_text.split(' ')
                    self.append_result_users_photo(event.user_id, params_search)
                elif event.text.lower() == 'далее':
                    if RESULT_USERS_PHOTO:
                        for id in RESULT_USERS_PHOTO.keys():
                            self.message_send(event.user_id, f'https://vk.com/{id}')
                            for photo_user in RESULT_USERS_PHOTO[id]:
                                self.message_send(event.user_id, f'https://vk.com/{id}{photo_user}')
                            RESULT_USERS_PHOTO.pop(id, None)
                            break
                    else:
                        self.message_send(event.user_id, 'Вы еще не запускали команду "поиск"')     
                else:
                    self.message_send(
                        event.user_id,
                        'Для нового поиска напишите "поиск" пробел и через запятую укажите параметры поиска: id города, возраст От, возраст До, пол(1 - женский, 2- мужской), семейное положение (0 - холост, 1 - в браке)'
                    )
                    self.message_send(event.user_id, 'Пример запроса:\nпоиск 99,20,40,2,1')
                    self.message_send(event.user_id, 'Для просмотра уже собранного списка скажите "далее"')

def source_users():
    bot = BotInterface(COMUNITY_TOKEN, 'postgres', 'Shcola219')
    bot.handler()

if __name__ == '__main__':
    source_users()
