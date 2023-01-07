#! /usr/bin/python

# Simpele klasse die een dictionary omzet in een object
# met dank aan joelmccun, https://joelmccune.com/python-dictionary-as-object/
# werkt als een tierelier ;-)
class DictObj:
    def __init__(self, in_dict: dict):
        assert isinstance(in_dict, dict)
        for key, val in in_dict.items():
            if isinstance(val, (list, tuple)):
                setattr(self, key, [DictObj(x) if isinstance(
                    x, dict) else x for x in val])
            else:
                setattr(self, key, DictObj(val)
                        if isinstance(val, dict) else val)


# De data die normalieter terug komt via een database aanroep
# data = {'data': dict([('registerUser', {'ok': True, 'user': {'username': 'flint', 'email': 'flint@nu.nl',
#                      'password': 'pbkdf2:sha256:260000$LsiBhjBveWL1LdIQ$913d4141990c2450aaf9b74ce4f1da5b4284e27d16f79b5ede19cdec4846d32b'}})])}

# # We zetten de data om tot een dictionary die weekunnen gebruiken
# result = data['data']['registerUser']

# #  en dan zetten we de data om in een object
# obj = DictObj(result)

# # zo kan je 'm direct als object gebruiken in je project
# print(f"{obj.ok} , {obj.user.username} {obj.user.email}")
