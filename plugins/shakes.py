#!/usr/bin/python
from random import choice

phrases = """It is certain
It is decidedly so
Without a doubt
Yes - definitely
You may rely on it
As I see it, yes
Most likely
Outlook good
Signs point to yes
Yes
Reply hazy, try again
Ask again later
Better not tell you now
Cannot predict now
Concentrate and ask again
Don't count on it
My reply is no
My sources say no
Outlook not so good
Very doubtful""".split('\n')

def eightball():
    return choice( phrases )

def main( data ):
    if '8' in data and 'ball' in data:
        return eightball()

if __name__ == '__main__':
    print eightball()

