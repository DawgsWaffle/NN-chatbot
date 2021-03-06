package io.github.lunarwatcher.chatbot.bot.sites;

import io.github.lunarwatcher.chatbot.Database;
import io.github.lunarwatcher.chatbot.SiteConfig;
import io.github.lunarwatcher.chatbot.User;
import io.github.lunarwatcher.chatbot.bot.command.CommandCenter;
import io.github.lunarwatcher.chatbot.bot.command.CommandGroup;
import io.github.lunarwatcher.chatbot.data.BotConfig;
import org.jetbrains.annotations.NotNull;

import java.io.IOException;
import java.util.List;
import java.util.Properties;

public interface Chat {
    void logIn() throws IOException;
    void save();
    void load();

    BotConfig getConfig();
    String getName();
    List<Long> getHardcodedAdmins();
    Properties getBotProps();
    Database getDatabase();
    CommandCenter getCommands();

    /**
     * Since the username systems for each site is different, this method aims to add abstraction to get it.
     * The uid is a long to handle everything, but if it's necessary to use as an int, casting locally is the
     * way to go
     * @param uid The user ID to retrieve
     * @return The username, or a stringified form of the UID if not found.
     */
    String getUsername(long uid);
    List<Long> getUidForUsernameInRoom(String username, long server);
    void leaveServer(long serverId);
    boolean getTruncated();
    List<CommandGroup> getCommandGroup();
    SiteConfig getCredentialManager();
    @NotNull
    List<User> getUsersInServer(long server);
    Host getHost();
    boolean editMessage(long messageId, String newContent);
    boolean deleteMessage(long messageId);

}
