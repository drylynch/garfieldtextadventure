# why am i doing this

"""
TODO

look into reduce code for getting user input bit - change ordering (may not be viable but could work idk)
add ability to just type action + number to do something (eg 'm5' to move to room 5)
        - reflect that in tutorial

"""

import os
import platform
import collections

"""
text based clone of garfield, released pc and ps2, 2004 by hip games

garfield has to clean the house up cause odie fucked it or something

move garfield around the house with his trusty vaccuum cleaner and put items back where they belong
can suck up stray items and blow them back to their rightful place, or store them in save boxes for later
max of 3 items in the vaccuum at any one time, max of 20 items in each save box
"""


# ----------------------------------------


class Junk:
    """ an item that sits in a room, to be sucked up or blown """
    def __init__(self, junk_id, junk_name):
        """
        :param int junk_id: unique junk id
        :param str junk_name: readable name for display
        """
        self._id = junk_id  # int
        self._name = junk_name  # str

    def __str__(self):  # main reason why junk is a class: can just print each object and get a nice string
        return "[{0}] {1}".format(self._id, self._name)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name


class Room:
    """ a room, with some loose junk, and some ghosts of junk that need to be filled """
    def __init__(self, room_id, room_name, loose_junk, ghost_junk, doors, my_key, rewards_key, has_savebox):
        """
        :param int room_id: unique room id
        :param str room_name: readable name for display
        :param list loose_junk: junk ids, items to be sucked up
        :param list ghost_junk: junk ids, items to be put back
        :param list doors: room ids, adjacent rooms
        :param Room or None my_key: require this Room to be complete to unlock, or always unlocked (None)
        :param bool rewards_key: true if rewards a key upon completion
        :param bool has_savebox: if the room has a savebox
        """
        self._id = room_id
        self._name = room_name
        self._loose_junk = [ALLJUNKS[junk_id] for junk_id in loose_junk]  # swap junk ids with their corresponding Junk objs
        self._ghost_junk = [ALLJUNKS[junk_id] for junk_id in ghost_junk]
        self._doors = doors
        self._my_key = my_key
        self._rewards_key = rewards_key
        self._has_savebox = has_savebox
        if has_savebox:
            self._savebox = _SaveBox()
        else:
            self._savebox = None

    def __str__(self):
        if self.unlocked():
            string_id = self._id
            string_name = self._name
        else:  # locked doors are mysteries
            string_id = '?'
            string_name = 'LOCKED'
        return "[{0}] {1}".format(string_id, string_name)

    def create_obj_references(self):
        """ must be called after /all/ rooms created, converts key & doorlist items from int to Room objs """
        self._doors = [ALLROOMS[room_id] for room_id in self._doors]
        if self._my_key:  # just for rooms that have keys
            self._my_key = ALLROOMS[self._my_key]

    def unlocked(self):
        """ true if room is unlocked, duh """
        if self._my_key is None:  # no key needed
            return True
        return self._my_key.ghosts_complete()  # doors are unlocked when their keygivers are complete

    def place_in_room(self, j):
        """ add an item to the room in it's ghostly place """
        self._ghost_junk.remove(j)

    def take_from_room(self, j):
        """ remove a loose item from the room """
        self._loose_junk.remove(j)

    def ghosts_complete(self):
        """ return true if room is complete (all ghosts filled) """
        return len(self._ghost_junk) == 0

    def loose_complete(self):
        """ true if no more loose objects """
        return len(self._loose_junk) == 0

    def cheat(self):
        """ >:( """
        if self._has_savebox:
            self._savebox = []
        self._loose_junk = []
        self._ghost_junk = []

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def loose_junk(self):
        return self._loose_junk

    @property
    def ghost_junk(self):
        return self._ghost_junk

    @property
    def doors(self):
        return self._doors

    @property
    def rewards_key(self):
        return self._rewards_key

    @property
    def has_savebox(self):
        return self._has_savebox

    @property
    def savebox(self):
        return self._savebox


