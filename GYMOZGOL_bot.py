from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# اطلاعات اولیه
ADMIN_PASSWORD = "1018"
admins = set()  # مدیران
coaches = set()  # مربیان
athletes = set()  # ورزشکاران
absences = {}  # غیبت‌ها

# وضعیت‌ها برای ConversationHandler
(
    WAITING_FOR_ADMIN_PASSWORD,
    WAITING_FOR_COACH_NAME,
    WAITING_FOR_ATHLETE_NAME,
) = range(3)

# شروع ربات
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "به ربات باشگاه خوش آمدید!\n"
        "برای ورود به پنل مدیریت، دستور /admin را وارد کنید.\n"
        "برای اعلام غیبت، دستور /absence را وارد کنید."
    )

# ورود به پنل مدیریت
def admin_panel(update: Update, context: CallbackContext):
    update.message.reply_text("لطفاً رمز عبور مدیریت را وارد کنید:")
    return WAITING_FOR_ADMIN_PASSWORD

def check_admin_password(update: Update, context: CallbackContext):
    if update.message.text == ADMIN_PASSWORD:
        admins.add(update.effective_user.id)
        update.message.reply_text("به پنل مدیریت خوش آمدید!", reply_markup=admin_menu())
        return ConversationHandler.END
    else:
        update.message.reply_text("رمز اشتباه است. دوباره تلاش کنید.")
        return WAITING_FOR_ADMIN_PASSWORD

def admin_menu():
    keyboard = [
        [InlineKeyboardButton("ثبت مربی", callback_data="register_coach")],
        [InlineKeyboardButton("ثبت ورزشکار", callback_data="register_athlete")],
    ]
    return InlineKeyboardMarkup(keyboard)

def handle_admin_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "register_coach":
        query.edit_message_text("لطفاً نام مربی را وارد کنید:")
        return WAITING_FOR_COACH_NAME
    elif query.data == "register_athlete":
        query.edit_message_text("لطفاً نام ورزشکار را وارد کنید:")
        return WAITING_FOR_ATHLETE_NAME

def register_coach(update: Update, context: CallbackContext):
    coach_name = update.message.text
    coaches.add(coach_name)
    update.message.reply_text(f"مربی {coach_name} با موفقیت ثبت شد!")
    return ConversationHandler.END

def register_athlete(update: Update, context: CallbackContext):
    athlete_name = update.message.text
    athletes.add(athlete_name)
    update.message.reply_text(f"ورزشکار {athlete_name} با موفقیت ثبت شد!")
    return ConversationHandler.END

# اعلام غیبت
def absence(update: Update, context: CallbackContext):
    if update.effective_user.id not in athletes:
        update.message.reply_text("شما به عنوان ورزشکار ثبت نشده‌اید. لطفاً با ادمین تماس بگیرید.")
        return

    keyboard = [
        [InlineKeyboardButton("امروز غیبت دارم", callback_data="absent_today")],
    ]
    update.message.reply_text("لطفاً یکی از گزینه‌ها را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))

def handle_absence(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "absent_today":
        absences[update.effective_user.id] = "امروز"
        query.edit_message_text("غیبت شما ثبت شد و به مربی اطلاع داده خواهد شد.")
        notify_coaches(update.effective_user.id)

def notify_coaches(athlete_id):
    for coach in coaches:
        context.bot.send_message(
            chat_id=coach,
            text=f"ورزشکار {athlete_id} امروز غیبت دارد."
        )

def main():
    updater = Updater("7628739336:AAFXQwMM0J_CfOJf5zQNoG7d5YpzhMNjtak")  # جایگزین کردن توکن ربات با توکن صحیح

    dp = updater.dispatcher

    # دستورهای عمومی
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", admin_panel))

    # مدیریت پنل (ConversationHandler برای مدیریت وضعیت‌ها)
    admin_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_panel)],
        states={
            WAITING_FOR_ADMIN_PASSWORD: [MessageHandler(Filters.text & ~Filters.command, check_admin_password)],
            WAITING_FOR_COACH_NAME: [MessageHandler(Filters.text & ~Filters.command, register_coach)],
            WAITING_FOR_ATHLETE_NAME: [MessageHandler(Filters.text & ~Filters.command, register_athlete)],
        },
        fallbacks=[],
    )
    dp.add_handler(admin_conversation_handler)

    # اعلام غیبت
    dp.add_handler(CommandHandler("absence", absence))
    dp.add_handler(CallbackQueryHandler(handle_absence))

    # اجرا
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
