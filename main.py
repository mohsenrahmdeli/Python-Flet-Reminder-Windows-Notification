import flet as ft
from win10toast import ToastNotifier
import jdatetime
import datetime
import threading
import json
import os




reminders = []
data_file = "reminders.json"


def save_reminders():
    with open(data_file, 'w') as f:
        json.dump(reminders, f)


def load_reminders():
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    return []


def show_notification(message, date, reminder_id):
    now = datetime.datetime.now()
    reminder_date = jdatetime.datetime(*date).togregorian()

    while now < reminder_date:
        now = datetime.datetime.now()

    toaster = ToastNotifier()
    toaster.show_toast("Reminder", message, duration=7)


    for reminder in reminders:
        if reminder["id"] == reminder_id:
            reminder["notified"] = True
            break
    save_reminders()

def main(page: ft.Page):
    page.title = "Reminder"
    page.window_height = 400
    page.window_width = 550
    page.window_resizable = False
    page.window_maximizable = False

    def update_countdown():
        now = datetime.datetime.now()
        for control in reminder_list.controls:
            if isinstance(control, ft.Row) and len(control.controls) == 4:
                reminder_date_str = control.controls[0].value.split(" - ")[0]
                reminder_date_parts = list(map(int, reminder_date_str.split('-')))
                reminder_date = jdatetime.datetime(*reminder_date_parts).togregorian()

                if now < reminder_date:
                    time_left = reminder_date - now
                    days, seconds = time_left.days, time_left.seconds
                    hours = seconds // 3600
                    minutes = (seconds % 3600) // 60
                    seconds = seconds % 60
                    countdown_text = f"{days}d {hours}h {minutes}m {seconds}s"
                    control.controls[1].value = countdown_text
                else:
                    control.controls[1].value = "Past"
        
        page.update()
        threading.Timer(1, update_countdown).start()

    def update_reminder_list():
        reminder_list.controls.clear()
        now = datetime.datetime.now()

        for reminder in reminders:
            reminder_date = jdatetime.datetime(*reminder["date"]).togregorian()
            reminder_text = f"{reminder['date'][0]}-{reminder['date'][1]:02d}-{reminder['date'][2]:02d} - {reminder['message']}"

            if now > reminder_date:
                reminder_text = f"{reminder_text} (Past)"
                reminder_row = ft.Row([
                    ft.Text(reminder_text, color="gray", style="text-decoration: line-through;"),
                    ft.Text("Past", color="gray"),
                    ft.ElevatedButton(text="Edit", on_click=lambda e, id=reminder["id"]: edit_reminder(id)),
                    ft.ElevatedButton(text="Delete", on_click=lambda e, id=reminder["id"]: delete_reminder(id)),
                ])
            else:
                reminder_row = ft.Row([
                    ft.Text(reminder_text),
                    ft.Text("", color="blue"),
                    ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, id=reminder["id"]: edit_reminder(id)),
                    ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, id=reminder["id"]: delete_reminder(id)),
                ])

            reminder_list.controls.append(reminder_row)

        page.update()

    def show_snackbar(message, color):
        snackbar = ft.SnackBar(ft.Text(message), bgcolor=color)
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()

    def set_reminder(date_str, message):
        try:
            date_parts = list(map(int, date_str.split('-')))
            if len(date_parts) == 3:
                reminder_id = len(reminders) + 1
                reminders.append({"id": reminder_id, "date": date_parts, "message": message, "notified": False})
                reminder_thread = threading.Thread(target=show_notification, args=(message, date_parts, reminder_id))
                reminder_thread.start()

                show_snackbar("Data Saved!", ft.colors.GREEN)


                update_reminder_list()
                save_reminders()


                date_input.value = ""
                message_input.value = ""
                page.update()
            else:
                raise ValueError
        except ValueError:
            show_snackbar("Wrong Format. Please use: YYYY-MM-DD", ft.colors.RED)

    def edit_reminder(reminder_id):
        for reminder in reminders:
            if reminder["id"] == reminder_id:
                date_input.value = f"{reminder['date'][0]}-{reminder['date'][1]:02d}-{reminder['date'][2]:02d}"
                message_input.value = reminder["message"]
                reminders.remove(reminder)
                save_reminders()
                update_reminder_list()
                break

    def delete_reminder(reminder_id):
        global reminders
        reminders = [r for r in reminders if r["id"] != reminder_id]
        save_reminders()
        update_reminder_list()


    global reminders
    reminders = load_reminders()
    

    date_input = ft.TextField(label="Date (YYYY-MM-DD)", hint_text="1403-12-05")
    message_input = ft.TextField(label="Your Message")
    btn_submit = ft.ElevatedButton(text="Save", on_click=lambda _: set_reminder(date_input.value, message_input.value))
    reminder_list = ft.ListView(expand=True)

    page.add(date_input, message_input, btn_submit, reminder_list)
    page.update()


    update_countdown()


    update_reminder_list()

ft.app(target=main)
