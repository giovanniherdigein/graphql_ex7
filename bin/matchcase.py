#! /usr/bin/python

name = 'help'
match name:
    case 'help':
        print('help')
    case _:
        print('No help given')
