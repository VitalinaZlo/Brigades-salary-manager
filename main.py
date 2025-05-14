from datetime import datetime, timedelta
import calendar
import json
import os

from tkinter import ttk, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

import pyperclip
import psycopg2
import ctypes

import config

class DatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title(config.APP_TITLE)
        self.root.geometry(config.WINDOW_SIZE)
        self.root.iconbitmap(config.LOGO)

        # Устанавливаем тему и цветовую схему
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("green")

        try:
            self.conn = psycopg2.connect(
                dbname=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                host=config.DB_HOST,
                port=config.DB_PORT,
                options=config.DB_OPTIONS
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к БД: {e}")
            self.root.destroy()
            return

        # Переменная для хранения текущего пользователя
        self.current_user = None
        self.current_user_id = None
        self.current_user_role = None

        # Переменные для хранения последнего логина и пароля
        self.last_login = None
        self.last_password = None
        self.load_last_login()

        # Показываем форму входа
        self.show_login_page()

    def load_last_login(self):
        """Загружает последний логин и пароль из файла."""
        try:
            if os.path.exists(config.LOGIN_FILE_PATH):
                with open(config.LOGIN_FILE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.last_login = data.get("last_login", "")
                    self.last_password = data.get("last_password", "")
            else:
                # Если файла нет, создаём его с пустыми значениями
                os.makedirs(os.path.dirname(config.LOGIN_FILE_PATH), exist_ok=True)
                with open(config.LOGIN_FILE_PATH, "w", encoding="utf-8") as f:
                    json.dump({"last_login": "", "last_password": ""}, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showwarning("Предупреждение", f"Не удалось загрузить данные последнего входа: {e}")
            self.last_login = ""
            self.last_password = ""

    def save_last_login(self, login, password):
        """Сохраняет логин и пароль в файл."""
        try:
            with open(config.LOGIN_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump({"last_login": login, "last_password": password}, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showwarning("Предупреждение", f"Не удалось сохранить данные последнего входа: {e}")

    def show_login_page(self):
        self.load_last_login()

        # Очищаем окно
        for widget in self.root.winfo_children():
            widget.destroy()

        # Устанавливаем фон с изображением
        bg_image = Image.open(config.BACKGROUND_LOGIN_IMAGE)
        bg_image = bg_image.resize((1200, 610), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = ctk.CTkLabel(self.root, image=self.bg_photo, text="")
        bg_label.place(relwidth=1, relheight=1)

        # Название приложения над формой
        ctk.CTkLabel(
            self.root,
            text=config.APP_TITLE,
            font=config.APP_TITLE_FONT,
            fg_color=config.HIGHLIGHT_COLOR,
            text_color="white",
            wraplength=800,
            justify="center"
        ).place(relx=0.5, rely=0.125, anchor="center")

        # Создаём фрейм для формы входа
        login_frame = ctk.CTkFrame(
            self.root,
            fg_color=config.BG_COLOR,
            bg_color=config.BUTTON_COLOR,
            border_color=config.BORDER_COLOR,
            border_width=config.BORDER_WIDTH
        )
        login_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.25, relheight=0.53)

        # Внутренний фрейм для содержимого
        content_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
        content_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Заголовок формы
        ctk.CTkLabel(
            content_frame,
            text=config.LOGIN_PAGE_TITLE,
            font=config.LOGIN_TITLE_FONT,
            text_color=config.TEXT_COLOR
        ).pack(pady=(10, 20))

        # Поле для логина
        login_frame_inner = ctk.CTkFrame(content_frame, fg_color=config.BG_COLOR)
        login_frame_inner.pack(anchor="w", padx=30, pady=(0, 2))
        ctk.CTkLabel(
            login_frame_inner,
            text="Логин:",
            font=config.LABEL_FONT,
            text_color=config.TEXT_COLOR,
            anchor="w"
        ).pack()
        self.login_entry = ctk.CTkEntry(content_frame, width=config.ENTRY_WIDTH, height=config.ENTRY_HEIGHT, font=config.LABEL_FONT)
        self.login_entry.pack(pady=(0, 10))

        if self.last_login:
            self.login_entry.delete(0, "end")
            self.login_entry.insert(0, self.last_login)

        self.login_entry.bind("<Control-KeyPress>", self.keys)

        # Поле для пароля
        password_frame_inner = ctk.CTkFrame(content_frame, fg_color=config.BG_COLOR)
        password_frame_inner.pack(anchor="w", padx=30, pady=(0, 2))
        ctk.CTkLabel(
            password_frame_inner,
            text="Пароль:",
            font=config.LABEL_FONT,
            text_color=config.TEXT_COLOR,
            anchor="w"
        ).pack()
        self.password_entry = ctk.CTkEntry(content_frame, width=config.ENTRY_WIDTH, height=config.ENTRY_HEIGHT, font=config.LABEL_FONT, show="*")
        self.password_entry.pack(pady=(0, 10))

        if self.last_password:
            self.password_entry.delete(0, "end")
            self.password_entry.insert(0, self.last_password)

        self.password_entry.bind("<Control-KeyPress>", self.keys)

        # Кнопка входа
        ctk.CTkButton(
            content_frame,
            text="Войти",
            command=self.validate_login,
            width=100,
            height=config.BUTTON_HEIGHT,
            fg_color=config.BUTTON_COLOR,
            hover_color=config.BUTTON_HOVER_COLOR,
            corner_radius=config.CORNER_RADIUS,
            font=config.BUTTON_FONT
        ).pack(pady=10)

        # Надпись "Забыли пароль?"
        ctk.CTkLabel(
            content_frame,
            text=config.FORGOT_PASSWORD_MESSAGE,
            font=config.SUBTITLE_FONT,
            text_color=config.SECONDARY_TEXT_COLOR,
            wraplength=config.ENTRY_WIDTH,
            justify="left",
            anchor="w"
        ).pack(pady=(5, 10), padx=20, anchor="w")

    def validate_login(self):
        login = self.login_entry.get()
        password = self.password_entry.get()

        if not login or not password:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        try:
            self.cursor.execute(
                "SELECT Full_Name, Role, ID_Employee FROM Users WHERE Login = %s AND Password = %s",
                (login, password)
            )
            user = self.cursor.fetchone()
            if user:
                self.current_user, self.current_user_role, self.current_user_id = user
                self.current_user = self.current_user.split()[1] if len(self.current_user.split()) > 1 else self.current_user
                if self.current_user_role == "Сотрудник" and self.current_user_id is None:
                    messagebox.showerror("Ошибка", "ID_Employee не указан для пользователя с ролью Сотрудник!")
                    return
                # Сохраняем логин и пароль, если они отличаются от последнего сохранённого
                if self.last_login != login:
                    self.save_last_login(login, password)
                self.setup_main_interface()
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при входе: {e}")

    def is_ru_lang_keyboard(self):
        u = ctypes.windll.LoadLibrary("user32.dll")
        pf = getattr(u, "GetKeyboardLayout")
        return hex(pf(0)) == '0x4190419'

    def keys(self, event):
        if hasattr(event.widget, "event_generate"):
            if self.is_ru_lang_keyboard():
                if event.keycode == 86:  # Ctrl+V
                    event.widget.event_generate("<<Paste>>")
                elif event.keycode == 67:  # Ctrl+C
                    event.widget.event_generate("<<Copy>>")
                elif event.keycode == 88:  # Ctrl+X
                    event.widget.event_generate("<<Cut>>")
                elif event.keycode == 65535:  # Ctrl+Delete
                    event.widget.event_generate("<<Clear>>")
                elif event.keycode == 65:  # Ctrl+A
                    event.widget.event_generate("<<SelectAll>>")
                return "break"

    def setup_main_interface(self):
        # Очищаем окно
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(fg_color=config.BG_COLOR)

        # Боковая панель (sidebar)
        self.sidebar = ctk.CTkFrame(self.root, width=config.SIDEBAR_WIDTH, fg_color=config.SIDEBAR_COLOR, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)

        # Заголовок боковой панели
        ctk.CTkLabel(self.sidebar, text=config.SIDEBAR_TITLE, font=config.TITLE_FONT).pack(pady=(20, 10))

        # Список для отслеживания кнопок
        self.sidebar_buttons = {}

        # Определяем доступные таблицы в зависимости от роли
        tables = [
            ("Главная", self.show_home_page),
            ("Сотрудники", self.show_employees_tab),
            ("Должности", self.show_positions_tab),
            ("Рейсы", self.show_trips_tab),
            ("Состав бригады", self.show_brigade_composition_tab),
            ("Календарь смен", self.show_shift_calendar_tab),
            ("Учёт зарплаты", self.show_payroll_accounting_tab)
        ]

        # Ограничения по ролям
        if self.current_user_role in config.ROLE_ACCESS:
            allowed_tables = config.ROLE_ACCESS[self.current_user_role]
            tables = [(name, cmd) for name, cmd in tables if name in allowed_tables]

        # Кнопки для боковой панели
        for name, command in tables:
            btn = ctk.CTkButton(
                self.sidebar,
                text=name,
                command=lambda cmd=command, btn_name=name: self.on_button_click(cmd, btn_name),
                width=config.BUTTON_WIDTH,
                height=config.BUTTON_HEIGHT,
                fg_color=config.BUTTON_COLOR,
                hover_color=config.BUTTON_HOVER_COLOR,
                corner_radius=config.CORNER_RADIUS,
                font=config.BUTTON_FONT
            )
            btn.pack(pady=5, padx=10)
            self.sidebar_buttons[name] = btn

        # Основной фрейм для содержимого
        self.main_content_frame = ctk.CTkFrame(self.root, fg_color=config.BG_COLOR)
        self.main_content_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Переменная для отслеживания активной кнопки
        self.active_button = None

        # Отображаем домашнюю страницу по умолчанию
        self.show_home_page()

        # Устанавливаем кнопку "Главная" в активное состояние
        self.on_button_click(self.show_home_page, "Главная")

    def on_button_click(self, command, button_name):
        if self.active_button:
            self.sidebar_buttons[self.active_button].configure(
                fg_color=config.BUTTON_COLOR,
                hover_color=config.BUTTON_HOVER_COLOR,
                text_color="white"
            )
        
        self.sidebar_buttons[button_name].configure(
            fg_color="white",
            hover_color="white",
            text_color=config.TEXT_COLOR,
            border_color=config.BORDER_COLOR,
            border_width=config.BORDER_WIDTH
        )
        
        self.active_button = button_name
        command()

    def show_home_page(self):
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

        home_frame = ctk.CTkFrame(self.main_content_frame, fg_color=config.BG_COLOR)
        home_frame.pack(expand=True, fill="both")

        # Приветственное сообщение
        welcome_label_top = ctk.CTkLabel(
            home_frame,
            text=config.WELCOME_MESSAGE.format(self.current_user),
            font=config.WELCOME_FONT,
            text_color=config.TEXT_COLOR,
            anchor="w"
        )
        welcome_label_top.pack(anchor="nw", padx=10, pady=10)

        # Логотип
        image = Image.open(config.TRAIN_LOGO_IMAGE)
        image = image.resize(config.LOGO_SIZE, Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        logo_label = ctk.CTkLabel(home_frame, image=photo, text="")
        logo_label.image = photo
        logo_label.pack(pady=(0, 0))

        # Сообщение
        welcome_label = ctk.CTkLabel(
            home_frame,
            text=config.HOME_PAGE_MESSAGE,
            font=config.HOME_MESSAGE_FONT,
            wraplength=600,
            justify="center"
        )
        welcome_label.pack(pady=(20, 0))

        # Кнопка "Выйти из аккаунта"
        logout_button = ctk.CTkButton(
            home_frame,
            text="Выйти из аккаунта",
            command=self.show_login_page,
            width=150,
            height=config.BUTTON_HEIGHT,
            fg_color=config.BUTTON_COLOR,
            hover_color=config.BUTTON_HOVER_COLOR,
            corner_radius=config.CORNER_RADIUS,
            font=config.BUTTON_FONT
        )
        logout_button.pack(anchor="se", expand=True, padx=10, pady=10)

    def load_icon(self, icon_path, size=config.ICON_SIZE):
        try:
            image = Image.open(icon_path)
            image = image.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить иконку {icon_path}: {e}")
            return None

    def create_icon_label(self, parent, icon_path):
        photo = self.load_icon(icon_path)
        if photo:
            label = ctk.CTkLabel(parent, image=photo, text="", fg_color="white")
            label.image = photo
            label.pack(side="left", padx=1)
        return label
    
    def get_employees(self):
        try:
            self.conn.rollback()
            self.cursor.execute("SELECT Full_Name || ' (' || ID_Employee || ')' AS Full_Name, ID_Employee FROM Employees ORDER BY Full_Name")
            employees = [(row[0].strip(), row[1]) for row in self.cursor.fetchall()]
            return employees
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить сотрудников: {e}")
            return []

    def get_trips(self):
        try:
            self.conn.rollback()
            self.cursor.execute("SELECT Trip_Name || ' (' || ID_Trip || ')' AS Trip_Name, ID_Trip FROM Trips ORDER BY Trip_Name")
            trips = [(row[0].strip(), row[1]) for row in self.cursor.fetchall()]
            return trips
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить рейсы: {e}")
            return []

    def create_tab(self, table_name, columns, fields, load_query, insert_query, update_query, delete_query, search_field, show_search=True):
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(self.main_content_frame, fg_color=config.BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title_label = ctk.CTkLabel(
            main_frame,
            text=table_name,
            font=config.TITLE_FONT,
            text_color=config.TEXT_COLOR
        )
        title_label.pack(pady=(0, 10))

        left_frame = ctk.CTkFrame(main_frame, fg_color=config.BG_COLOR)
        left_frame.pack(side="left", fill="both", expand=True, padx=5)

        if show_search:
            search_frame = ctk.CTkFrame(left_frame, fg_color=config.BG_COLOR)
            search_frame.pack(fill="x", pady=5)

            def clear_search():
                search_entry.delete(0, "end")
                self.load_records(tree, load_query)

            close_icon = self.load_icon(config.CLOSE_ICON, size=config.ICON_SIZE)
            if close_icon:
                close_button = ctk.CTkButton(
                    search_frame,
                    image=close_icon,
                    text="",
                    command=clear_search,
                    width=config.ICON_SIZE[0],
                    height=config.ICON_SIZE[1],
                    fg_color="white",
                    hover_color="white"
                )
                close_button.pack(side="left", padx=0)
            else:
                messagebox.showwarning("Предупреждение", "Не удалось загрузить close_icon.png, кнопка очистки не отобразится")
                
            # Используем переданный table_name
            search_column = search_field
            # Преобразуем имя столбца в читаемый формат
            if search_column == "Full_Name":
                search_column = "ФИО Сотрудника"
            elif search_column == "Name_Position":
                search_column = "Название должности"  
            elif search_column == "Trip_Name":
                search_column = "Название рейса"
            elif search_column == "Brigade_Name":
                search_column = "Название бригады"
            elif search_column in ["sc.id_brigade", "ID_Brigade"]: 
                search_column = "ID Бригады"
            elif search_column == "e.Full_Name":
                search_column = "ФИО Сотрудника"
            placeholder_text = f"Поиск по: «{search_column}»"

            search_entry = ctk.CTkEntry(
                search_frame,
                width=config.ENTRY_WIDTH,
                height=config.ENTRY_HEIGHT,
                font=config.SEARCH_ENTRY_FONT,
                placeholder_text=placeholder_text,
                placeholder_text_color=config.SECONDARY_TEXT_COLOR 
            )
            search_entry.pack(side="left", padx=0)

            search_icon = self.load_icon(config.SEARCH_ICON, size=config.ICON_SIZE)
            if search_icon:
                search_button = ctk.CTkButton(
                    search_frame,
                    image=search_icon,
                    text="",
                    command=lambda: self.search_records(tree, search_entry, load_query, search_field),
                    width=config.ICON_SIZE[0],
                    height=config.ICON_SIZE[1],
                    fg_color="white",
                    hover_color="white"
                )
                search_button.pack(side="left", padx=0)
            else:
                messagebox.showwarning("Предупреждение", "Не удалось загрузить search_icon.png, кнопка поиска не отобразится")

            search_entry.bind("<Return>", lambda event: self.search_records(tree, search_entry, load_query, search_field))

        tree_frame = ctk.CTkFrame(left_frame, fg_color=config.TABLE_BG_COLOR, height=400)
        tree_frame.pack(fill="both", expand=False, pady=5)
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=config.TREEVIEW_HEIGHT)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree.pack(fill="both", expand=True)

        # Стили для Treeview
        style = ttk.Style()
        style.configure("Treeview", font=config.TREEVIEW_FONT, rowheight=config.TREEVIEW_ROW_HEIGHT,
                        background=config.TABLE_BG_COLOR, fieldbackground=config.TABLE_BG_COLOR, foreground=config.TEXT_COLOR)
        style.map("Treeview",
                background=[("selected", config.TABLE_SELECTED_COLOR), ("!selected", config.TABLE_BG_COLOR)],
                foreground=[("selected", config.TEXT_COLOR), ("!active", config.TEXT_COLOR)])
        style.configure("Treeview.Heading", font=config.TREEVIEW_HEADING_FONT, background=config.TABLE_BG_COLOR, foreground=config.TEXT_COLOR)
        style.map("Treeview.Heading",
                background=[("active", config.TABLE_BG_COLOR), ("!active", config.TABLE_BG_COLOR)],
                foreground=[("active", config.TEXT_COLOR), ("!active", config.TEXT_COLOR)])
        tree.configure(style="Treeview")

        # Определяем, показывать ли кнопки управления
        show_edit_buttons = True
        show_add_button = True

        if self.current_user_role == "Бухгалтер":
            if table_name == "Сотрудники":
                show_edit_buttons = False
                show_add_button = False
        elif self.current_user_role == "Сотрудник":
            if table_name in ["Календарь смен", "Учёт зарплаты"]:
                show_edit_buttons = False
                show_add_button = False

        if show_edit_buttons:
            button_frame = ctk.CTkFrame(left_frame, fg_color=config.BG_COLOR)
            button_frame.pack(fill="x", pady=5, anchor="w")

            work_label = ctk.CTkLabel(
                button_frame,
                text="Работа с записями таблицы:",
                font=config.SUBTITLE_FONT,
                text_color=config.TEXT_COLOR
            )
            work_label.pack(anchor="w", pady=(0, 5))

            buttons_subframe = ctk.CTkFrame(button_frame, fg_color=config.BG_COLOR)
            buttons_subframe.pack(anchor="w")

            copy_button = ctk.CTkButton(
                buttons_subframe,
                text="Копировать",
                command=lambda: self.copy_record(tree),
                width=100,
                height=config.BUTTON_HEIGHT,
                fg_color=config.BUTTON_COLOR,
                hover_color=config.BUTTON_HOVER_COLOR,
                corner_radius=config.CORNER_RADIUS,
                font=config.BUTTON_FONT
            )
            copy_button.pack(side="left", padx=5)

            edit_button = ctk.CTkButton(
                buttons_subframe,
                text="Изменить",
                command=lambda: on_edit(),
                width=100,
                height=config.BUTTON_HEIGHT,
                fg_color=config.BUTTON_COLOR,
                hover_color=config.BUTTON_HOVER_COLOR,
                corner_radius=config.CORNER_RADIUS,
                font=config.BUTTON_FONT
            )
            edit_button.pack(side="left", padx=5)

            delete_button = ctk.CTkButton(
                buttons_subframe,
                text="Удалить",
                command=lambda: self.delete_record(tree, delete_query, load_query),
                width=100,
                height=config.BUTTON_HEIGHT,
                fg_color=config.BUTTON_COLOR,
                hover_color=config.BUTTON_HOVER_COLOR,
                corner_radius=config.CORNER_RADIUS,
                font=config.BUTTON_FONT
            )
            delete_button.pack(side="left", padx=5)

        # Создаём панель ввода
        input_frame = ctk.CTkFrame(main_frame, fg_color="white", width=config.INPUT_FRAME_WIDTH)
        input_frame.pack(side="right", fill="y", padx=5)
        input_frame.pack_propagate(False)

        # Проверяем, нужно ли создавать поля ввода
        if show_edit_buttons or show_add_button:
            # Инициализируем словарь для данных автодополнения
            self.autocomplete_data = getattr(self, 'autocomplete_data', {})

            # Создаём поля ввода только если разрешено редактирование или добавление
            entries = {}
            for label, field_type, options in fields:
                field_frame = ctk.CTkFrame(input_frame, fg_color="white")
                field_frame.pack(anchor="w", pady=2)

                if label == "Дата рождения:" and table_name == "Сотрудники":
                    self.create_icon_label(field_frame, config.BIRTHDAY_ICON)
                elif  label == "Пол:" and table_name == "Сотрудники":
                    self.create_icon_label(field_frame, config.GENDER_ICON)
                elif label == "ФИО Сотрудника:" and table_name in ["Состав бригады", "Учёт зарплаты"]:
                    self.create_icon_label(field_frame, config.USER_ICON)
                elif label == "ID Рейса:" and table_name == "Календарь смен":
                    self.create_icon_label(field_frame, config.FLIGHT_ICON)
                elif label in config.ICON_MAPPING:
                    self.create_icon_label(field_frame, config.ICON_MAPPING[label])

                ctk.CTkLabel(field_frame, text=label, font=config.LABEL_FONT).pack(side="left", padx=5)

                if field_type == "entry":
                    entry = ctk.CTkEntry(input_frame, width=config.INPUT_FRAME_WIDTH, height=config.ENTRY_HEIGHT, font=config.LABEL_FONT)
                    entry.pack(anchor="w", pady=2)
                    entries[label] = entry
                elif field_type == "combobox":
                    entry = ctk.CTkComboBox(input_frame, values=options, width=config.INPUT_FRAME_WIDTH, height=config.ENTRY_HEIGHT, font=config.LABEL_FONT)
                    entry.pack(anchor="w", pady=2)
                    entries[label] = entry
                elif field_type == "combobox_autocomplete":
                    values = []
                    value_id_map = {}
                    if label == "ФИО Сотрудника:":
                        employees = self.get_employees()
                        values = [name for name, _ in employees]
                        value_id_map = {name: id for name, id in employees}
                    elif label == "Название рейса:":
                        trips = self.get_trips()
                        values = [name for name, _ in trips]
                        value_id_map = {name: id for name, id in trips}
                    entry = ctk.CTkComboBox(
                        input_frame,
                        values=values,
                        width=config.INPUT_FRAME_WIDTH,
                        height=config.ENTRY_HEIGHT,
                        font=config.LABEL_FONT,
                        dropdown_font=config.LABEL_FONT,
                        state="normal"
                    )
                    entry.pack(anchor="w", pady=2)
                    entries[label] = entry
                    self.autocomplete_data[label] = value_id_map  # Сохраняем value_id_map в self.autocomplete_data

                    def update_combobox(event, combo, vals):
                        current = combo.get().strip()
                        current_lower = current.lower()
                        filtered = [v for v in vals if v.lower().startswith(current_lower)] if current else vals
                        combo.configure(values=filtered)
                        combo.set(current)
                        return "break"

                    entry.bind("<KeyRelease>", lambda event, c=entry, v=values: update_combobox(event, c, v))

                    def validate_selection(combo, vals):
                        selected = combo.get().strip()
                        if selected and selected not in vals:
                            messagebox.showwarning("Ошибка", f"Выберите значение из списка для поля '{label[:-1]}'!")
                            return False
                        return True

                    entry.bind("<FocusOut>", lambda event, c=entry, v=values: validate_selection(c, v))

            # Создаём кнопку "Добавить" только если разрешено добавление
            if show_add_button:
                action_frame = ctk.CTkFrame(input_frame, fg_color="white")
                action_frame.pack(anchor="w", pady=10)

                self.add_save_button = ctk.CTkButton(
                    action_frame,
                    text="Добавить",
                    command=lambda: self.add_record(tree, entries, insert_query, load_query),
                    width=100,
                    height=config.BUTTON_HEIGHT,
                    fg_color=config.BUTTON_COLOR,
                    hover_color=config.BUTTON_HOVER_COLOR,
                    corner_radius=config.CORNER_RADIUS,
                    font=config.BUTTON_FONT
                )
                self.add_save_button.pack(side="left", padx=5)
        else:
            # Если редактирование и добавление запрещены, показываем только сообщение
            readonly_label = ctk.CTkLabel(
                input_frame,
                text=config.TABLE_READONLY_MESSAGE,
                font=config.LABEL_FONT,
                text_color=config.SECONDARY_TEXT_COLOR,
                wraplength=config.INPUT_FRAME_WIDTH - 20,
                justify="center"
            )
            readonly_label.pack(expand=True, anchor="center", pady=20)

        def on_edit():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Ошибка", "Выберите запись!")
                return
            values = tree.item(selected)["values"]
            if not values or len(values) < len(columns):
                messagebox.showwarning("Ошибка", "Выбранная строка содержит некорректные данные!")
                return
                        
            if table_name == "Сотрудники":
                field_mapping = {
                    "ФИО:": 1,
                    "Пол:": 2,
                    "Дата рождения:": 3,
                    "Должность:": 5,
                    "Почта:": 6
                }
            elif table_name == "Должности":
                field_mapping = {
                    "Название должности:": 1,
                    "Ставка за час:": 2
                }
            elif table_name == "Рейсы":
                field_mapping = {
                    "Название рейса:": 1,
                    "Дата отправления:": 3,
                    "Дата прибытия:": 4,
                    "Время отправления:": 5,
                    "Время прибытия:": 6
                }
            elif table_name == "Состав бригады":
                field_mapping = {
                    "ID Бригады:": 0,
                    "ФИО Сотрудника:": 1,
                    "Название рейса:": 2,
                    "Название бригады:": 3,
                    "Дата формирования:": 4
                }
            elif table_name == "Календарь смен":
                field_mapping = {
                    "ID Бригады:": 0,
                    "Дата начала:": 1,
                    "Дата окончания:": 2,
                    "ID Рейса:": 3
                }
            elif table_name == "Учёт зарплаты":
                field_mapping = {
                    "ФИО Сотрудника:": 0,
                    "Сумма:": 1,
                    "Дата выплаты:": 2
                }
            else:
                field_mapping = {}

            for label, index in field_mapping.items():
                widget = entries[label]
                value = values[index] if index < len(values) else ""
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, "end")
                    widget.insert(0, str(value) if value is not None else "")
                elif isinstance(widget, ctk.CTkComboBox):
                    try:
                        options = widget.cget("values")
                        options = [str(opt).strip() for opt in options]
                        str_value = str(value).strip() if value is not None else ""
                        if str_value in options:
                            widget.set(str_value)
                        else:
                            widget.set("")
                    except Exception as e:
                        widget.set("")
                        messagebox.showerror("Ошибка", f"Не удалось заполнить выпадающий список для {label}: {e}")

            self.add_save_button.configure(
                text="Сохранить",
                command=lambda: self.update_record(tree, entries, update_query, load_query, on_save_success)
            )

        def on_save_success():
            for label, widget in entries.items():
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, "end")
                elif isinstance(widget, ctk.CTkComboBox):
                    widget.set("")

            self.add_save_button.configure(
                text="Добавить",
                command=lambda: self.add_record(tree, entries, insert_query, load_query)
            )

        self.load_records(tree, load_query)
        self.root.update()

    def copy_record(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите запись для копирования!")
            return
        try:
            values = tree.item(selected)["values"]
            record_text = "\t".join(str(value) for value in values)
            pyperclip.copy(record_text)
            messagebox.showinfo("Успех", "Запись скопирована в буфер обмена!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось скопировать запись: {e}")

    def load_records(self, tree, query):
        try:
            self.conn.rollback()
            current_items = [(item, tree.item(item)["values"]) for item in tree.get_children()]
            for item in tree.get_children():
                tree.delete(item)
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            for row in rows:
                # Преобразуем значения для отображения
                formatted_row = []
                for idx, value in enumerate(row):
                    if idx == 2 and query.startswith("SELECT ID_Trip"):  
                        if isinstance(value, timedelta):
                            # Преобразуем timedelta в формат HH:MM:SS
                            total_seconds = int(value.total_seconds())
                            hours = total_seconds // 3600
                            minutes = (total_seconds % 3600) // 60
                            seconds = total_seconds % 60
                            formatted_value = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                            formatted_row.append(formatted_value)
                        else:
                            formatted_row.append(str(value) if value is not None else "")
                    else:
                        formatted_row.append(str(value) if value is not None else "")
                tree.insert("", "end", values=formatted_row)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить записи: {e}")

    def calculate_age(self, birth_date_str):
        try:
            birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
            current_date = datetime.now()  
            age = current_date.year - birth_date.year
            if current_date.month < birth_date.month or (current_date.month == birth_date.month and current_date.day < birth_date.day):
                age -= 1
            return age
        except ValueError as e:
            return None

    def add_record(self, tree, entries, insert_query, load_query):
        entry_values = []
        table_name = None
        for name, cfg in config.TABLES.items():
            if cfg["insert_query"] == insert_query:
                table_name = name
                break

        if not table_name:
            messagebox.showerror("Ошибка", "Не удалось определить таблицу для добавления!")
            return

        for label, field_type, _ in config.TABLES[table_name]["fields"]:
            widget = entries.get(label)
            if not widget or not isinstance(widget, (ctk.CTkEntry, ctk.CTkComboBox)):
                messagebox.showwarning("Ошибка", f"Некорректное поле '{label}'!")
                return

            value = widget.get().strip()
            if field_type == "combobox_autocomplete":
                id_map = self.autocomplete_data.get(label, {})
                if value in id_map:
                    value = id_map[value]
                else:
                    messagebox.showwarning("Ошибка", f"Недопустимое значение для поля '{label[:-1]}'!")
                    return
            entry_values.append(value)

        if not all(v.strip() if isinstance(v, str) else v for v in entry_values):
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        # Проверки для таблицы "Сотрудники"
        if table_name == "Сотрудники":
            labels = ["ФИО:", "Пол:", "Дата рождения:", "Должность:", "Почта:"]
            for label, value in zip(labels, entry_values):
                if label == "ФИО:":
                    if not isinstance(value, str) or not value.strip():
                        messagebox.showerror("Ошибка", f"Введённое значение для поля {label[:-1]} имеет неверный тип! Ожидается строка.")
                        return
                elif label == "Пол:":
                    if value not in ["М", "Ж"]:
                        messagebox.showerror("Ошибка", f"Введённое значение для поля {label[:-1]} имеет неверный тип! Ожидается 'М' или 'Ж'.")
                        return
                elif label == "Дата рождения:":
                    age = self.calculate_age(value)
                    if age is None:
                        messagebox.showerror("Ошибка", f"Введённое значение для поля {label[:-1]} имеет неверный формат! Ожидается дата в формате ГГГГ-ММ-ДД.")
                        return
                    if age < 16:
                        messagebox.showerror("Ошибка", "Сотрудник не достигает возраста 16 лет!")
                        return
                elif label == "Должность:":
                    if not isinstance(value, str) or not value.strip():
                        messagebox.showerror("Ошибка", f"Введённое значение для поля {label[:-1]} имеет неверный тип! Ожидается строка.")
                        return
                elif label == "Почта:":
                    if not isinstance(value, str):
                        messagebox.showerror("Ошибка", f"Введённое значение для поля {label[:-1]} имеет неверный тип! Ожидается строка.")
                        return
                    
        elif table_name == "Учёт зарплаты":
            employee_id = entry_values[0]  # ID_Employee
            try:
                self.cursor.execute("SELECT ID_Employee FROM Employees WHERE ID_Employee = %s", (employee_id,))
                if not self.cursor.fetchone():
                    messagebox.showerror("Ошибка", f"Сотрудник с ID {employee_id} не найден!")
                    return
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка проверки данных: {e}")
                return

        try:
            self.conn.rollback()
            self.cursor.execute(insert_query, entry_values)
            self.conn.commit()
            self.load_records(tree, load_query)
            for entry in entries.values():
                if isinstance(entry, ctk.CTkEntry):
                    entry.delete(0, "end")
                elif isinstance(entry, ctk.CTkComboBox):
                    entry.set("")
            messagebox.showinfo("Успех", "Запись успешно добавлена!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить запись: {e}")

    def update_record(self, tree, entries, update_query, load_query, on_save_success):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите запись!")
            return
        values = tree.item(selected)["values"]
        if not values:
            messagebox.showwarning("Ошибка", "Выбранная строка пуста!")
            return
        
        # Находим таблицу по update_query
        table_name = None
        for name, cfg in config.TABLES.items():
            if cfg["update_query"] == update_query:
                table_name = name
                break

        if not table_name:
            messagebox.showerror("Ошибка", "Не удалось определить таблицу для обновления!")
            return

        # Собираем значения из виджетов в порядке полей
        entry_values = []
        for label, field_type, _ in config.TABLES[table_name]["fields"]:
            widget = entries.get(label)
            if not widget or not isinstance(widget, (ctk.CTkEntry, ctk.CTkComboBox)):
                entry_values.append("")
                continue

            value = widget.get().strip()
            if field_type == "combobox_autocomplete":
                id_map = self.autocomplete_data.get(label, {})
                if value in id_map:
                    value = id_map[value]  # Используем ID вместо строки
                else:
                    messagebox.showwarning("Ошибка", f"Недопустимое значение для поля '{label[:-1]}'!")
                    return
            entry_values.append(value)

        if not all(v.strip() if isinstance(v, str) else v for v in entry_values):
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        # Получаем индексы столбцов для WHERE
        where_keys = config.TABLES[table_name].get("where_keys", [0])

        # Проверяем, достаточно ли данных в values для всех ключей
        max_key = max(where_keys)
        if len(values) <= max_key:
            messagebox.showerror("Ошибка", f"Недостаточно данных в выбранной строке для обновления! Требуется {max_key + 1} значений, найдено {len(values)}.")
            return

        # Формируем значения для WHERE
        where_values = []
        for key_idx in where_keys:
            if (table_name == "Состав бригады" and key_idx == 1) or (table_name == "Учёт зарплаты" and key_idx == 0):
                # Для ID_Employee получаем ID по строке вида "Full_Name (ID)"
                employee_str = values[key_idx]
                id_map = self.autocomplete_data.get("ФИО Сотрудника:", {})
                if employee_str in id_map:
                    where_values.append(id_map[employee_str])
                else:
                    messagebox.showerror("Ошибка", f"Сотрудник '{employee_str}' не найден!")
                    return
            else:
                where_values.append(values[key_idx])

        # Добавляем значения для условия WHERE к основным значениям
        final_values = entry_values + where_values

        # Специфические проверки для таблицы "Состав бригады"
        if table_name == "Состав бригады":
            employee_id = entry_values[1]
            trip_id = entry_values[2]
            try:
                self.cursor.execute("SELECT ID_Employee FROM Employees WHERE ID_Employee = %s", (employee_id,))
                if not self.cursor.fetchone():
                    messagebox.showerror("Ошибка", f"Сотрудник с ID {employee_id} не найден!")
                    return
                self.cursor.execute("SELECT ID_Trip FROM Trips WHERE ID_Trip = %s", (trip_id,))
                if not self.cursor.fetchone():
                    messagebox.showerror("Ошибка", f"Рейс с ID {trip_id} не найден!")
                    return
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка проверки данных: {e}")
                return

        try:
            self.conn.rollback()
            self.cursor.execute(update_query, final_values)
            self.conn.commit()
            self.load_records(tree, load_query)
            messagebox.showinfo("Успех", "Запись успешно обновлена!")
            on_save_success()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить запись: {e}")

    def delete_record(self, tree, delete_query, load_query):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите запись!")
            return
        values = tree.item(selected)["values"]
        if not values:
            messagebox.showwarning("Ошибка", "Выбранная строка пуста!")
            return

        # Находим таблицу по delete_query
        table_name = None
        for name, cfg in config.TABLES.items():
            if cfg["delete_query"] == delete_query:
                table_name = name
                break

        if not table_name:
            messagebox.showerror("Ошибка", "Не удалось определить таблицу для удаления!")
            return

        # Получаем индексы столбцов для WHERE
        where_keys = config.TABLES[table_name].get("where_keys", [0])

        # Проверяем, достаточно ли данных в values для всех ключей
        max_key = max(where_keys)
        if len(values) <= max_key:
            messagebox.showerror("Ошибка", f"Недостаточно данных в выбранной строке для удаления! Требуется {max_key + 1} значений, найдено {len(values)}.")
            return

        # Формируем значения для WHERE
        where_values = []
        for key_idx in where_keys:
            if table_name == "Учёт зарплаты" and key_idx == 0:
                # Для "Учёт зарплаты" ID_Employee в столбце "ФИО Сотрудника" (индекс 0)
                if self.current_user_role == "Сотрудник":
                    # Для роли "Сотрудник" столбец "ФИО Сотрудника" скрыт, используем current_user_id
                    if self.current_user_id is None:
                        messagebox.showerror("Ошибка", "ID сотрудника не определён для текущего пользователя!")
                        return
                    where_values.append(self.current_user_id)
                else:
                    # Извлекаем ID_Employee из строки "Full_Name (ID)"
                    employee_str = values[key_idx]
                    id_map = self.autocomplete_data.get("ФИО Сотрудника:", {})
                    if employee_str in id_map:
                        where_values.append(id_map[employee_str])
                    else:
                        messagebox.showerror("Ошибка", f"Сотрудник '{employee_str}' не найден в данных автодополнения!")
                        return
            elif table_name == "Состав бригады" and key_idx == 1:
                # Для "Состав бригады" ID_Employee в столбце "ФИО Сотрудника" (индекс 1)
                employee_str = values[key_idx]
                id_map = self.autocomplete_data.get("ФИО Сотрудника:", {})
                if employee_str in id_map:
                    where_values.append(id_map[employee_str])
                else:
                    messagebox.showerror("Ошибка", f"Сотрудник '{employee_str}' не найден в данных автодополнения!")
                    return
            else:
                # Для остальных полей (ID_Brigade, ID_Trip, Payment_Date) берём значение напрямую
                where_values.append(values[key_idx])

        try:
            self.conn.rollback()
            self.cursor.execute(delete_query, tuple(where_values))
            self.conn.commit()
            self.load_records(tree, load_query)
            messagebox.showinfo("Успех", "Запись успешно удалена!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")

    def search_records(self, tree, search_entry, load_query, search_field):
        try:
            self.conn.rollback()
            search_term = search_entry.get()
            for item in tree.get_children():
                tree.delete(item)

            # Находим таблицу по load_query (ищем базовую часть запроса до WHERE или ORDER BY)
            table_name = None
            base_load_query = load_query.split("WHERE")[0].split("ORDER BY")[0].strip()
            for name, cfg in config.TABLES.items():
                cfg_base_query = cfg["load_query"].split("WHERE")[0].split("ORDER BY")[0].strip()
                if cfg_base_query in base_load_query or base_load_query in cfg_base_query:
                    table_name = name
                    break

            if not table_name:
                messagebox.showerror("Ошибка", f"Не удалось определить таблицу для поиска! Base query: {base_load_query}")
                return

            # Получаем тип поля поиска
            search_field_type = config.TABLES[table_name].get("search_field_type", "string")

            # Разделяем load_query на основную часть и ORDER BY (если есть)
            query_parts = load_query.split("ORDER BY")
            base_query = query_parts[0].strip()
            order_by_clause = f" ORDER BY {query_parts[1].strip()}" if len(query_parts) > 1 else ""

            # Формируем условие поиска в зависимости от типа данных
            if search_field_type == "string":
                condition = f"{search_field} ILIKE %s"
                search_value = f"%{search_term}%"
            elif search_field_type == "integer":
                condition = f"{search_field} = %s"
                try:
                    search_value = int(search_term)
                except ValueError:
                    messagebox.showwarning("Ошибка", "Введите целое число для поиска по этому полю!")
                    self.load_records(tree, load_query)
                    return
            elif search_field_type == "timestamp":
                condition = f"{search_field}::text ILIKE %s"  # Изменено для частичного поиска по строке
                search_value = f"%{search_term}%"
            else:
                messagebox.showerror("Ошибка", f"Неизвестный тип поля для поиска: {search_field_type}")
                return

            # Проверяем, есть ли уже WHERE в запросе
            if "WHERE" in base_query.upper():
                query = f"{base_query} AND {condition}{order_by_clause}"
            else:
                query = f"{base_query} WHERE {condition}{order_by_clause}"

            self.cursor.execute(query, (search_value,))
            for row in self.cursor.fetchall():
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить поиск: {e}")

    def get_positions(self):
        try:
            self.conn.rollback()
            self.cursor.execute("SELECT Name_Position FROM Position")
            positions = [row[0].strip() for row in self.cursor.fetchall()]
            return positions
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить должности: {e}")
            return []

    def show_employees_tab(self):
        table = config.TABLES["Сотрудники"]
        fields = table["fields"].copy()
        for i, (label, field_type, _) in enumerate(fields):
            if label == "Должность:":
                fields[i] = (label, field_type, self.get_positions())
        self.create_tab(
            "Сотрудники",
            table["columns"],
            fields,
            table["load_query"],
            table["insert_query"],
            table["update_query"],
            table["delete_query"],
            table["search_field"],
            show_search=True
        )

    def show_positions_tab(self):
        table = config.TABLES["Должности"]
        self.create_tab(
            "Должности",
            table["columns"],
            table["fields"],
            table["load_query"],
            table["insert_query"],
            table["update_query"],
            table["delete_query"],
            table["search_field"],
            show_search=True
        )

    def show_trips_tab(self):
        table = config.TABLES["Рейсы"]
        self.create_tab(
            "Рейсы",
            table["columns"],
            table["fields"],
            table["load_query"],
            table["insert_query"],
            table["update_query"],
            table["delete_query"],
            table["search_field"],
            show_search=True
        )

    def show_brigade_composition_tab(self):
        table = config.TABLES["Состав бригады"]
        fields = table["fields"].copy()
        for i, (label, field_type, _) in enumerate(fields):
            if label == "ФИО Сотрудника:":
                fields[i] = (label, field_type, self.get_employees())
            elif label == "Название рейса:":
                fields[i] = (label, field_type, self.get_trips())
        self.create_tab(
            "Состав бригады",
            table["columns"],
            fields,
            table["load_query"],
            table["insert_query"],
            table["update_query"],
            table["delete_query"],
            table["search_field"],
            show_search=True
        )

    def show_shift_calendar_tab(self):
        # Определяем текущую дату
        today = datetime.now()
        self.current_year = today.year
        self.current_month = today.month
        self.current_day = today.day
        self.days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]

        table = config.TABLES["Календарь смен"]
        load_query = table["load_query"]
        if self.current_user_role == "Сотрудник" and self.current_user_id is not None:
            load_query += f"""
                WHERE bc.id_employee = {self.current_user_id}
                ORDER BY sc.start_date
            """
        else:
            load_query += " ORDER BY sc.start_date"

        if self.current_user_role != "Сотрудник":
            self.create_tab(
                "Календарь смен",
                table["columns"],
                table["fields"],
                load_query,
                table["insert_query"],
                table["update_query"],
                table["delete_query"],
                table["search_field"],
                show_search=True
            )
        else:
            # Для сотрудника показываем календарь
            for widget in self.main_content_frame.winfo_children():
                widget.destroy()

            main_frame = ctk.CTkFrame(self.main_content_frame, fg_color=config.BG_COLOR)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)

            header_frame = ctk.CTkFrame(main_frame, fg_color=config.BG_COLOR)
            header_frame.pack(fill="x", pady=(0, 10))

            left_arrow_image = ctk.CTkImage(Image.open(config.LEFT_ARROW_ICON), size=config.ARROW_ICON_SIZE)
            right_arrow_image = ctk.CTkImage(Image.open(config.RIGHT_ARROW_ICON), size=config.ARROW_ICON_SIZE)

            prev_button = ctk.CTkButton(
                header_frame,
                text="",
                image=left_arrow_image,
                command=lambda: self.change_month(-1),
                width=config.ARROW_ICON_SIZE[0] * 2,
                height=config.BUTTON_HEIGHT,
                fg_color="transparent",
                hover_color=config.BG_COLOR,
                corner_radius=config.CORNER_RADIUS
            )
            prev_button.pack(side="left", padx=5)

            self.title_label = ctk.CTkLabel(
                header_frame,
                text=f"{config.MONTH_NAMES[self.current_month - 1]} {self.current_year}",
                font=config.TITLE_FONT,
                text_color=config.TEXT_COLOR
            )
            self.title_label.pack(side="left", expand=True)

            next_button = ctk.CTkButton(
                header_frame,
                text="",
                image=right_arrow_image,
                command=lambda: self.change_month(1),
                width=config.ARROW_ICON_SIZE[0] * 2,
                height=config.BUTTON_HEIGHT,
                fg_color="transparent",
                hover_color=config.BG_COLOR,
                corner_radius=config.CORNER_RADIUS
            )
            next_button.pack(side="right", padx=5)

            self.left_frame = ctk.CTkFrame(main_frame, fg_color=config.BG_COLOR)
            self.left_frame.pack(side="left", fill="both", expand=True, padx=5)

            self.info_frame = ctk.CTkFrame(main_frame, fg_color="white", width=config.INPUT_FRAME_WIDTH)
            self.info_frame.pack(side="right", fill="y", padx=5)
            self.info_frame.pack_propagate(False)

            self.date_label = ctk.CTkLabel(
                self.info_frame,
                text="",
                font=config.TITLE_FONT,
                text_color=config.BUTTON_COLOR
            )
            self.date_label.pack(anchor="w", pady=(10, 5))

            self.shift_info_label = ctk.CTkLabel(
                self.info_frame,
                text="",
                font=config.LABEL_FONT,
                text_color=config.TEXT_COLOR,
                wraplength=config.INPUT_FRAME_WIDTH - 10,
                justify="left"
            )
            self.shift_info_label.pack(anchor="w", pady=5)

            self.load_query = load_query
            self.update_calendar()

    def change_month(self, delta):
        self.current_month += delta
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        elif self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.update_calendar()

    def update_calendar(self):
        self.days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
        self.title_label.configure(text=f"{config.MONTH_NAMES[self.current_month - 1]} {self.current_year}")

        for widget in self.left_frame.winfo_children():
            widget.destroy()

        calendar_frame = ctk.CTkFrame(self.left_frame, fg_color=config.TABLE_BG_COLOR)
        calendar_frame.pack(fill="both", expand=True, pady=5)

        calendar_grid = ctk.CTkFrame(calendar_frame, fg_color=config.TABLE_BG_COLOR)
        calendar_grid.pack(pady=5, padx=5)

        for col, day_name in enumerate(config.DAYS_OF_WEEK):
            day_label = ctk.CTkLabel(
                calendar_grid,
                text=day_name,
                font=config.CALENDAR_DAY_BOLD_FONT,
                text_color=config.TEXT_COLOR,
                width=config.CALENDAR_DAY_WIDTH,
                height=20
            )
            day_label.grid(row=0, column=col, padx=2, pady=2)

        shifts = []
        if self.current_user_id is not None:
            try:
                self.conn.rollback()
                self.cursor.execute(self.load_query)
                shifts = self.cursor.fetchall()
            except Exception as e:
                self.conn.rollback()

        shift_days = set()
        shift_details = {}
        for shift in shifts:
            start_datetime = shift[1]
            end_datetime = shift[2]
            trip_name = shift[4]
            arrival_time = shift[5]
            brigade_name = shift[6]
            start_date = start_datetime.date()
            end_date = end_datetime.date()

            current_date = start_date
            while current_date <= end_date:
                if current_date.year == self.current_year and current_date.month == self.current_month:
                    day = current_date.day
                    shift_days.add(day)
                    if day not in shift_details:
                        shift_details[day] = []
                    shift_details[day].append((start_datetime, end_datetime, trip_name, arrival_time, brigade_name))
                current_date += timedelta(days=1)

        first_day_of_month = datetime(self.current_year, self.current_month, 1).weekday()
        self.day_buttons = {}
        for day in range(1, self.days_in_month + 1):
            row = (day + first_day_of_month - 1) // 7 + 1
            col = (day + first_day_of_month - 1) % 7

            day_frame = ctk.CTkFrame(
                calendar_grid,
                width=config.CALENDAR_DAY_WIDTH,
                height=config.CALENDAR_DAY_HEIGHT,
                fg_color=config.BG_COLOR,
                border_width=config.CALENDAR_DAY_BORDER_WIDTH if day in shift_days else 0,
                border_color=config.BORDER_COLOR if day in shift_days else None,
                corner_radius=config.CORNER_RADIUS
            )
            day_frame.grid(row=row, column=col, padx=2, pady=2)
            day_frame.grid_propagate(False)

            day_number = ctk.CTkLabel(
                day_frame,
                text=str(day),
                font=config.CALENDAR_DAY_FONT,
                text_color=config.TEXT_COLOR,
                anchor="nw"
            )
            day_number.place(x=5, y=5)

            # Добавляем метки для времени начала и окончания смены
            if day in shift_details:
                for start_datetime, end_datetime, _, _, _ in shift_details[day]:
                    start_date = start_datetime.date()
                    end_date = end_datetime.date()
                    start_time = start_datetime.strftime("%H:%M")
                    end_time = end_datetime.strftime("%H:%M")

                    # Если смена начинается и заканчивается в один день
                    if start_date == end_date and start_date.day == day:
                        start_time_label = ctk.CTkLabel(
                            day_frame,
                            text=start_time,
                            font=config.CALENDAR_DAY_FONT,
                            text_color=config.TEXT_COLOR,
                            anchor="center"
                        )
                        start_time_label.place(relx=0.5, rely=0.35, anchor="center")

                        end_time_label = ctk.CTkLabel(
                            day_frame,
                            text=end_time,
                            font=config.CALENDAR_DAY_FONT,
                            text_color=config.TEXT_COLOR,
                            anchor="center"
                        )
                        end_time_label.place(relx=0.5, rely=0.6, anchor="center")
                        
                        start_time_label.bind("<Button-1>", lambda event, d=day: on_day_click(d))
                        end_time_label.bind("<Button-1>", lambda event, d=day: on_day_click(d))

                    else:
                        # Если это первый день смены
                        if start_date.day == day:
                            start_time_label = ctk.CTkLabel(
                                day_frame,
                                text=start_time,
                                font=config.CALENDAR_DAY_FONT,
                                text_color=config.TEXT_COLOR,
                                anchor="center"
                            )
                            start_time_label.place(relx=0.5, rely=0.5, anchor="center")
                            start_time_label.bind("<Button-1>", lambda event, d=day: on_day_click(d))
                        # Если это последний день смены
                        elif end_date.day == day:
                            end_time_label = ctk.CTkLabel(
                                day_frame,
                                text=end_time,
                                font=config.CALENDAR_DAY_FONT,
                                text_color=config.TEXT_COLOR,
                                anchor="center"
                            )
                            end_time_label.place(relx=0.5, rely=0.5, anchor="center")
                            end_time_label.bind("<Button-1>", lambda event, d=day: on_day_click(d))
                    # Промежуточные дни не показывают время, только выделение
                    break  # Показываем только одну смену на день

            self.day_buttons[day] = day_frame

        def update_info_panel(selected_day):
            selected_date = datetime(self.current_year, self.current_month, selected_day)
            day_name = config.DAYS_OF_WEEK[selected_date.weekday()]
            date_str = f"{selected_date.strftime('%d.%m.%Y')}, {day_name}"
            self.date_label.configure(text=date_str)

            if selected_day not in shift_days:
                self.shift_info_label.configure(text="На данную дату смена не поставлена")
            else:
                info_text = ""
                for start_datetime, end_datetime, trip_name, arrival_time, brigade_name in shift_details[selected_day]:
                    start_str = start_datetime.strftime("%d.%m.%Y %H:%M")
                    end_str = end_datetime.strftime("%d.%m.%Y %H:%M")
                    start_time = start_datetime.strftime("%H:%M")
                    end_time = end_datetime.strftime("%H:%M")
                    start_date = start_datetime.date()
                    end_date = end_datetime.date()

                info_text += f"• Путь следования: \n «{trip_name}»\n\n"
                # Проверяем, начинается и заканчивается ли смена в один день
                if start_date == end_date:
                    # Если смена в один день и это выбранный день
                    if start_date.day == selected_day:
                        info_text += f"• Начало смены: \n {start_time}\n\n"
                        info_text += f"• Конец смены: \n {end_time}\n\n"
                else:
                    # Смена длится несколько дней
                    if start_date.day == selected_day:
                        # Первый день смены: показываем только время начала
                        info_text += f"• Начало смены: \n {start_time}\n\n"
                        info_text += f"• Конец смены: \n {end_str}\n\n"
                    elif end_date.day == selected_day:
                        # Последний день смены: показываем только время конца
                        info_text += f"• Начало смены: \n {start_str}\n\n"
                        info_text += f"• Конец смены: \n {end_time}\n\n"
                    else:
                        # Промежуточный день: показываем обе даты
                        info_text += f"• Начало смены: \n {start_str}\n\n"
                        info_text += f"• Конец смены: \n {end_str}\n\n"


                info_text += f"• Время в пути: \n {arrival_time}\n\n"
                info_text += f"• Смена в составе бригады: \n «{brigade_name}»\n\n"

                self.shift_info_label.configure(text=info_text.strip())

        def on_day_click(day):
            update_info_panel(day)
            for d, btn in self.day_buttons.items():
                # Сбрасываем цвет фона и текста для всех карточек
                btn.configure(fg_color=config.BG_COLOR)
                # Перебираем все дочерние виджеты (метки) и меняем их цвет текста
                for child in btn.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        child.configure(text_color=config.TEXT_COLOR)

            # Устанавливаем цвет фона и текста для активной карточки
            active_btn = self.day_buttons[day]
            active_btn.configure(fg_color=config.HIGHLIGHT_COLOR)
            # Перебираем все дочерние виджеты активной карточки и меняем их цвет текста
            for child in active_btn.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    child.configure(text_color=config.TEXT_COLOR_2)

        for day in range(1, self.days_in_month + 1):
            self.day_buttons[day].bind("<Button-1>", lambda event, d=day: on_day_click(d))

        today = datetime.now()
        default_day = min(today.day, self.days_in_month) if today.year == self.current_year and today.month == self.current_month else 1
        update_info_panel(default_day)
        self.day_buttons[default_day].configure(fg_color=config.HIGHLIGHT_COLOR)
        # Устанавливаем цвет текста для меток начального активного дня
        for child in self.day_buttons[default_day].winfo_children():
            if isinstance(child, ctk.CTkLabel):
                child.configure(text_color=config.TEXT_COLOR_2)

    def show_payroll_accounting_tab(self):
        table = config.TABLES["Учёт зарплаты"]
        fields = table["fields"].copy()
        for i, (label, field_type, _) in enumerate(fields):
            if label == "ФИО Сотрудника:":
                fields[i] = (label, field_type, self.get_employees())  
        load_query = table["load_query"]
        columns = list(table["columns"])

        # Для сотрудника скрываем столбец ФИО Сотрудника, поля ввода и строку поиска
        show_search = True
        if self.current_user_role == "Сотрудник" and self.current_user_id is not None:
            if "ФИО Сотрудника" in columns:
                columns.remove("ФИО Сотрудника")

            # Удаляем Full_Name из SELECT в load_query
            load_query = load_query.replace("e.Full_Name || ' (' || e.ID_Employee || ')' AS Full_Name, ", "")
            # Добавляем условие фильтрации по ID_Employee
            load_query += f" WHERE p.ID_Employee = {self.current_user_id}"

            # Для роли "Сотрудник" передаём пустой список полей, чтобы не создавать поля ввода
            fields = []
            # Скрываем строку поиска
            show_search = False

        load_query += " ORDER BY p.Payment_Date"

        self.create_tab(
            "Учёт зарплаты",
            columns,
            fields,
            load_query,
            table["insert_query"],
            table["update_query"],
            table["delete_query"],
            table["search_field"],
            show_search=show_search
        )

    def exit(self):
        self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = DatabaseApp(root)
    root.mainloop()