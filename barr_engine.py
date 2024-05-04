import copy
import math
import os
from typing import List


class SolidCollision(Exception):
   """ Raised when a solid GameObj has the same Coord as another solid GameObj. """
   pass

class NotPhysical(Exception):
   """ Raised when a GameObj method is used and the GameObj is not physically initialized. """
   pass


class Room:
   """
   Room class represents a room within the game (Size, [Objects in room], String).
   """

   def __init__(self, init_size=(4, 4), init_floor=0, init_objects=[], init_string='No map initialized'):
       self.Size = init_size  # the size of the room (x, y)
       self.Floor = init_floor  # the floor the room is on may determine the enemy types and/or a collection of rooms
       self.Objects = init_objects  # list of all objects to be recognized as being in the room
       self.MapString = init_string  # a string representation of the room

   def __str__(self):
       return self.MapString

   def add_obj(self, new_obj):
       """ Add newObject to Objects. """
      
       if not new_obj._IsPhysical:
           raise NotPhysical("GameObj is not physical")
      
       if self.is_solid_at(new_obj.pos):
           raise SolidCollision("GameObj cannot be added to room @ position " + str(new_obj.pos))
      
       self.Objects.extend([new_obj])

   def is_obj_at(self, check_pos):
       """
       See if the checkPos is occupied by any GameObj.

       Return True if space is occupied by a GameObj, otherwise return False.
       """
      
       if (check_pos[0] > (self.Size[0] - 1) or check_pos[1] > (self.Size[1] - 1)
           or check_pos[0] < 0 or check_pos[1] < 0):
         raise ValueError("Coord is out of bounds")
      
       # iterate through all objects in room to see if there is an obj @ check_pos
       for i in self.Objects:
           if i.pos == check_pos:
               return True
       return False
  
   def is_solid_at(self, check_pos):
       """
       See if the checkPos is occupied by a solid object.

       Return True if space is occupied by a solid, otherwise return False.
       """
      
       if (check_pos[0] > (self.Size[0] - 1) or check_pos[1] > (self.Size[1] - 1)
           or check_pos[0] < 0 or check_pos[1] < 0):
         raise ValueError("Coord is out of bounds")
      
       # iterate through all objects in room to see if there is a solid @ check_pos
       # there may be more than one object with the same position
       for i in self.Objects:
           if i.pos == check_pos and i.IsSolid:
               return True
       return False

   def update_map_str(self):  # creates new string for room
       """ Update MapString attr with a string representation of the room and its objects. """

       new_map_str = ''
       str_at_pos = ''

       # iterate through every object for every point in the room
       for row in range(self.Size[1]):
           for col in range(self.Size[0]):
               # add the str for the object @ this position
               for i in self.Objects:
                   if (col, row) == i.pos:
                       str_at_pos = str(i) + ' '
                       if i.IsSolid:  # ensures that solids appear when on top of non-solids
                           break
               if str_at_pos == '':
                   str_at_pos = ". "
              
               new_map_str += str_at_pos
               str_at_pos = ''
           new_map_str += '\n'
      
       self.MapString = new_map_str


class GameObj:
   """ Class represents an object existing within the game world. """
   IsInteractive: bool
   _Pos: tuple
   IsSolid: bool

   def __init__(self, init_room, init_pos=(0, 0), solid=True, interactive=False):
       self._CRoom = init_room
       self.IsSolid = solid
       self._Pos = init_pos
       self.IsInteractive = interactive
       self._IsPhysical = False

   def __str__(self):  # string for unspecified static objects
       if self.IsSolid:
           return '#'
       else:
           return '~'

   @property
   def pos(self):  # return the Coord the static is @
       return copy.copy(self._Pos)

   @pos.setter
   def pos(self, value):
       assert isinstance(value, tuple)
       self._Pos = value
  
   def p_init(self):
       self._IsPhysical = True
       self._CRoom.add_obj(self)

   def move_8d(self, direction, distance):  # move in a cardinal direction a number of units
       new_pos = self.pos

       if direction == 'n':
           new_pos = (new_pos[0], new_pos[1] - distance)
       elif direction == "ne":
           new_pos = (new_pos[0] + distance, new_pos[1] - distance)
       elif direction == 'e':
           new_pos = (new_pos[0] + distance, new_pos[1])
       elif direction == 'se':
           new_pos = (new_pos[0] + distance, new_pos[1] + distance)
       elif direction == 's':
           new_pos = (new_pos[0], new_pos[1] + distance)
       elif direction == 'sw':
           new_pos = (new_pos[0] - distance, new_pos[1] + distance)
       elif direction == 'w':
           new_pos = (new_pos[0] - distance, new_pos[1])
       elif direction == "nw":
           new_pos = (new_pos[0] - distance, new_pos[1] - distance)
       else:
           raise ValueError('''Invalid direction "{}"'''.format(direction))
      
       if self._CRoom.is_solid_at(new_pos):
           raise SolidCollision("Cannot move to position @ " + str(new_pos))

       self.pos = new_pos