class Player:
    """ you! """
    def __init__(self, player_name, starting_room):
        self._name = player_name  # str
        self._location = starting_room  # Room obj
        self._vaccuum = []  # list of junk_ids

    def __str__(self):
        return self._name

    def vaccuum_full(self):
        """ true if vaccuum is at capacity """
        return len(self._vaccuum) == VACCUUM_CAP

    def vaccuum_empty(self):
        """ true if vaccuum is empty """
        return len(self._vaccuum) == 0

    def move(self, new_room):
        """ moves the player's current location """
        for doorway in self._location.doors:
            if doorway == new_room:
                self._location = new_room
                return

    def suck(self, j):
        """ suck up an item from the current room to vaccuum """
        if not self.vaccuum_full():
            self._location.take_from_room(j)  # take from room
            self._vaccuum.append(j)  # give to vaccuum

    def blow(self, j):
        """ blow an item from vaccuum to the current room """
        if j in self._vaccuum:
            self._vaccuum.remove(j)  # take from vaccuum
            self._location.place_in_room(j)  # give to room

    def drop(self, j):
        """ drop an item in the savebox of the current room """
        if j in self._vaccuum and self._location.has_savebox and not self._location.savebox.is_full():
            self._vaccuum.remove(j)  # take from vaccuum
            self._location.savebox.store(j)  # give to savebox

    def grab(self, j):
        """ grab an item out of the savebox in the current room """
        if self._location.has_savebox and j in self._location.savebox:
            self._location.savebox.remove(j)  # take from savebox
            self._vaccuum.append(j)  # give to vaccuum

    def cheat(self):
        """ >:( """
        self._vaccuum = []
        self._name = 'big cheater boy'  # >:)

    @property
    def location(self):
        return self._location

    @property
    def vaccuum(self):
        return self._vaccuum


class _SaveBox:
    """ a savebox that can hold some items for later """
    def __init__(self):
        """ basically just a list """
        self._contents = []

    def __iter__(self):
        yield from self._contents

    def store(self, j):
        if not self.is_full():
            self._contents.append(j)

    def remove(self, j):
        if j in self._contents:
            self._contents.remove(j)

    def is_empty(self):
        return len(self._contents) == 0

    def is_full(self):
        return len(self._contents) == SAVEBOX_CAP


def prompt_input():
    """ returns all the necessary info from user input """
    s = input('>>> ')
    if not s:  # gave nothing
        return None
    elif is_int(s):  # gave an int, return whole thing
        return int(s)
    return s[0].lower()  # gave a string, return just first char


def prompt_continue():
    """ simple continue prompt """
    input('press enter to continue...')


def game_is_finished():
    """ return true if all rooms are complete, else false """
    for room in ALLROOMS.values():
        if not room.ghosts_complete():  # any room is incomplete, not done
            return False
    return True  # all rooms complete, done


def cheat_game(cheater):
    """ all of the glory, none of the sport """
    for room in ALLROOMS.values():
        room.cheat()
    cheater.cheat()


def is_int(s):
    """ return true if int, false otherwise """
    try:
        int(s)
        return True
    except ValueError:
        return False


def get_clearcmd():
    """ returns the command to clear the screen on the current os """
    if platform.system() == 'Windows':
        return 'cls'
    return 'clear'


