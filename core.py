import vk_api
import vk_api.exceptions 
from vk_api.exceptions import ApiError 


ACCES_TOKEN = 'vk1.a.5VrWisNUJMbVTzYdNxYLL_xt2NmLw4y8Y1EiVc-q6Szq0Fn-iBXIp9TxVhSMhAPHSOCF1hRmT2nguimbHRXaYh98b5nEQga7k_v_juoRuqtk8LAkKwy_efUCZivuEhQPngTpi9-zwI6IE7vvdnDn6MuF0Cxi393K2DQfyndFEqGOuOZ-1xj-w51u1kY3KQp1l42BkPgv-VyzKOpxdrfMCA'


class VkTools():
    def __init__(self, token):
        self.ext_api = vk_api.VkApi(token=token)

    def get_profile_info(self, user_id):
        try:
            info = self.ext_api.method('users.get',
                                    {'user_id': user_id,
                                     'fields': 'bdate,city,sex,relation'
                                    }
                                     )
        except ApiError:
            return

        return info

    def photos_get(self, user_id):
        photos = self.ext_api.method('photos.get',
                                     {'album_id': 'profile',
                                      'owner_id': user_id,
                                      'extended': 1,
                                      }
                                     )
        try:
            photos = photos['items']
        except KeyError:
            return

        result = []
        photos = sorted(photos, key=lambda k: k['likes']['count']+k['comments']['count'], reverse=True)
        for num, photo in enumerate(photos):
            result.append({'owner_id': photo['owner_id'],
                           'id': photo['id'],
                           'likes': photo['likes']['count'],
                            'comments': photo['comments']['count'],
                           })
            if num == 2: 
                  break

        return result

    def user_serch(self, city_id: int, age_from: int, age_to: int, sex: int, relation: int, offset = None):
        try:
            profiles = self.ext_api.method('users.search',
                                       {'city_id': city_id,
                                        'age_from': age_from,
                                        'age_to': age_to,
                                        'sex': sex,
                                        'count': 30,
                                        'relation': relation,
                                        'offset': offset,
                                       }
                                      )
        except ApiError:
            return

        profiles = profiles['items']
        result = []
        for profile in profiles:
            if profile['is_closed'] == False:
                result.append({'name': profile['first_name'] + ' ' + profile['last_name'],
                               'id': profile['id']
                               })
      
        return result

def get_vk_ankets():
    tools = VkTools(ACCES_TOKEN)
    city_id = 99
    age_from = 20
    age_to = 40
    sex = 2
    relation = 1
    profiles = tools.user_serch(city_id, age_from, age_to, sex, relation)
    for profil in profiles:
        profile_info = tools.get_profile_info(profil['id'])
        if 'city' in profile_info[0]:
            if profile_info[0]['city']['id'] == city_id:
                photos = tools.photos_get(profile_info[0]['id'])
                print(photos)


if __name__ == '__main__':
    get_vk_ankets()
