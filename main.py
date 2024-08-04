import flet as ft
from win10toast import ToastNotifier
import jdatetime
import datetime
import threading




reminders = []


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

def main(page: ft.Page):
    page.title = "Reminder"
    page.window_height = 460
    page.window_width = 350
    page.window_resizable = False
    page.window_maximizable = False

    def update_countdown():
        now = datetime.datetime.now()
        for control in reminder_list.controls:
            if isinstance(control, ft.Row) and len(control.controls) == 2:
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
                    ft.Text(reminder_text, color="gray", decoration=ft.TextDecoration.LINE_THROUGH),
                    ft.Text("Past", color="gray")
                ])
            else:
                reminder_row = ft.Row([
                    ft.Text(reminder_text),
                    ft.Text("", color="blue")
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

                date_input.value = ""
                message_input.value = ""
                page.update()
            else:
                raise ValueError
        except ValueError:
            show_snackbar("Please use this format: YYYY-MM-DD", ft.colors.RED)

    date_input = ft.TextField(label="(YYYY-MM-DD)", hint_text="1403-12-05")
    message_input = ft.TextField(label="Your Message")
    btn_submit = ft.ElevatedButton(text="Save", on_click=lambda _: set_reminder(date_input.value, message_input.value))
    reminder_list = ft.Column()

    page.add(date_input, message_input, btn_submit, reminder_list)
    page.update()

    update_countdown()

ft.app(target=main)