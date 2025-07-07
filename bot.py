import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

CARD_NUMBER = "1234-5678-9012-3456"
SUPPORT_ID = "@YourSupportID"

ACCOUNTS_FILE = os.path.join(os.path.dirname(__file__), "accounts.txt")

if os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        accounts = f.read().splitlines()
else:
    accounts = []

waiting_for_confirmation = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام!\nبرای خرید اکانت شماره کارت را دریافت کنید با دستور /card\n"
        "بعد از واریز بنویسید 'پرداخت کردم' تا اکانت برایتان ارسال شود."
    )

async def card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"شماره کارت برای واریز:\n{CARD_NUMBER}\n\n"
        "بعد از واریز بنویسید: پرداخت کردم"
    )

async def payment_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    waiting_for_confirmation[user_id] = True
    await update.message.reply_text(
        "پرداخت شما در حال بررسی است. پس از تایید، اکانت به شما ارسال خواهد شد."
    )

async def approve_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("لطفا آیدی کاربر را وارد کنید:\n/approve <user_id>")
        return

    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("آیدی کاربر باید عدد باشد.")
        return

    if user_id in waiting_for_confirmation:
        if accounts:
            account = accounts.pop(0)
            with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(accounts))

            await context.bot.send_message(
                chat_id=user_id,
                text=f"اکانت شما:\n{account}\n\nدر صورت نیاز با پشتیبانی در تماس باشید: {SUPPORT_ID}"
            )

            del waiting_for_confirmation[user_id]
            await update.message.reply_text(f"پرداخت کاربر {user_id} تایید و اکانت ارسال شد.")
        else:
            await update.message.reply_text("اکانت موجود نیست.")
    else:
        await update.message.reply_text("این کاربر در انتظار تایید پرداخت نیست.")

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("❌ BOT_TOKEN environment variable not set.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("card", card))
    app.add_handler(MessageHandler(filters.Regex("پرداخت کردم"), payment_confirm))
    app.add_handler(CommandHandler("approve", approve_payment))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