def init():
    """ start her up boys """
    RData = collections.namedtuple('RData', ['name', 'loose_junk', 'ghost_junk', 'doors', 'my_key', 'rewards_key', 'has_savebox'])
    junk = {100: '10kg Weight',  # id: name
            101: 'Alarm Clock',
            102: 'Animal Bed',
            103: 'Barbell',
            104: 'Baseball',
            105: 'Bathroom Scales',
            106: 'Beef',
            107: 'Birdhouse',
            108: 'Bongo',
            109: 'Boomerang',
            110: 'Boots',
            111: 'Box of Apples',
            112: 'Box of Detergent',
            113: 'Bucket',
            114: 'Bunny Slipper',
            115: 'Bunny Trophy',
            116: 'Buzzsaw',
            117: 'Candlebra',
            118: 'Car Jack',
            119: "Catcher's Mitt",
            120: 'Cheese',
            121: 'Chess Board',
            122: 'Clock',
            123: 'Computer Screen',
            124: 'Conditioner',
            125: 'Cookie Jar',
            126: 'Cushion',
            127: 'DVD Player',
            128: 'Dart',
            129: 'Desk Lamp',
            130: 'Disco Trophy',
            131: 'Egg Basket',
            132: 'Fertilizer',
            133: 'Fish Bowl',
            134: 'Fish Decoration',
            135: 'Flowerpot',
            136: 'Fruit Bowl',
            137: 'Fuse',
            138: 'Globe',
            139: 'Gramophone',
            140: 'Green Plate',
            141: 'Guitar',
            142: 'Hose Nozzle',
            143: 'Hot Water Bottle',
            144: 'Jar of Peppers',
            145: 'Kitchen Scales',
            146: 'Lamp',
            147: 'Large Pumpkin',
            148: 'Laundry Basket',
            149: 'Lei',
            150: 'Magazine Rack',
            151: 'Magic 8-Ball',
            152: 'Mailbox',
            153: 'Maraca',
            154: 'Neck Vase',
            155: "Odie's Bowl",
            156: 'Oil Can',
            157: 'Pasta Sauce',
            158: 'Patio Light',
            159: 'Phone',
            160: 'Photo of Garfield',
            161: 'Piggy Bank',
            162: 'Pinata',
            163: 'Pool Cue',
            164: 'Power Drill',
            165: 'Power Sander',
            166: 'RC Car',
            167: 'Radio',
            168: 'Red Book',
            169: 'Red Hat',
            170: 'Remote',
            171: 'Roller Blade',
            172: 'Round Picture Frame',
            173: 'Rubber Duck',
            174: 'Shampoo',
            175: 'Sheet Pasta',
            176: 'Sombrero',
            177: 'Spare Tire',
            178: 'Speaker',
            179: 'Stereo',
            180: 'Stretch the Chicken',
            181: 'Tie',
            182: 'Tissue Box',
            183: 'Toaster',
            184: 'Toilet Brush',
            185: 'Towel',
            186: 'Toy Car',
            187: 'Trash Bin',
            188: 'Trumpet',
            189: 'Vase',
            190: 'Video Game',
            191: 'Vinyl Record',
            192: 'Waste Paper Basket',
            193: 'Water Valve'}
    rooms = {1: RData(name='Living Room',
                      loose_junk=[110, 130, 136, 140, 160, 186],  # list of int junk ids
                      ghost_junk=[126, 127, 133, 150, 160, 170, 178],  # list of int junk ids
                      doors=[2, 5],  # list of int room ids
                      my_key=None,  # int room id, or None
                      rewards_key=True,
                      has_savebox=False),
             2: RData(name='Kitchen',
                      loose_junk=[120, 123, 133, 135, 149, 153, 168, 184, 192],
                      ghost_junk=[106, 120, 125, 131, 136, 140, 144, 145, 157, 167, 175, 183],
                      doors=[1, 4, 3, 9],
                      my_key=None,
                      rewards_key=False,
                      has_savebox=False),
             3: RData(name='Downstairs Hallway',
                      loose_junk=[141, 148, 178, 182],
                      ghost_junk=[122, 168, 172, 182],
                      doors=[5, 2, 12, 6],
                      my_key=None,
                      rewards_key=False,
                      has_savebox=True),
             4: RData(name='Utility Room',
                      loose_junk=[112, 113, 159, 172],
                      ghost_junk=[102, 110, 112, 113, 148],
                      doors=[12, 2, 11],
                      my_key=None,
                      rewards_key=True,
                      has_savebox=False),
             5: RData(name='Den',
                      loose_junk=[102, 115, 138, 146, 185],
                      ghost_junk=[115, 123, 129, 130, 138, 192],
                      doors=[1, 3],
                      my_key=None,
                      rewards_key=True,
                      has_savebox=False),
             6: RData(name='Upstairs Landing',
                      loose_junk=[117, 129, 187, 191],
                      ghost_junk=[117, 146, 154, 189],
                      doors=[12, 3, 7, 8, 10, 14, 12],
                      my_key=None,
                      rewards_key=True,
                      has_savebox=False),
             7: RData(name='Master Bedroom',
                      loose_junk=[108, 114, 122, 126, 143, 170, 176],
                      ghost_junk=[101, 114, 143, 159, 179, 181, 187],
                      doors=[6],
                      my_key=5,
                      rewards_key=True,
                      has_savebox=False),
             8: RData(name='Small Bedroom',
                      loose_junk=[127, 145, 150, 151, 154, 188],
                      ghost_junk=[108, 141, 149, 153, 162, 176],
                      doors=[6],
                      my_key=4,
                      rewards_key=True,
                      has_savebox=False),
             9: RData(name='Basement',
                      loose_junk=[101, 106, 121, 161, 162, 166, 180, 189],
                      ghost_junk=[100, 103, 137, 171, 188, 193],
                      doors=[2],
                      my_key=1,
                      rewards_key=True,
                      has_savebox=True),
             10: RData(name='Games Room',
                       loose_junk=[107, 137, 144, 156, 179, 181],
                       ghost_junk=[121, 128, 151, 161, 163, 186, 190, 191],
                       doors=[6],
                       my_key=6,
                       rewards_key=True,
                       has_savebox=True),
             11: RData(name='Garage',
                       loose_junk=[128, 132, 142, 169, 171, 183],
                       ghost_junk=[116, 118, 156, 164, 165, 166, 177],
                       doors=[4],
                       my_key=7,
                       rewards_key=True,
                       has_savebox=False),
             12: RData(name='Gardens',
                       loose_junk=[100, 103, 111, 116, 124, 131, 139, 157, 163, 165, 174, 175, 190, 193],
                       ghost_junk=[107, 132, 135, 142, 147, 152, 155, 158],
                       doors=[3, 4, 15, 6],
                       my_key=8,
                       rewards_key=False,
                       has_savebox=False),
             13: RData(name='Bathroom',
                       loose_junk=[109, 118, 119, 147, 152, 167],
                       ghost_junk=[105, 124, 134, 173, 174, 184, 185],
                       doors=[6],
                       my_key=9,
                       rewards_key=False,
                       has_savebox=False),
             14: RData(name='Attic',
                       loose_junk=[105, 125, 134, 155, 158, 164, 177],
                       ghost_junk=[104, 109, 119, 139, 169, 180],
                       doors=[6],
                       my_key=10,
                       rewards_key=False,
                       has_savebox=False),
             15: RData(name='Greenhouse',
                       loose_junk=[104, 173],
                       ghost_junk=[111],
                       doors=[12],
                       my_key=11,
                       rewards_key=False,
                       has_savebox=False)}
    # fill the big dicts of junks and rooms
    for each in junk.items():  # j = (id, name)
        jid, name = each
        ALLJUNKS[jid] = Junk(jid, name)
    for each in rooms.items():  # room = (id, rdata(name, loose_junk, ghost_junk, doors, key, has_seedbox))
        rid, r = each
        ALLROOMS[rid] = Room(rid, r.name, r.loose_junk, r.ghost_junk, r.doors, r.my_key, r.rewards_key, r.has_savebox)
    for r in ALLROOMS:  # make sure the lists are full of objects, not ids
        ALLROOMS[r].create_obj_references()


