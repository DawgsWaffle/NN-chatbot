
# Google command
# Kill command
# Lick command
# Give command

# Ban, unban, promote, demote
# wikipedia
# xkcd

import discord
import Config
import random as r
import os
import time

r.seed = time.time()

class PermissionManager:
    sites: list() = []

    @staticmethod
    def addSite(name: str):
        site = Site(name)
        PermissionManager.sites.append(site)

    @staticmethod
    def assumeAllAndInject():
        PermissionManager.addSite("stackoverflow.com")
        PermissionManager.addSite("stackexchange.com")
        PermissionManager.addSite("meta.stackexchange.com")
        PermissionManager.addSite("discord")

    @staticmethod
    def getSite(name: str):
        for site in PermissionManager.sites:
            if name == site.name:
                return site
        return None
    @staticmethod
    def saveAll():
        for site in PermissionManager.sites:
            site.save()

class Command():

    def __init__(self, name: str, aliases: [], help: str, desc: str, handlerMethod, rankReq: int = 1):
        self.name = name;
        self.aliases = aliases
        self.help = help
        self.desc = desc
        self.rankReq = rankReq
        self.handlerMethod = handlerMethod

    def onMessage(self, specificCommand, message, userId: int, site: str, indentBased=True):
        ste = PermissionManager.getSite(site)
        userRank = ste.getUserRank(userId)
        if userRank < self.rankReq:
            return True, "You don't have permission to use this command"
        reply, response = self.handlerMethod(specificCommand, message, indentBased, userRank, site)
        return reply, response

class StaticResponses:
    licks = ["Tastes horrible!", "Tastes like a wet cat!", "Tastes like a wet dog!", "Tastes like pizza!",
             "Tastes like sewer! *shivers*", "*dies*", "*shivers*", "*passes out*",
             "Tastes AWFUL! *goes back in time to avoid licking it in the first place*"]
    kills = ["*shoots {}*. ***HEADSHOT!***", "{} has been disposed of.",
             "{} was in an airplane \"accident\"", "It was in the news. {} didn't watch enough MLP!",
             "{} was beamed into space", "PIRATES! {} was ejected along with the rest of the crew",
             "{} didn't watch their step and fell off a cliff", "Unfortunately, {} hasn't been heard from in a few days",
             "I can't dispose of {}. They're already disposed of", "It's all over the news today, {} was killed by an angry mob!",
             "*sending poisoned dinner to {}...*"]

async def delegateDiscord(message: discord.Message, dClient: discord.Client, uid: int, nnFun):
    # The discord part checks for the presence of the trigger before callig this method
    triggerless = str(message.content)[len(Config.trigger):]
    cmdName = triggerless.split()[0]
    messageContent = triggerless[len(cmdName):].strip()
    try:
        _, replyContent = Commands.commands[Commands.getCommandName(cmdName)].onMessage(cmdName, messageContent, uid, "discord", False)
        await dClient.send_message(message.channel, replyContent)
    except KeyError:
        await dClient.send_message(message.channel, "Sorry, that's not a command I know");

def delegate(message, uid: int, client, nnFun):
    site = client.host
    if PermissionManager.getSite(site).getUserRank(uid) == 0:
        return

    if message.content.startswith(Config.netTrigger):
        message.message.reply(nnFun(Commands.cleanMessage(message.content.replace(Config.netTrigger, "").strip())))
        return
    # TODO listeners
    if not message.content.startswith(Config.trigger):

        return
    cleaned = Commands.cleanMessage(message.content)
    triggerless = str(cleaned)[len(Config.trigger):]
    cmdName = triggerless.split()[0]
    messageContent = triggerless[len(cmdName) + 1:]

    try:
        reply, replyContent = Commands.commands[Commands.getCommandName(cmdName)].onMessage(cmdName, messageContent, uid, site)
        if(reply):
            message.message.reply(replyContent)
        else:
            message.room.send_message(replyContent)
    except KeyError:
        message.message.reply("Sorry, that's not a command I know");

def helpCommand(specificCommand, message, indentBased, userRank: int, site: str):
    commandNames = list(Commands.commands.keys())
    commandDescriptions = [cmd.desc for name, cmd in Commands.commands.items()]
    res = ""
    maxLen = 0
    for n in commandNames:
        maxLen = max(maxLen, len(n))
    for i in range(len(commandNames)):
        adjustedLen: int = (maxLen) - len(commandNames[i])
        res = res + commandNames[i] + "".join([" " for i in range(adjustedLen)]) + " | " + commandDescriptions[i] + "\n"

    return False, fixedFormat(res, not indentBased)

def lickCommand(specificCommand, message, discord: bool, userRank: int, site: str):
    message = message.strip()
    if message == "":
        return "You have to tell me who to lick"
    return True, "*licks " + message + "*. " + StaticResponses.licks[r.randint(0, len(StaticResponses.licks) - 1)]

def killCommand(specificCommand, message, discord: bool, userRank: int, site: str):
    message = message.strip()
    print(">>:" + message)
    if message == "":
        return "You have to tell me who to kill"
    return True, StaticResponses.kills[r.randint(0, len(StaticResponses.kills) - 1)].format(message)

