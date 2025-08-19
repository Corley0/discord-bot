Use `?help` to access syntax and the setup guild

# Setup Guide
1) Do `?giveaway setup` in the channel you wish to send all giveaway messages to, this includes claim tickets.
2) Create a giveaway host role
3) Do `?giveaway host_role [role]` to assign the host role.

# Giveaway Command Syntax
`?giveaway create [sponsor] [prize] [duration] [claim time]`
`?giveaway end [message id]`
`?giveaway reroll [message id]`
`?giveaway delete [message id]`

**Message ID:** Message ID of the original giveaway message.
**Time Format:** Use a number followed by a letter.
-   `m` = minutes (e.g. `10m` → 10 minutes)
-   `h` = hours (e.g. `2h` → 2 hours)
-   `d` = days (e.g. `1d` → 1 day)

**Prize:** Single word string unless quoted

**Example Giveaway Command:**
A giveaway for $1000 hosted by @corley lasting 7 days with a claim time of 1 day
`?giveaway create @corley $1000 7d 1d`

# Moderation Commands Syntax
    
`?purge any [amount] ?purge user [user] [amount]`
`?warn [user] [reason]`
`?warns [user]`
`?mute [user] [duration] [reason]`
`?unmute [user] [reason]`

**Time Format:** Use a number followed by a letter.
-   `m` = minutes (e.g. `10m` → 10 minutes)
-   `h` = hours (e.g. `2h` → 2 hours)
-   `d` = days (e.g. `1d` → 1 day)
