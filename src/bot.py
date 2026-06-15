import  os
from datetime import datetime, time, timedelta
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application,CommandHandler, MessageHandler, filters, ContextTypes
USER_TASKS = {}
USER_NOTES = {}

# check for duplicates in notes/tasks

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
            header_lower = header.lower()
            if body_text not in notes.values() and header_lower not in notes:
                notes[header_lower] = body_text
                await update.message.reply_text(f"saved note under *{header.capitalize()}*", parse_mode="Markdown")
            else:
                if header_lower in notes:
                    await update.message.reply_text(f"A note with *{header.capitalize()}* already exists")
                else:
                    await update.message.reply_text(f"Note already *EXISTS* with this exact text")
            
            
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
            if task_text not in tasks:
                tasks.append(task_text)
                tasks.sort()
                await update.message.reply_text(f"Added: \"{task_text}\"")
            else:
                await update.message.reply_text(f"Task:\"{task_text}\" already exists!")
            
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
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        load_dotenv()
        TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("BOT_TOKEN not found in system environment or .env file")
    app = Application.builder().token(TOKEN).post_init(check_bot_identity).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("help",help))
    app.add_handler(CommandHandler("note",note_manage))
    app.add_handler(CommandHandler("task",task_command))
    app.add_handler(CommandHandler("remind", remind_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_message))

    app.run_polling()

async def smart_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    text = update.message.text.strip()

    tasks = USER_TASKS.setdefault(chat_id, [])
    notes = USER_NOTES.setdefault(chat_id, {})

    lower_text = text.lower()

    # ===== TASKS =====

    if lower_text.startswith("task "):
        task_text = text[5:].strip()

        if task_text:
            if task_text not in tasks:
                tasks.append(task_text)
                tasks.sort()
                await update.message.reply_text(
                    f"✅ Task added:\n{task_text}"
                )
            else:
                await update.message.reply_text(
                    "⚠️ Task already exists."
                )
        return

    if lower_text == "show tasks":
        if not tasks:
            await update.message.reply_text(
                "Your task list is empty."
            )
            return

        message_lines = ["📋 Tasks"]

        for i, task in enumerate(tasks, start=1):
            message_lines.append(f"{i}. {task}")

        await update.message.reply_text(
            "\n".join(message_lines)
        )
        return

    # ===== NOTES =====

    if lower_text.startswith("note "):
        note_text = text[5:].strip()

        note_id = f"note{len(notes)+1}"

        notes[note_id] = note_text

        await update.message.reply_text(
            f"📝 Note saved:\n{note_text}"
        )
        return

    if lower_text == "show notes":
        if not notes:
            await update.message.reply_text(
                "No notes found."
            )
            return

        message_lines = ["📝 Notes"]

        for header, body in notes.items():
            message_lines.append(
                f"\n{header}\n{body}"
            )

        await update.message.reply_text(
            "\n".join(message_lines)
        )
        return

    # ===== SEARCH NOTES =====

    if lower_text.startswith("search "):
        query = lower_text.replace("search ", "")

        found = []

        for header, body in notes.items():
            if query in header.lower() or query in body.lower():
                found.append(f"{header}\n{body}")

        if found:
            await update.message.reply_text(
                "\n\n".join(found)
            )
        else:
            await update.message.reply_text(
                "No matching notes found."
            )

        return

    # ===== STATS =====

    if lower_text == "stats":
        await update.message.reply_text(
            f"📊 Statistics\n\n"
            f"Tasks: {len(tasks)}\n"
            f"Notes: {len(notes)}"
        )
        return

    # ===== MORNING =====

    if lower_text == "morning":
        lines = [
            "☀️ Good Morning",
            "",
            f"Tasks: {len(tasks)}",
            f"Notes: {len(notes)}",
            ""
        ]

        if tasks:
            lines.append("Today's Tasks:")

            for i, task in enumerate(tasks[:5], start=1):
                lines.append(f"{i}. {task}")

        await update.message.reply_text(
            "\n".join(lines)
        )
        return

    # ===== HELP =====

    if lower_text == "help":
        await update.message.reply_text(
        )
        return

    # ===== FALLBACK =====

    await update.message.reply_text(
        "❓ I didn't understand.\nType 'help' to see available commands."
    )

if __name__ == "__main__":
    main()