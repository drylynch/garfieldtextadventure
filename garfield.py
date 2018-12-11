# why am i doing this

"""
TODO

maybe do
* make in pygame ?

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
        return "[{_id}] {_name}".format(**self.__dict__)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name


class Room:
    """ a room, with some loose junk, and some ghosts of junk that need to be filled """

    def __init__(self, room_id, room_name, loose_junk, ghost_junk, doors, my_key, rewards_key, has_savebox,
                 savebox_capacity):
        """
        :param int room_id: unique room id
        :param str room_name: readable name for display
        :param list loose_junk: junk ids, items to be sucked up
        :param list ghost_junk: junk ids, items to be put back
        :param list doors: room ids, adjacent rooms
        :param Room or None my_key: require this Room to be complete to unlock, or always unlocked (None)
        :param bool rewards_key: true if room rewards a key upon completion
        :param bool has_savebox: true if room has a savebox
        :param int savebox_capacity: max items for this rooms savebox (irrelevant if room has no savebox)
        """
        self._id = room_id
        self._name = room_name
        self._loose_junk = ChunkyTrunk(loose_junk, ALLJUNKS)
        self._ghost_junk = ChunkyTrunk(ghost_junk, ALLJUNKS)
        self._doors = doors
        self._my_key = my_key
        self._rewards_key = rewards_key
        self._has_savebox = has_savebox
        if has_savebox:
            self._savebox = SimpleTrunk(savebox_capacity)
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
        """
            must be called after /all/ rooms created
            converts doors from a list of room ids to dict with items (room_id: Room obj)
            converts room's key from room_id to Room obj with that id
        """
        self._doors = {room_id: ALLROOMS[room_id] for room_id in self._doors}
        if self._my_key:  # just for rooms that have keys
            self._my_key = ALLROOMS[self._my_key]

    def unlocked(self):
        """ true if room is unlocked, duh """
        if self._my_key is None:  # no key needed
            return True
        return self._my_key.needs_complete()  # doors are unlocked when their keygivers are complete

    def place_in_room(self, junk):
        """ add an item to the room in it's ghostly place """
        self._ghost_junk.remove(junk)

    def still_needs(self, junk):
        """ true if room still needs junk """
        return self._ghost_junk.contains(junk)

    def get_needs(self, junk_id):
        """ return ghost junk with given id, None if not found """
        return self._ghost_junk.get(junk_id)

    def all_junk_needs(self):
        """ return list of all items a room still needs """
        return self._ghost_junk.contents()

    def needs_complete(self):
        """ return true if no more ghost items (room is complete) """
        return self._ghost_junk.is_empty()

    def take_from_room(self, junk):
        """ remove a loose item from the room """
        self._loose_junk.remove(junk)

    def has_loose(self, junk):
        """ true if room has junk lying around """
        return self._loose_junk.contains(junk)

    def all_junk_loose(self):
        """ return all items a room has lying around """
        return self._loose_junk.contents()

    def get_loose(self, junk_id):
        """ return loose junk with given id, None if not found """
        return self._loose_junk.get(junk_id)

    def loose_complete(self):
        """ true if no more loose objects """
        return self._loose_junk.is_empty()

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

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

    def __init__(self, player_name, starting_room, vaccuum_capacity):
        """
        :param str player_name: cool name
        :param Room starting_room: room the player begins in
        :param int vaccuum_capacity: how much stuff the player can hold at once
        """
        self._name = player_name
        self._location = starting_room
        self._vaccuum = SimpleTrunk(vaccuum_capacity)

    def __str__(self):
        return self._name

    def vaccuum_full(self):
        """ true if vaccuum is at capacity """
        return self._vaccuum.is_full()

    def vaccuum_empty(self):
        """ true if vaccuum is empty """
        return self._vaccuum.is_empty()

    def vaccuum_contains(self, junk):
        """ true if vaccuum contains junk """
        return self._vaccuum.contains(junk)

    def vaccuum_contents(self):
        """ return list of junk in vaccuum """
        return self._vaccuum.contents()

    def vaccuum_get(self, junk_id):
        """ get junk obj with junk_id from vaccuum, None if not found """
        return self._vaccuum.get(junk_id)

    def move(self, room):
        """ moves the player's current location to given Room """
        self._location = room

    def suck(self, junk):
        """ suck up an item from the current room to vaccuum """
        self._location.take_from_room(junk)  # take from room
        self._vaccuum.insert(junk)  # give to vaccuum

    def blow(self, junk):
        """ blow an item from vaccuum to the current room """
        self._vaccuum.remove(junk)  # take from vaccuum
        self._location.place_in_room(junk)  # give to room

    def drop(self, junk):
        """ drop an item in the savebox of the current room """
        self._vaccuum.remove(junk)  # take from vaccuum
        self._location.savebox.insert(junk)  # give to savebox

    def grab(self, junk):
        """ grab an item out of the savebox in the current room """
        self._location.savebox.remove(junk)  # take from savebox
        self._vaccuum.insert(junk)  # give to vaccuum

    @property
    def location(self):
        return self._location


