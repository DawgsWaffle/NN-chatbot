package io.github.lunarwatcher.chatbot.bot.commands.twitch

import io.github.lunarwatcher.chatbot.bot.chat.Message
import io.github.lunarwatcher.chatbot.bot.chat.ReplyMessage
import io.github.lunarwatcher.chatbot.bot.command.CommandCenter
import io.github.lunarwatcher.chatbot.bot.commands.AbstractCommand
import io.github.lunarwatcher.chatbot.bot.sites.twitch.TwitchChat

class JoinTwitch : AbstractCommand("joinTwitch", listOf("join-twitch"), rankRequirement = 5){
    override fun handleCommand(message: Message): List<ReplyMessage>? {
        if(!canUserRun(message.user, message.chat)){
            return getLowRankMessage();
        }

        val twitch = CommandCenter.bot.getChatByName("twitch") ?: return listOf(ReplyMessage("Twitch is not set up.", true))

        val where = splitCommand(message.content)["content"] ?: return listOf(ReplyMessage("You have to tell me where to join", true))
        if(twitch !is TwitchChat)
            return listOf(ReplyMessage("The chat instance with the name \"twitch\" is not an instance of \"TwitchChat\". TL;DR: I'm broken", true))

        if(!twitch.doesChannelExist(where))
            return listOf(ReplyMessage("That channel does not appear to exist", true))

        if(twitch.isInChannel(where))
            return listOf(ReplyMessage("I'm already there", true))

        val result = twitch.joinChannel(where)
        return if(!result)
            listOf(ReplyMessage("Something went wrong when trying to join", true))
        else listOf(ReplyMessage("Joined $where!", true))
    }
}