def rankUpdate(specificCommand, message, discord: bool, userRank : int, site: str):
    try:
        split = message.split(" ")
        if len(split) != 2 and specificCommand != "ban" and specificCommand != "unban":
            return True, "Arguments required: userId newRank"
        id = int(split[0].strip())
        if specificCommand != "ban" and specificCommand != "unban":
            newRank = int(split[1].strip())
        elif specificCommand == "ban":
            newRank = 0
        else:
            newRank = 1
    except ValueError:
        return True, "Invalid ID"

    currentRank = PermissionManager.getSite(site).getUserRank(id)

    if specificCommand == "ban":
        if userRank < 7:
            return True, "Not high enough rank!"
        if(userRank <= currentRank):
            return True, "You cannot ban someone with an equal higher rank than you"
        if currentRank == 10:
            return True, "You cannot ban admins. Please remove them manually from Config.py before trying to ban"
        PermissionManager.getSite(site).setUserRank(id, newRank)
        return True, "User {} has been banned".format(id)
    elif specificCommand == "setRank":
        if userRank < 8:# If the requesting user's rank is < 8
            return True, "Not high enough rank!"
        if currentRank >= userRank \
                and not userRank == 10 and not currentRank == 10:# if the rank of the updating user >= the user and the users rank != 10 and the current rank != 10
            return True, "You cannot change the rank of someone with a higher or the same rank as you"
        if newRank == 10:
            return True, "Rank 10 is bot admin. These can only be added in Config.py"
        if currentRank == 10:
            if id in Config.ownerIds[site]:
                return True, "You cannot change the ranks of bot admins. Please remove them manually"
            if userRank < 10:
                return True, "You have to be a bot admin to remove rank 10 users"
        PermissionManager.getSite(site).setUserRank(id, newRank)
        return True, "User {}'s rank changed to {}".format(id, newRank)
    return True, "Unimplemented call: {}".format(specificCommand)

def getRank(specificCommand, message, discord: bool, userRank : int, site: str):
    try:
        id = int(message.strip())
    except ValueError:
        return True, "Invalid ID"

    currentRank = PermissionManager.getSite(site).getUserRank(id)

    return True, "User {} has the rank {}".format(id, currentRank)

def aboutCommand(specificCommand, message, discord: bool, userRank : int, site: str):
    return True, "Hiya! I'm {}. I'm a chatbot created by [Olivia](https://github.com/LunarWatcher). I'm written in Python, in order to use Tensorflow and use it for" \
                 " machine learning, which allows me to talk when you mention me. In addition, there are commands you can use. See the list by doing {}help. My source is available on [GitHub]({})".format(Config.botName, Config.trigger, Config.ghRepo)
# Utils

def fixedFormat(stringToFormat: str, discord: bool):
    result = ""
    if not discord:
        for line in stringToFormat.split("\n"):
            result += ''.join([" " for i in range(4)]) + line + "\n"
    else:
        result += "```"
        result += stringToFormat
        result += "```"
    return result

class Site:

    def __init__(self, name: str):
        self.name = name
        self.users = dict()

        for site, ownerList in Config.ownerIds.items():
            if site == name:
                for ownerId in ownerList:
                    self.users.update({ownerId : 10})

        self.fileName = "privs_" + self.name.replace(".", "_") + ".dat"
        if os.path.isfile(Config.storageDir + self.fileName):
            with open(Config.storageDir + self.fileName, "r") as f:
                lines = f.readlines()
                for line in lines:
                    if line != "":
                        split = line.split(" +++$+++ ")
                        uid = int(split[0].strip())
                        rank = int(split[1].strip())
                        self.setUserRank(uid, rank)

    def save(self):
        if not os.path.isdir(Config.storageDir):
            os.makedirs(Config.storageDir)
        with open(Config.storageDir + self.fileName, "w") as f:
            for uid, rank in self.users.items():
                f.write(str(uid) + " +++$+++ " + str(rank) + "\n")

    def getUserRank(self, userId):
        if not userId in self.users:
            # Avoid crash on unknown users, + index more users
            self.users.update({userId: 1})
        return self.users[userId]

    def setUserRank(self, userId, newRank):
        self.users.update({userId : newRank})

class Commands:
    commands = {
        "about" : Command("about", ["whoareyou"], "", "Let me tell you a little about myself...", handlerMethod=aboutCommand, rankReq=1),
        "help" : Command("help", ["halp", "hilfe", "help"], "", "Lists the bots commands", handlerMethod=helpCommand, rankReq=1),
        "lick" : Command("lick", [], "", "Licks someone", handlerMethod=lickCommand, rankReq=1),
        "kill" : Command("kill", ["assassinate"], "", "Disposes of someone", handlerMethod=killCommand, rankReq=1),
        "ban"  : Command("ban", ["exterminate"], "", "Bans someone. Rank 8+", handlerMethod=rankUpdate, rankReq=8),
        "getRank" : Command("getRank", [], "", "Gets someone's rank. Rank 7+", handlerMethod=getRank, rankReq=7),
        "setRank" : Command("setRank", [], "", "Changs someone's rank. Rank 8+", handlerMethod=rankUpdate, rankReq=8)
    }

    @staticmethod
    def getCommandName(foundName: str):
        try:
            cmd = Commands.commands[foundName.strip()]#This throws an exception if not found
            if cmd is None:
                raise KeyError()
            return foundName# Meaning if it gets here, it is found and the command name is this name
        except KeyError:
            # This is where things gets complicated.
            pass
        # Since the key isn't the obvious one (the name itself), it is most likely an alias
        # So iterate the commands dict...
        for cmdN, command in Commands.commands.items():
            for alias in command.aliases:#... iterate the aliases ...
                if foundName == alias:# ... and if the alias matches...
                    return cmdN #... return the name of the command.
        return None# Otherwise, all options are exhausted. Return None

    cleaning = {"&quot;": "\"", "&#39;" : '\'',
                "&gt;": ">", "&lt;": "<"}
    @staticmethod
    def cleanMessage(raw: str):
        fixed = raw
        for k, v in Commands.cleaning.items():
            fixed = fixed.replace(k, v)
        return fixed