SAVEBOX_CAP = 20
VACCUUM_CAP = 3
ALLJUNKS = {}
ALLROOMS = {}


# ----------------------------------------


def main():
    init()
    clearcmd = get_clearcmd()
    player = Player('garfield', ALLROOMS[1])  # start in room 1

    # tutorial time
    print("""the year is 2004.
you are garfield.
you gotta clean the house.

use your vaccuum cleaner to move items around.
suck up loose items, and blow them into their proper place (their 'ghost').

you can only hold 3 items at a time.
you can store items in saveboxes for later, though.

select choices by typing commands in the square brackets.
eg:
    to [m]ove, type
    >>> m
    
    to [s]uck up this item: [69] Cool Shades
    >>> s
    >>> 69
    
not many rooms are open to start with.
some rooms may reward keys when they're completed...

god speed.
""")
    prompt_continue()

    while True:  # game loop
        if game_is_finished():
            os.system(clearcmd)
            break

        thisroom = player.location
        room_has_savebox = thisroom.has_savebox
        nicelinelen = 20 + len(thisroom.name)
        os.system(clearcmd)

        # description of room and player state
        print('=' * nicelinelen)
        print('| you are in the {0}'.format(thisroom.name), end='')
        print('\n| connected rooms: ', end='')
        print(*thisroom.doors, sep=', ')
        print('-' * nicelinelen)
        print('| your vaccuum:    ', end='')
        if player.vaccuum_empty():
            print('- empty -')
        else:
            print(*player.vaccuum, sep=', ')
        if room_has_savebox:
            print('|      savebox:    ', end='')
            if thisroom.savebox.is_empty():
                print('- empty -')
            else:
                print(*thisroom.savebox, sep=', ')
        print('-' * nicelinelen)
        print('| loose items:', end='\n|\t')
        print(*thisroom.loose_junk, sep='\n|\t')
        print('| ghost items:', end='\n|\t')
        if thisroom.ghosts_complete():
            print('- room is complete! -', end='')
            if thisroom.rewards_key:
                print('\n|\t - you found a key! -', end='')
            print()
        else:
            print(*thisroom.ghost_junk, sep='\n|\t')
        print('-' * nicelinelen)

        # print actions
        print("you can:\n",
              "\t[m]ove to another room\n",
              "\t[s]uck up a loose item\n",
              "\t[b]low an item to it's correct place")
        if room_has_savebox:
            print("\t[d]rop something in the savebox\n",
                  "\t[g]rab something from the savebox")

        # get action
        action = prompt_input()
        if not action:  # nothing entered
            continue  # pretend it didn't happen and ask again

        # for babies
        elif action == 69800813569:
            cheat_game(player)

        # move room
        elif action == 'm':
            match = False
            print('where do you want to go? (back: [x])')
            while not match:  # loop until user picks a valid room
                user_choice = prompt_input()
                if user_choice is None:  # nothing entered
                    continue
                if user_choice == 'x':  # bye
                    break
                for otherroom in thisroom.doors:
                    if user_choice == otherroom.id:  # only go to rooms that are connected
                        if otherroom.unlocked():
                            player.move(otherroom)
                        else:
                            print("LOCKED: you don't have the key for that room...")
                            prompt_continue()
                        match = True
                        break

        # suck up item
        elif action == 's':
            if player.vaccuum_full():  # no room to succ :(
                print('\n\nyou have no room for items! place or store what you have first.')
                prompt_continue()
                continue
            elif thisroom.loose_complete():  # no items left to suck
                print('\n\nthere are no items here to suck up! there must be some elsewhere...')
                prompt_continue()
                continue
            else:  # room to succ :)
                match = False
                print('what item do you wanna suck? (back: [x])')
                while not match:  # loop til user picks something
                    user_choice = prompt_input()
                    if user_choice is None:  # nothing entered
                        continue
                    if user_choice == 'x':  # bye
                        break
                    for looseitem in thisroom.loose_junk:
                        if user_choice == looseitem.id:
                            player.suck(looseitem)  # only suck item if it's in the room
                            match = True
                            break

        # blow item
        elif action == 'b':
            if player.vaccuum_empty():  # no items to blow
                print('\n\nyou have no items! suck some up first.')
                prompt_continue()
                continue
            elif thisroom.ghosts_complete():  # nothing left in the room to fill
                print('\n\nthis room is complete! your items must belong somewhere else...')
                prompt_continue()
                continue
            else:  # blow some items
                match = False
                print('what item do you want to blow? (back: [x])')
                while not match:  # wait till user picks something
                    user_choice = prompt_input()
                    if user_choice is None:  # nothing entered
                        continue
                    if user_choice == 'x':  # bye
                        break
                    for vaccuumitem in player.vaccuum:
                        if user_choice == vaccuumitem.id and vaccuumitem in thisroom.ghost_junk:  # choice is in vaccuum and ghost in room
                            player.blow(vaccuumitem)
                            match = True
                            break

        elif room_has_savebox:

            # drop item in savebox
            if action == 'd':
                if player.vaccuum_empty():  # no items to blow
                    print('\n\nyou have no items! suck some up first.')
                    prompt_continue()
                    continue
                elif thisroom.savebox.is_full():  # no room left to drop
                    print('\n\nthis savebox is full! remove some items, or find another box.')
                    prompt_continue()
                    continue
                else:
                    match = False
                    print('what item do you want to drop in the savebox? (back: [x])')
                    while not match:
                        user_choice = prompt_input()
                        if user_choice is None:
                            continue
                        if user_choice == 'x':
                            break
                        for vaccuumitem in player.vaccuum:
                            if user_choice == vaccuumitem.id:
                                player.drop(vaccuumitem)
                                match = True
                                break

            # grab item from savebox
            elif action == 'g':
                if player.vaccuum_full():  # can only swap
                    print('\n\nyour vaccuum is full! drop some items first.')
                    prompt_continue()
                    continue
                elif thisroom.savebox.is_empty():  # nothing to grab
                    print("\n\nthere's nothing in here! drop some items first.")
                    prompt_continue()
                    continue
                else:
                    match = False
                    print('what item do you want to grab from the savebox? (back: [x])')
                    while not match:
                        user_choice = prompt_input()
                        if user_choice is None:
                            continue
                        if user_choice == 'x':
                            break
                        for saveboxitem in thisroom.savebox:
                            if user_choice == saveboxitem.id:
                                player.grab(saveboxitem)
                                match = True
                                break

    # win
    print('\n\n\n\t\tcongratz {0}, u did it yahoo'.format(player))
    input('\n\n\t\tpress enter to exit')


if __name__ == '__main__':
    main()