class Item:
   """ Item class represents an item that can be stored within something. """

   def __init__(self, init_name="Empty",  init_defense=0, init_attack=0, init_equipable=False, init_obtained=False):
       self.Name = init_name
       self.Defense = init_defense
       self.Attack = init_attack
       self.IsEquipable = init_equipable
       self.IsObtained = init_obtained


class Inventory:
   """ Inventory class represents a Player's inventory. """

   def __init__(self, init_defense=0,
                init_equipped={"head": Item(), "body": Item(), "rings": Item(), "weapon": Item()}, init_unequipped=[],
                init_misc=[]):
       self.Defense = init_defense  # integer representing the total defense value
       self.Equipped = init_equipped  # dictionary of equipped Item objects
       self.Unequipped = init_unequipped
       self.Misc = init_misc

   def __str__(self):
       return str(self.getAtts())


class Player(GameObj):
   """ Player class carries the attributes of a player. """
   Inv: Inventory
   Htp: List[int]

   def __init__(self, c_room, init_name='P', init_agi=1, init_dxt=1, init_end=1, init_int=1, init_str=1, init_exp=0,
                init_lvl=1, init_htp=[1, 1], init_inv=Inventory(), init_pos=(1, 1)):
       GameObj.__init__(self, c_room, init_pos, True, False)
       self.Name = init_name
       self.Htp = init_htp  # Hit points [current, max]
       self.Agi = init_agi  # Agility
       self.Dxt = init_dxt  # Dexterity
       self.End = init_end  # Endurance
       self.Exp = init_exp  # Experience
       self.Int = init_int  # Intelligence
       self.Inv = init_inv  # Inventory
       self.Lvl = init_lvl  # Level
       self.Str = init_str  # Strength

   def __str__(self):
       return '@'

   def stat_string(self):  #move to main later#
       return "Health: {}  Exp: {}  Level: {}\n".format(self.Htp[0], self.Exp, self.Lvl)

   def prompt_plyr_atts(self):
       """ Collect and assign the player attributes from a series of prompts. """

       ans1 = ''
       while not (ans1 == 'y' or ans1 == 'Y'):
           player_name, attPoints = input(
               "What is your name?\n>"), 50  # request name and initialize number of skill points
           cheat_names = ("Goku", "Saitama", "Superman")
           if (player_name.capitalize()) in cheat_names:  # if it's a cool name, give the player cool atts
               intel, dexte, agili, endur, stren = 10, 10, 10, 8901, 999
               ans1 = input("Are you sure you wish to continue with that name? ('Y' for yes)\n")

           else:  # this is where a bunch of prompts ask for the user to assign skill points
               print(
                   "\nYou possess the skills of intelligence, dexterity, agility, endurance, and strength. You have {} skill points to allocate.".format(attPoints))
               intel = int(input("\nWhat shall be your intelligence? ({} points left)\n>".format(attPoints)))
               attPoints -= intel
               dexte = int(input("What shall be your dexterity? ({} points left)\n>".format(attPoints)))
               attPoints -= dexte
               agili = int(input("What shall be your agility? ({} points left)\n>".format(attPoints)))
               attPoints -= agili
               endur = int(input("What shall be your endurance? ({} points left)\n>".format(attPoints)))
               attPoints -= endur
               stren = int(input("What shall be your strength? ({} points left)\n>".format(attPoints)))
               attPoints -= stren

               if not attPoints < 0:
                   ans1 = input("Do you wish to continue? ('Y' for yes)\n>")
               else:
                   print("Invalid input")

       # assign all of that data to the player's attributes
       self.Name, self.Htp = player_name, [100 + endur, 100 + endur]
       self.Int, self.Dxt, self.Agi, self.End, self.Str = intel, dexte, agili, endur, stren

       return True


def clear():
   """ Clear the terminal """

   os.system('clear') ##'cls' if os.name() == 'nt' else 'clear')


def create_statics(room, w, l, start_pos=(0, 0), solidity=True): ##**NOT FINISHED**##
   """ Return static objects in list, assigned their position;
   first with position (startPos), last with position (startPos[0]+w, startPos[1]+l). """
   pass
   print("about to make walls")
   statics = []  # list for static objects (basically walls)
   for row in range(start_pos[0], w + start_pos[0]):
       for col in range(start_pos[1], l + start_pos[1]):
           newStatic = GameObj(room, (row, col), solidity)
           newStatic.p_init()
           statics.append([newStatic])  # add static @ pos(row, col)
           print((row, col))  # poop #

   print("made the walls")
   return statics

def distance_to(a, b):
   return math.sqrt((a[0] - b[0]) **2 + (a[1] - b[1]) **2)
