import telebot
import os

# Bot Token
TOKEN = "7818875325:AAF4iyHLavFsnUxyzcmEkEAT-cjd3_OW3xE"
bot = telebot.TeleBot(TOKEN)

# File-based Database
USERS_FILE = "users.txt"
REDEEM_FILE = "redeem_codes.txt"
ADMINS_FILE = "admins.txt"
BANNED_FILE = "banned_users.txt"
LOG_FILE = "bot_logs.txt"

def read_file(filename):
    """ Reads data from the given file and returns it as a dictionary """
    if not os.path.exists(filename):
        return {}
    with open(filename, "r") as file:
        return {line.split(',')[0]: line.strip().split(',')[1:] for line in file}

def write_file(filename, data):
    """ Writes data from the dictionary to the file """
    with open(filename, "w") as file:
        for key, values in data.items():
            file.write(f"{key},{','.join(values)}\n")

def log_action(action):
    """ Logs actions to a log file """
    with open(LOG_FILE, "a") as log:
        log.write(action + "\n")

# Command: /start
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = str(message.from_user.id)
    banned_users = read_file(BANNED_FILE)
    if user_id in banned_users:
        bot.send_message(user_id, "You are banned from using this bot.")
        return
    users = read_file(USERS_FILE)
    if user_id not in users:
        users[user_id] = ["1", "0"]  # 1 credit, not premium
        write_file(USERS_FILE, users)
        bot.send_message(user_id, "Welcome to OG KILLER 💎\nYou have 1 credit.")
    else:
        bot.send_message(user_id, "Welcome back! Use /info to check your credits.")

# Command: /info
@bot.message_handler(commands=['info'])
def info_command(message):
    user_id = str(message.from_user.id)
    users = read_file(USERS_FILE)
    if user_id in users:
        credits, premium = users[user_id]
        status = "Premium" if premium == "1" else "Regular"
        bot.send_message(user_id, f"Profile Info:\nCredits: {credits}\nStatus: {status}")
    else:
        bot.send_message(user_id, "You are not registered. Use /start to begin.")

# Command: /redeem [code]
@bot.message_handler(commands=['redeem'])
def redeem_command(message):
    user_id = str(message.from_user.id)
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(user_id, "Usage: /redeem [code]")
        return
    code = args[1]
    users = read_file(USERS_FILE)
    redeem_codes = read_file(REDEEM_FILE)
    if code in redeem_codes:
        credits_to_add = redeem_codes[code][0]
        users[user_id][0] = str(int(users[user_id][0]) + int(credits_to_add))
        del redeem_codes[code]  # Remove used code
        write_file(USERS_FILE, users)
        write_file(REDEEM_FILE, redeem_codes)
        bot.send_message(user_id, f"Code redeemed! You received {credits_to_add} credits.")
        log_action(f"User {user_id} redeemed code {code} for {credits_to_add} credits.")
    else:
        bot.send_message(user_id, "Invalid or expired code.")

# Command: /kd (Premium Only)
@bot.message_handler(commands=['kd'])
def kd_command(message):
    user_id = str(message.from_user.id)
    users = read_file(USERS_FILE)
    if user_id in users and users[user_id][1] == "1":
        bot.send_message(user_id, "Kill CC executed successfully!")
    else:
        bot.send_message(user_id, "You must be a premium user to use this command.")

# Command: /buy
@bot.message_handler(commands=['buy'])
def buy_command(message):
    user_id = str(message.from_user.id)
    buy_options = (
       "💳 *Buy Credits* 💳\n\n"
        "🔹 50 Credits = $5\n"
        "🔹 100 Credits = $10\n"
        "🔹 500 Credits = $50\n\n"
        "📩 Contact @SatsNova or @@GareebRehanKaAbbu to purchase."
    )
    bot.send_message(user_id, buy_options)

# Command: /help
@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = str(message.from_user.id)
    help_message = (
        "📌 Help Menu 📌\n\n"
        "🔹 /start - Start the bot and check credits\n"
        "🔹 /info - View your profile and credits\n"
        "🔹 /redeem [code] - Redeem a code for credits\n"
        "🔹 /buy - Purchase credits\n"
        "🔹 /status - Check Gate Health\n"
        "🔹 /cmds - View available commands\n\n"
        "For further assistance, contact @SatsNova."
    )
    bot.send_message(user_id, help_message)

# Command: /cmds
@bot.message_handler(commands=['cmds'])
def cmds_command(message):
    user_id = str(message.from_user.id)
    cmds_list = (
        "/kd - Kill CC (Premium Only)\n"
        "/chk - Check Cards\n"
    )
    bot.send_message(user_id, f"Available Commands:\n{cmds_list}")

# Admin Commands

# Add Admin Command
@bot.message_handler(commands=['addadmin'])
def add_admin_command(message):
    user_id = str(message.from_user.id)
    admins = read_file(ADMINS_FILE)
    
    # Check if the user is an existing admin
    if user_id not in admins:
        bot.send_message(user_id, "You are not authorized to add admins.")
        return
    
    # Check if the new admin ID is provided
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(user_id, "Usage: /addadmin [user_id]")
        return
    
    # New admin user_id
    new_admin_id = args[1]
    if new_admin_id == user_id:
        bot.send_message(user_id, "You cannot add yourself as an admin.")
        return
    
    # Add the new admin if not already an admin
    if new_admin_id not in admins:
        admins[new_admin_id] = ["1"]
        write_file(ADMINS_FILE, admins)
        bot.send_message(user_id, f"User {new_admin_id} is now an admin.")
        log_action(f"Admin {user_id} added {new_admin_id} as an admin.")
    else:
        bot.send_message(user_id, f"User {new_admin_id} is already an admin.")

# Create Redeem Code Command
@bot.message_handler(commands=['createredeem'])
def create_redeem_command(message):
    user_id = str(message.from_user.id)
    admins = read_file(ADMINS_FILE)
    
    # Check if the user is an admin
    if user_id not in admins:
        bot.send_message(user_id, "You are not authorized to create redeem codes.")
        return
    
    # Check if the redeem code and credits are provided
    args = message.text.split()
    if len(args) < 3:
        bot.send_message(user_id, "Usage: /createredeem [code] [credits]")
        return
    
    code = args[1]
    credits = args[2]
    redeem_codes = read_file(REDEEM_FILE)
    
    # Add the redeem code if not already created
    if code in redeem_codes:
        bot.send_message(user_id, f"Redeem code {code} already exists.")
        return
    
    redeem_codes[code] = [credits]
    write_file(REDEEM_FILE, redeem_codes)
    bot.send_message(user_id, f"Redeem code {code} created with {credits} credits.")
    log_action(f"Admin {user_id} created redeem code {code} with {credits} credits.")

# Run bot
bot.polling(none_stop=True)