class _BaseTrunk:
    """
        dict-based item container to map an object to its corresponding id, eg (obj.id: obj)
        requires object to have id attribute to be used as key
    """

    def __init__(self):
        self._contents = {}

    def get(self, obj_id):
        """ return obj with the given id, or None if not found """
        return self._contents.get(obj_id, None)

    def contents(self):
        """ return list of objs """
        return self._contents.values()

    def contains(self, obj):
        """ return true if contains obj """
        return obj.id in self._contents

    def remove(self, obj):
        """ yank something out """
        del self._contents[obj.id]

    def is_empty(self):
        return self.length() == 0

    def length(self):
        return len(self._contents)


class SimpleTrunk(_BaseTrunk):
    """
        small, limited, user-interactable Trunk
        holds only junk objects
        can insert and remove items
        used for player vaccuum and saveboxes
    """

    def __init__(self, capacity):
        """
        :param int capacity: max number of items that can be held by this trunk
        """
        super().__init__()
        self._capacity = capacity

    def is_full(self):
        """ true if at capacity """
        return self.length() == self._capacity

    def insert(self, junk):
        """ plop something in """
        self._contents[junk.id] = junk


class ChunkyTrunk(_BaseTrunk):
    """
        large, unlimited, pre-filled Trunk
        holds both junk and room objects
        can only remove items
        used to reflect room state and doors
    """

    def __init__(self, contents_keys, contents_map):
        """
        :param list contents_keys: keys to map onto values
        :param dict contents_map: map of (key: value) to use for lookup
        """
        super().__init__()
        self._contents = {key: contents_map[key] for key in contents_keys}


def prompt_input_both():
    """
        ask user for input and return (action, choice) if they're valid:

        action  |  str, len 1      |  eg 'm'
        choice  |  int, len 1+     |  eg '13'
        both    |  str+int, len2+  |  eg 'm13'

        only returns just action or both, not just choice (that's what prompt_input_choice() is for)
        missing choice is replaced with None
        return (None, None) on completely invalid input

    """
    s = input(INPUT_PROMPT).strip()
    if s:
        if not is_int(s):  # make sure it's not just choice
            if len(s) == 1:
                return s, None  # is just action
            else:
                first = s[0]  # should be action
                second = s[1:]  # should be choice
                if not is_int(first) and is_int(second):
                    return first, int(second)  # is both

    return None, None


def prompt_input_choice(question):
    """ like prompt_input_both() but just gets a choice, asks a question, and loops until the user gives a valid answer """
    if question:  # just print once
        print(question + ' (back: [{0}])'.format(INPUT_QUIT_CHAR))  # let user know they can back out
    while True:
        s = input(INPUT_PROMPT).strip()
        if s:
            if s == INPUT_QUIT_CHAR:
                return INPUT_QUIT_CHAR  # return quit char so game loop knows to go back
            elif is_int(s):
                return int(s)


def prompt_continue(message=None):
    """
        customisable continue prompt
        given no message, will print default msg
        given a message, will print that followed by the default msg
    """
    default = '[enter] continue... '
    if message is None:
        input(default)
    else:
        input(INPUT_PROMPT + message + '\n' + default)


def is_int(s):
    """ true if int, false otherwise """
    try:
        int(s)
        return True
    except ValueError:
        return False


