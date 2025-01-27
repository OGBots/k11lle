import telebot
import os
import importlib

# Bot Token
TOKEN = "7818875325:AAF4iyHLavFsnUxyzcmEkEAT-cjd3_OW3xE"
bot = telebot.TeleBot(TOKEN)

# Database Files
USERS_FILE = "users.txt"
REDEEM_FILE = "redeem_codes.txt"
ADMINS_FILE = "admins.txt"
BANNED_FILE = "banned_users.txt"

def read_file(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename, "r") as file:
        return {line.split(',')[0]: line.strip().split(',')[1:] for line in file}

def write_file(filename, data):
    with open(filename, "w") as file:
        for key, values in data.items():
            file.write(f"{key},{','.join(values)}\n")

# Start Command
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = str(message.from_user.id)
    banned_users = read_file(BANNED_FILE)
    users = read_file(USERS_FILE)

    if user_id in banned_users:
        bot.send_message(user_id, "🚫 You are banned from using this bot.")
        return

    if user_id not in users:
        users[user_id] = ["1", "0"]  # 1 credit, not premium
        write_file(USERS_FILE, users)
        bot.send_message(user_id, "💎 *Welcome to OG KILLEE!* 💎\n\n_You have 1 credit._\nUse /help for commands.", parse_mode="Markdown")
    else:
        bot.send_message(user_id, "👋 Welcome back! Use /help to see all commands.")

# Profile Info
@bot.message_handler(commands=['info'])
def info_command(message):
    user_id = str(message.from_user.id)
    users = read_file(USERS_FILE)

    if user_id in users:
        credits, premium = users[user_id]
        status = "🌟 *Premium*" if premium == "1" else "🔹 Regular"
        bot.send_message(user_id, f"📋 *Profile Info:* 📋\n\n💰 *Credits:* {credits}\n🏆 *Status:* {status}", parse_mode="Markdown")
    else:
        bot.send_message(user_id, "❌ You are not registered. Use /start to begin.")

# Redeem Code
@bot.message_handler(commands=['redeem'])
def redeem_command(message):
    user_id = str(message.from_user.id)
    args = message.text.split()

    if len(args) < 2:
        bot.send_message(user_id, "⚠ Usage: /redeem [code]")
        return

    code = args[1]
    users = read_file(USERS_FILE)
    redeem_codes = read_file(REDEEM_FILE)

    if code in redeem_codes:
        credits_to_add = int(redeem_codes[code][0])

        if user_id not in users:
            users[user_id] = ["1", "0"]  # Default user entry
        
        users[user_id][0] = str(int(users[user_id][0]) + credits_to_add)
        del redeem_codes[code]

        write_file(USERS_FILE, users)
        write_file(REDEEM_FILE, redeem_codes)
        bot.send_message(user_id, f"✅ Code redeemed! You received *{credits_to_add}* credits.", parse_mode="Markdown")
    else:
        bot.send_message(user_id, "❌ Invalid or expired code.")

# Create Redeem Code (Admin Only)
@bot.message_handler(commands=['createredeem'])
def create_redeem_command(message):
    user_id = str(message.from_user.id)
    admins = read_file(ADMINS_FILE)

    if user_id not in admins:
        bot.send_message(user_id, "❌ You are not authorized to use this command.")
        return

    args = message.text.split()
    if len(args) < 3:
        bot.send_message(user_id, "⚠ Usage: /createredeem [code] [credits]")
        return

    code, credits = args[1], args[2]
    
    if not credits.isdigit():
        bot.send_message(user_id, "❌ Credits must be a number.")
        return

    redeem_codes = read_file(REDEEM_FILE)
    if code in redeem_codes:
        bot.send_message(user_id, "❌ Code already exists.")
        return

    redeem_codes[code] = [credits]
    write_file(REDEEM_FILE, redeem_codes)
    bot.send_message(user_id, f"✅ Redeem code `{code}` created for {credits} credits.", parse_mode="Markdown")

# Buying Credits
@bot.message_handler(commands=['buy'])
def buy_command(message):
    user_id = str(message.from_user.id)
    buy_options = (
        "💳 *Buy Credits* 💳\n\n"
        "🔹 50 Credits = $5\n"
        "🔹 100 Credits = $10\n"
        "🔹 500 Credits = $50\n\n"
        "📩 Contact @SatsNova to purchase."
    )
    bot.send_message(user_id, buy_options, parse_mode="Markdown")

# Help Menu
@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = str(message.from_user.id)
    help_message = (
        "📌 *Help Menu* 📌\n\n"
        "🔹 /start - Start the bot and check credits\n"
        "🔹 /info - View your profile and credits\n"
        "🔹 /redeem [code] - Redeem a code for credits\n"
        "🔹 /buy - Purchase credits\n"
        "🔹 /status - Check Gate Health\n"
        "🔹 /cmds - View available commands\n\n"
        "💬 *Support:* Contact @SatsNova."
    )
    bot.send_message(user_id, help_message, parse_mode="Markdown")

# Available Commands
@bot.message_handler(commands=['cmds'])
def cmds_command(message):
    user_id = str(message.from_user.id)
    cmds_list = (
        "🔹 /chk - Check Card (Live or Not)\n"
        "🔹 /kd - Kill CC (Premium Only)\n"
    )
    bot.send_message(user_id, f"🛠 *Available Commands:* \n{cmds_list}", parse_mode="Markdown")

# Admin Commands
@bot.message_handler(commands=['ban'])
def ban_command(message):
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, "⚠ Usage: /ban [user_id]")
        return
    banned_users = read_file(BANNED_FILE)
    banned_users[args[1]] = ["1"]
    write_file(BANNED_FILE, banned_users)
    bot.send_message(message.chat.id, f"🚫 User {args[1]} has been banned.")

@bot.message_handler(commands=['givepremium'])
def give_premium_command(message):
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, "⚠ Usage: /givepremium [user_id]")
        return
    users = read_file(USERS_FILE)
    if args[1] in users:
        users[args[1]][1] = "1"
        write_file(USERS_FILE, users)
        bot.send_message(message.chat.id, f"🏆 User {args[1]} is now a premium user.")
    else:
        bot.send_message(message.chat.id, "❌ User not found.")

@bot.message_handler(commands=['og'])
def admin_commands(message):
    bot.send_message(message.chat.id, "⚙ *Admin Commands:*\n/addadmin [user_id]\n/createredeem [code] [credits]\n/ban [user_id]\n/givepremium [user_id]\n/og", parse_mode="Markdown")

# Run Bot
bot.polling(none_stop=True)
