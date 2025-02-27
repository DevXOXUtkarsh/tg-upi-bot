import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot API Tokens
BOT_TOKEN = "7812777086:AAH3Va5ltPjqllVFmIt34-c24ZDLn1ercsE"
UPI_BOT_API = "7507509892:AAHhq_NBNxjMlFIrF5D7d7wYEb7nRSn8cz0"

# Chat ID where admin gets withdrawal requests
ADMIN_CHAT_ID = 7553947992  

# Channel List (Replace with your channel usernames)
CHANNELS = ["net_hacks77", "@channel2", "@channel3", "@channel4"]

# User data storage
users = {}

bot = telebot.TeleBot(BOT_TOKEN)

# Function to check if a user joined all channels
def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# Start Command
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.chat.id
    if user_id not in users:
        users[user_id] = {"balance": 1, "referrals": 0, "upi": None}

    if check_subscription(user_id):
        send_main_menu(user_id)
    else:
        send_subscription_menu(user_id)

# Subscription Menu
def send_subscription_menu(user_id):
    markup = InlineKeyboardMarkup()
    
    # Add JOIN buttons for all channels
    for channel in CHANNELS:
        markup.add(InlineKeyboardButton("✅ JOIN", url=f"https://t.me/{channel.replace('@', '')}"))
    
    # Add VERIFY button
    markup.add(InlineKeyboardButton("✔ VERIFY", callback_data="verify"))
    
    bot.send_message(user_id, "🔹 *Join all channels to continue!*\nThen press 'VERIFY'.", parse_mode="Markdown", reply_markup=markup)

# Verification Handler
@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify(call):
    user_id = call.message.chat.id
    if check_subscription(user_id):
        bot.send_message(user_id, "✅ *Verification successful!*")
        send_main_menu(user_id)
    else:
        bot.answer_callback_query(call.id, "❌ Join all channels first!")

# Main Menu
def send_main_menu(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💰 Bonus", callback_data="bonus"),
               InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"))
    markup.add(InlineKeyboardButton("📤 Refer & Earn", callback_data="refer"))
    
    bot.send_message(user_id, "🎉 Welcome! Choose an option:", reply_markup=markup)

# Button Handlers
@bot.callback_query_handler(func=lambda call: True)
def menu_handler(call):
    user_id = call.message.chat.id

    if call.data == "bonus":
        bot.answer_callback_query(call.id, f"🎁 Your balance: ₹{users[user_id]['balance']}")
    
    elif call.data == "withdraw":
        if users[user_id]["balance"] < 30:
            bot.answer_callback_query(call.id, "❌ Not enough balance (Min ₹30)")
        else:
            ask_withdraw_details(user_id)
    
    elif call.data == "refer":
        refer_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        bot.send_message(user_id, f"🔗 Your referral link:\n{refer_link}")

# Ask for Withdrawal Details
def ask_withdraw_details(user_id):
    msg = bot.send_message(user_id, "🔹 Enter your *UPI ID*:")
    bot.register_next_step_handler(msg, get_upi, user_id)

def get_upi(message, user_id):
    upi_id = message.text
    users[user_id]["upi"] = upi_id
    msg = bot.send_message(user_id, "🔹 Enter your *Full Name*:")
    bot.register_next_step_handler(msg, get_name, user_id)

def get_name(message, user_id):
    name = message.text
    amount = users[user_id]["balance"]
    
    # Send withdrawal request to admin bot
    bot.send_message(ADMIN_CHAT_ID, f"🔔 *New Withdrawal Request:*\n👤 Name: {name}\n💳 UPI: {users[user_id]['upi']}\n💰 Amount: ₹{amount}\n🆔 User ID: {user_id}", parse_mode="Markdown")

    bot.send_message(user_id, "✅ Your withdrawal request has been sent to the admin!")

# Referral System
@bot.message_handler(func=lambda msg: msg.text.startswith("/start "))
def handle_referral(message):
    referrer_id = message.text.split(" ")[1]
    user_id = message.chat.id

    if user_id not in users:
        users[user_id] = {"balance": 1, "referrals": 0, "upi": None}
    
    if referrer_id.isdigit():
        referrer_id = int(referrer_id)
        if referrer_id in users and referrer_id != user_id:
            users[referrer_id]["balance"] += 1
            users[referrer_id]["referrals"] += 1
            bot.send_message(referrer_id, "🎉 You got ₹1 for a successful referral!")

    send_main_menu(user_id)

# Broadcast Admin Messages
@bot.message_handler(func=lambda message: message.chat.id == ADMIN_CHAT_ID)
def broadcast_message(message):
    for user_id in users:
        bot.forward_message(user_id, ADMIN_CHAT_ID, message.message_id)

# Run the bot
bot.polling()