def game_is_finished():
    """ return true if all rooms are complete, else false """
    for room in ALLROOMS.values():
        if not room.needs_complete():  # any room is incomplete, not done
            return False
    return True  # all rooms complete, game is finished


def get_clearcmd():
    """ returns the command to clear the screen on the current os """
    if platform.system() == 'Windows':
        return 'cls'
    return 'clear'


def init():
    """ start her up boys """
    savebox_cap = 20
    RoomData = collections.namedtuple('RoomData', ['name', 'loose_junk', 'ghost_junk',
                                                   'doors', 'my_key', 'rewards_key',
                                                   'has_savebox', 'savebox_capacity'])
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
    rooms = {1: RoomData(name='Living Room',
                         loose_junk=[110, 130, 136, 140, 160, 186],  # list of int junk ids
                         ghost_junk=[126, 127, 133, 150, 160, 170, 178],  # list of int junk ids
                         doors=[2, 5],  # list of int room ids
                         my_key=None,  # int room id, or None
                         rewards_key=True,
                         # just to show notification to player that they got a key when they complete this room
                         has_savebox=False,
                         savebox_capacity=None),
             2: RoomData(name='Kitchen',
                         loose_junk=[120, 123, 133, 135, 149, 153, 168, 184, 192],
                         ghost_junk=[106, 120, 125, 131, 136, 140, 144, 145, 157, 167, 175, 183],
                         doors=[1, 4, 3, 9],
                         my_key=None,
                         rewards_key=False,
                         has_savebox=False,
                         savebox_capacity=None),
             3: RoomData(name='Downstairs Hallway',
                         loose_junk=[141, 148, 178, 182],
                         ghost_junk=[122, 168, 172, 182],
                         doors=[5, 2, 12, 6],
                         my_key=None,
                         rewards_key=False,
                         has_savebox=True,
                         savebox_capacity=savebox_cap),
             4: RoomData(name='Utility Room',
                         loose_junk=[112, 113, 159, 172],
                         ghost_junk=[102, 110, 112, 113, 148],
                         doors=[12, 2, 11],
                         my_key=None,
                         rewards_key=True,
                         has_savebox=False,
                         savebox_capacity=None),
             5: RoomData(name='Den',
                         loose_junk=[102, 115, 138, 146, 185],
                         ghost_junk=[115, 123, 129, 130, 138, 192],
                         doors=[1, 3],
                         my_key=None,
                         rewards_key=True,
                         has_savebox=False,
                         savebox_capacity=None),
             6: RoomData(name='Upstairs Landing',
                         loose_junk=[117, 129, 187, 191],
                         ghost_junk=[117, 146, 154, 189],
                         doors=[12, 3, 7, 8, 10, 14, 13],
                         my_key=None,
                         rewards_key=True,
                         has_savebox=False,
                         savebox_capacity=None),
             7: RoomData(name='Master Bedroom',
                         loose_junk=[108, 114, 122, 126, 143, 170, 176],
                         ghost_junk=[101, 114, 143, 159, 179, 181, 187],
                         doors=[6],
                         my_key=5,
                         rewards_key=True,
                         has_savebox=False,
                         savebox_capacity=None),
             8: RoomData(name='Small Bedroom',
                         loose_junk=[127, 145, 150, 151, 154, 188],
                         ghost_junk=[108, 141, 149, 153, 162, 176],
                         doors=[6],
                         my_key=4,
                         rewards_key=True,
                         has_savebox=False,
                         savebox_capacity=None),
             9: RoomData(name='Basement',
                         loose_junk=[101, 106, 121, 161, 162, 166, 180, 189],
                         ghost_junk=[100, 103, 137, 171, 188, 193],
                         doors=[2],
                         my_key=1,
                         rewards_key=True,
                         has_savebox=True,
                         savebox_capacity=savebox_cap),
             10: RoomData(name='Games Room',
                          loose_junk=[107, 137, 144, 156, 179, 181],
                          ghost_junk=[121, 128, 151, 161, 163, 186, 190, 191],
                          doors=[6],
                          my_key=6,
                          rewards_key=True,
                          has_savebox=True,
                          savebox_capacity=savebox_cap),
             11: RoomData(name='Garage',
                          loose_junk=[128, 132, 142, 169, 171, 183],
                          ghost_junk=[116, 118, 156, 164, 165, 166, 177],
                          doors=[4],
                          my_key=7,
                          rewards_key=True,
                          has_savebox=False,
                          savebox_capacity=None),
             12: RoomData(name='Gardens',
                          loose_junk=[100, 103, 111, 116, 124, 131, 139, 157, 163, 165, 174, 175, 190, 193],
                          ghost_junk=[107, 132, 135, 142, 147, 152, 155, 158],
                          doors=[3, 4, 15, 6],
                          my_key=8,
                          rewards_key=False,
                          has_savebox=False,
                          savebox_capacity=None),
             13: RoomData(name='Bathroom',
                          loose_junk=[109, 118, 119, 147, 152, 167],
                          ghost_junk=[105, 124, 134, 173, 174, 184, 185],
                          doors=[6],
                          my_key=9,
                          rewards_key=False,
                          has_savebox=False,
                          savebox_capacity=None),
             14: RoomData(name='Attic',
                          loose_junk=[105, 125, 134, 155, 158, 164, 177],
                          ghost_junk=[104, 109, 119, 139, 169, 180],
                          doors=[6],
                          my_key=10,
                          rewards_key=False,
                          has_savebox=False,
                          savebox_capacity=None),
             15: RoomData(name='Greenhouse',
                          loose_junk=[104, 173],
                          ghost_junk=[111],
                          doors=[12],
                          my_key=11,
                          rewards_key=False,
                          has_savebox=False,
                          savebox_capacity=None)}
    # fill the big dicts of junks and rooms
    for (jid, name) in junk.items():  # each = (junk_id, name)
        ALLJUNKS[jid] = Junk(jid, name)
    for (rid, r) in rooms.items():  # each = (room_id, rdata(name, loose_junk, ghost_junk, doors, key, has_seedbox))
        ALLROOMS[rid] = Room(rid, r.name, r.loose_junk, r.ghost_junk, r.doors, r.my_key, r.rewards_key, r.has_savebox,
                             r.savebox_capacity)
    for room in ALLROOMS.values():  # swap lists of room ids for lists of room objects, after all rooms are created
        room.create_obj_references()


