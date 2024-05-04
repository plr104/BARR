__version__ = "0.20"
__author__ = "Phillip L. Reid"

import barr_engine as eng

# tuples of valid commands and Exception classes
# please add new elements to end of the tuples to prevent unexpected behavior from take_cmd_input()
MASTER_CMDS = ("", 'n', 'w', 's', 'e', "ne", "nw", "se", "sw", 'a', 'i')
ACTION_CMDS = ("Possible actions:", 'a', 'i', 'u', 'o')  # tuple of subcommands for actions
INVENT_CMDS = ("inventory:", 'c', 'e', 'd', 'u', 's')  # tuple of subcommands for the inventory


class NotValidCommand(Exception):
   """ Raised when a command is not in the list of valid commands """
   pass


def main():
   """
   Written by Phillip L. Reid
   Created in 2017
   Last update: 28 May 2019
   """

   print("\t\t  **BARR**\n\t  A cool Rogue RPG by PLR\n")
   currentRoom = eng.Room((12, 8))  # create a beginning 8x16 room
   eng.GameObj(currentRoom, (1,2), True).p_init()
   ##player.prompt_plyr_atts() # assign player attributes
   player = eng.Player(currentRoom, "Phill", 10, 10, 10, 10, 10, 9001)
   player.p_init()

   ##someWalls = eng.create_statics(currentRoom, 0, 20)

   draw_room(currentRoom, player)
   print('''Enter "Help" for a list of commands.''')
   result_str = take_cmd_input(player, MASTER_CMDS)
   while True:
       draw_room(currentRoom, player)
       print(result_str)
       result_str = take_cmd_input(player, MASTER_CMDS)
  
   print("END OF GAME")


def draw_room(room, plyr):
   """ Clear terminal, print title, stats, and room """

   eng.clear()
   print("\t\t  **BARR**\n\t  A cool Rogue RPG by PLR\n")  # reprint the title
   print(plyr.stat_string())
   room.update_map_str()
   print(room)


def take_cmd_input(plyr, cmds):##rename cmds var
   """ Prompt for player input and update player object accordingly. """
  
   print(cmds[0] + '\n')
  
   cmd = ''  # initialize a variable for the command from user
   while cmd == '':  # keep asking for command from player until a valid command is given
       try:
           cmd = input("\nInput command:")
           cmd = cmd.lower().strip()  # make string lower case and remove whitespace
          
           if cmd == "help":
               print(cmds)
               cmd = ''
               continue
           if cmd not in cmds:  # check if command is valid
               cmd = ''
               raise NotValidCommand("Not a valid command.")
       except (TypeError, NotValidCommand):
           print('''Invalid command, enter "help" for a list of valid commands.''')
  
   cmd_num = -1
   for i, j in enumerate(cmds):  # assign a number to cmd_num for easier control flow
       if j == cmd:
           cmd_num = i
           break
  
   if cmds == MASTER_CMDS:
       if cmd_num < 9:  # if the command is a move command
           try:
               plyr.move_8d(cmd, 1)
               return "You successfully moved."
           except eng.SolidCollision:
               return "You cannot move there."
           except ValueError:
               return "You cannot move there."
       elif cmd_num == 9:  # if the action command
           return take_cmd_input(plyr, ACTION_CMDS)
       elif cmd_num == 10:  # if the inventory command
           return take_cmd_input(plyr, INVENT_CMDS)
  
   elif cmds == ACTION_CMDS:
       if cmd_num == 1:
           return "attacked"
       elif cmd_num == 2:
           return "interacted"
       elif cmd_num == 3:
           return "used"
       elif cmd_num == 4:
           return "observed"
  
   elif cmds == INVENT_CMDS:
       while True:
           break
       return "Closed inventory."
  
   return ''


if __name__ == "__main__":
   main()
