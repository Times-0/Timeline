# Commands
Commands let you invoke custom functions using some shortcuts codes/commands from the chat system.

# Default
**Prefix:** `!`

**Using command:** `!<command_name> command_param_1 command_param_2 command_param_3 ... command_param_n`
    Example, `!jr 100`, `!jr [name] Town`

# Usage
This command system is very elegant and easy to use. 

<details>
<summary> If you are to add new commands within the Commands.py file, <a>click me</a> </summary>

Find `__commands__` in the file `Commands.py`, and add your custom commands to it.
For example, if your `__commands__` looks like
```py
__commands__ = ["jr"]
```
and you want to add a new command `ac` (which can be used like `!ac`), you just add `ac` to the list as follows
```py
__commands__ = ["jr", "ac"]
```

Now that the Plugin knows such command `ac` exists, all you need to do next is make a function that can process that command, 
for that find this line
```py
GeneralEvent.on('command=jr', self.JoinRoomByExtId)
```
Below the same (without changing indents), add the following
```py
GeneralEvent.on('command=ac', self.AddCoinsToTheUser)
```

Now that you have a function `AddCoinsToTheUser`, you must define it, add that function in the same class :-).
For example,
```py
from Timeline.Database.DB import Coin

def AddCoinsToTheUser(self, client, params): # The parameters are exact and doesn't change
    coins = int(params[0])
    Coin(penguin_id=client['id'], transaction=coins, comment="Coins earned by playing Command").save()
```
</details>

<details>
<summary> If you are to use this in a different plugin <a>click me</a> </summary>

First you need to include the dependency/requirement for commands plugin, then add it to `__commands__`, then invoke a event for it. 

Let's take an example plugin of `TestPlugin`, which does the same as above, adding coins.
```py
from Timeline.Utils.Plugins.IPlugin import IPlugin, IPluginAbstractMeta, Requirement
from Timeline.Utils.Plugins import extend

from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline.Database.DB import Coin

import logging

class TestPlugin(IPlugin):
    """Testing commands outside commandPlugin"""


    requirements = [Requirement(**{'name' : 'Commands', 'developer' : 'Dote'})]
    name = 'TestPlugin'
    developer = 'None'
    
    command = "ac" # the command you are going to test
    
     def __init__(self):
        super(TestPlugin, self).__init__()

        self.logger = logging.getLogger(TIMELINE_LOGGER)
        
        CommandsPlugin = self.dependencies[0]        
        if self.command not in CommandsPlugin.__commands__:
            CommandsPlugin.__commands__.append(self.command)

        GeneralEvent.on('command={}'.format(self.command.lower()), self.handleAddCoins)
        self.logger.debug("Add Coins Command set. Command : %s", self.command)

     def handleAddCoins(self, client, params):
        coins = int(params[0])
        Coin(penguin_id=client['id'], transaction=coins, comment="Coins earned by !AC Command").save()
    
```

</details>


**NOTE: All the commands must be in lowercases while adding to `__commands__`, but while using it you can use it as preferred**