# constants accessed by functions above, can't be in init() or main()
INPUT_PROMPT = '>>> '
INPUT_QUIT_CHAR = 'x'
ALLJUNKS = {}
ALLROOMS = {}


# ----------------------------------------


def main():
    init()
    clearcmd = get_clearcmd()
    player = Player('garfield', ALLROOMS[1], 3)  # start room 1

    # tutorial time
    print("""
 THE YEAR IS 2004.
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

     or, all at once
     >>> s69   ->   suck up item 69
     >>> m13   ->   move to room 13

 not many rooms are open to start with.
 some rooms may reward keys when they're completed...

 god speed.
""")
    prompt_continue()

    while not game_is_finished():  # game loop

        thisroom = player.location  # for convenience
        room_has_savebox = thisroom.has_savebox  # instead of calling 3 times
        nicelinelen = 20 + len(thisroom.name)
        os.system(clearcmd)

        # description of room and player state
        # gross but concise
        print('=' * nicelinelen)
        print('| you are in the {0}'.format(thisroom.name), end='')
        print('\n| connected rooms: ', end='')
        print(*thisroom.doors.values(), sep=', ')
        print('-' * nicelinelen)
        print('| your vaccuum:    ', end='')
        if player.vaccuum_empty():
            print('- empty -')
        else:
            print(*player.vaccuum_contents(), sep=', ')
        if room_has_savebox:
            print('|      savebox:    ', end='')
            if thisroom.savebox.is_empty():
                print('- empty -')
            else:
                print(*thisroom.savebox.contents(), sep=', ')
        print('-' * nicelinelen)
        print('| loose items:', end='\n|\t')
        print(*thisroom.all_junk_loose(), sep='\n|\t')
        print('| ghost items:', end='\n|\t')
        if thisroom.needs_complete():
            if thisroom.rewards_key:
                print('- room complete! you found a KEY! -')
            else:
                print('- room complete! -')
        else:
            print(*thisroom.all_junk_needs(), sep='\n|\t')
        print('-' * nicelinelen)

        # print actions
        print("you can:\n",
              "\t[m]ove to another room\n",
              "\t[s]uck up a loose item\n",
              "\t[b]low an item to it's correct place")
        if room_has_savebox:
            print("\t[d]rop something in the savebox\n",
                  "\t[g]rab something from the savebox")

        # get action and choice
        action, choice = prompt_input_both()
        if action is None:  # nothing entered
            continue  # pretend it didn't happen and ask again

        # move room
        elif action == 'm':
            if choice is None:  # get choice if user didn't give it already
                choice = prompt_input_choice('where do you want to go?')
                if choice == INPUT_QUIT_CHAR:  # quit, return to top of gameloop
                    continue
            room = thisroom.doors.get(choice, None)  # doors is still just a dict (for now)
            if room is not None:
                if room.unlocked():
                    player.move(room)
                else:
                    prompt_continue("LOCKED: you don't have the key for that room...")
            else:
                prompt_continue("NOPE: that rooms isn't connected to this one!")

        # suck up item
        elif action == 's':
            if player.vaccuum_full():  # too much succ
                prompt_continue('NOPE: you have no room for items! blow or drop what you have first.')
            elif thisroom.loose_complete():  # nothing to succ
                prompt_continue('NOPE: there are no items here to suck up! there must be some elsewhere...')
            else:
                if choice is None:
                    choice = prompt_input_choice('what item do you want to suck up?')
                    if choice == INPUT_QUIT_CHAR:
                        continue
                junk = thisroom.get_loose(choice)
                if junk is not None:
                    player.suck(junk)  # ;^)
                else:
                    prompt_continue("NOPE: that item isn't in the room!")

        elif action == 'b':
            if player.vaccuum_empty():  # nothing to blow
                prompt_continue('NOPE: you have no items! suck some up first.')
            elif thisroom.needs_complete():  # room doesn't need any items
                prompt_continue('NOPE: this room is complete! there must be other rooms that need items...')
            else:
                if choice is None:
                    choice = prompt_input_choice('what item do you want to blow down?')
                    if choice == INPUT_QUIT_CHAR:
                        continue
                junk = player.vaccuum_get(choice)
                if junk is not None:  # choice in vaccuum
                    if thisroom.still_needs(junk):  # choice has ghost in room
                        player.blow(junk)  # ;^))))
                    else:
                        prompt_continue("NOPE: this room doesn't need that item!")
                else:
                    prompt_continue("NOPE: you don't have that item!")

        elif room_has_savebox:

            if action == 'd':
                if player.vaccuum_empty():  # nothing to drop
                    prompt_continue('NOPE: you have no items! suck some up first.')
                elif thisroom.savebox.is_full():  # no room to drop
                    prompt_continue('NOPE: this savebox is full! grab some items from it first, or find another box.')
                else:
                    if choice is None:
                        choice = prompt_input_choice('what item do you want to drop into the savebox?')
                        if choice == INPUT_QUIT_CHAR:
                            continue
                    junk = player.vaccuum_get(choice)
                    if junk is not None:
                        player.drop(junk)  # :^( ?
                    else:
                        prompt_continue("NOPE: you don't have that item!")

            elif action == 'g':
                if player.vaccuum_full():  # no room for items
                    prompt_continue("NOPE: your vaccuum is full! drop some off first.")
                elif thisroom.savebox.is_empty():  # nothing to grab
                    prompt_continue("NOPE: this savebox is empty! drop some items in first.")
                else:
                    if choice is None:
                        choice = prompt_input_choice('what item do you want to grab from the savebox?')
                        if choice == INPUT_QUIT_CHAR:
                            continue
                    junk = thisroom.savebox.get(choice)
                    if junk is not None:
                        player.grab(junk)  # :o)
                    else:
                        prompt_continue("NOPE: that item isn't in this savebox!")

    # win
    os.system(clearcmd)
    print('\n\n\n\t\tcongratz {0}, u did it yahoo'.format(player))
    input('\n\n\t\tpress enter to exit')


if __name__ == '__main__':
    main()
