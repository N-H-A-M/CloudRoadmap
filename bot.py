import logging, os
from datetime import datetime, time, timedelta
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application,CommandHandler, MessageHandler, filters, ContextTypes
USER_TASKS = {}
USER_NOTES = {} 
logging.basicConfig(
    filename="bot.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts bot"""
    await update.message.reply_text(" bot is online., \n choose from the following" \
    "\n /remind, /note, /task, /help")
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("this bot has the following function\n /note - note taking implementation,"\
"\n /remind - a reminder implementation takes HH:MM and a event\n /task - for task managing /task returns the list of tasks, add appends the list of tasks,\n done finishes the task and remove it")
async def note_manage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    message = context.args
    notes = USER_NOTES.setdefault(chat_id,{})
    match message:
        case[]:
            if not notes:
                await update.message.reply_text("no notes to read")
                return
            message_lines = ["*Notes:*"]
            for header, body in notes.items():
                message_lines.append(f"*{header.capitalize()}*\n{body}\n" + "-"*20)
            message_lines.append("\n to remove a note please write delete <number>")
            await update.message.reply_text("\n".join(message_lines), parse_mode="Markdown")
        case["add",header,*body_words] if body_words:
            body_text = " ".join(body_words)
            notes[header.lower()] = body_text
            await update.message.reply_text(f"saved note under *{header}*", parse_mode="Markdown")
        case["add", _] | ["add"]:
            await update.message.reply_text("Format: `/note add <header> <your text>`\n"
                "Example: `/note add dentist appointment at 15:25`", 
                parse_mode="Markdown")
        case["delete",header]:
            header_lower = header.lower()
            if header_lower in notes:
                del notes[header_lower]
                await update.message.reply_text(f"Deleted: *{header}*", parse_mode="Markdown")
            else:
                await update.message.reply_text(f"Could not find a note named '{header}'.")
        case _:
            await update.message.reply_text("Unkown command! Use 'add' , 'delete'",parse_mode="Markdown")


    return
async def check_bot_identity(application: Application):
    bot_info = await application.bot.get_me()
    print("\n" + "="*40)
    print(f"BOT IS ALIVE!")
    print(f"Name: {bot_info.first_name}")
    print(f"Username: @{bot_info.username}")
    print("="*40 + "\n")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """tests text invoice and echos them"""
    text_received = update.message.text
    await update.message.reply_text(f"You said: {text_received}")

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id,
    text=f"REMINDER: {job.data}")

async def remind_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /remind <HH:MM> <text>\nExample: /remind 15:45 Walk the dog")
        return
    time_input = context.args[0]
    reminder_text = " ".join(context.args[1:])
    try: 
        target_time = datetime.strptime(time_input, "%H:%M").time()
        now = datetime.now()
        target_datetime = datetime.combine(now.date(), target_time)
        if target_datetime < now:
            target_datetime += timedelta(days=1)
        time_difference = (target_datetime - now).total_seconds()
        context.job_queue.run_once(
            send_reminder, 
            when=time_difference, 
            chat_id=chat_id, 
            data=reminder_text
        )
        await update.message.reply_text(f"Dynamic reminder set for {time_input}")
    except ValueError:
        await update.message.reply_text("invalid time format")

async def task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    tasks = USER_TASKS.setdefault(chat_id,[])
    match context.args:
        case []:
            if not tasks:
                await update.message.reply_text("your task list is empty.")
                return
            message_lines = ["*Tasks:*"] + [f"{i}. {item}" for i, item in enumerate(tasks, start=1)]
            message_lines.append("\nTo finish a task, type: `/task done <number>`")
            await update.message.reply_text("\n".join(message_lines), parse_mode="Markdown")

        case ["add", *task_words] if task_words:
            task_text = " ".join(task_words)
            tasks.append(task_text)
            await update.message.reply_text(f"Added: \"{task_text}\"")
        case ["add"]:
            await update.message.reply_text("please specify what task to add!\n", parse_mode="Markdown")
        case ["done", index_str] if index_str.isdigit():
            idx = int(index_str) - 1
            if 0 <= idx < len(tasks):
                removed = tasks.pop(idx)
                await update.message.reply_text(f"removed: \"{removed}\"")
            else:
                await update.message.reply_text("Invalid task number")
        case _:
            await update.message.reply_text("Unkown command! Use 'add' , 'done'",parse_mode="Markdown")



def main():
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    app = Application.builder().token(TOKEN).post_init(check_bot_identity).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("help",help))
    app.add_handler(CommandHandler("note",note_manage))
    app.add_handler(CommandHandler("task",task_command))
    app.add_handler(CommandHandler("remind", remind_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_polling()

if __name__ == "__main__":
    main()