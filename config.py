import os.path

# Определяем корневую директорию проекта относительно текущего файла
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================================================
# Параметры базы данных
# ==========================================================================
DB_NAME = "SalaryAccounting"
DB_USER = "postgres"
DB_PASSWORD = "root"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_OPTIONS = "-c client_encoding=UTF8"

# ==========================================================================
# Названия и заголовки
# ==========================================================================
APP_TITLE = "Учёт заработной платы локомотивных бригад"
SIDEBAR_TITLE = "АС УРЗП"

# Форма входа в система
LOGIN_PAGE_TITLE = "Вход в систему"
FORGOT_PASSWORD_MESSAGE = "Забыли пароль? Тогда обратитесь к администратору"

# Раздел "Главная"
WELCOME_MESSAGE = "Добрый день, {}!"
HOME_PAGE_MESSAGE = (
    "Вы находитесь в приложении для учёта заработной платы локомотивных бригад.\n"
    "Для начала работы выберите одну из таблиц слева."
)

# Прочее
TABLE_READONLY_MESSAGE = "Данная таблица доступна только в режиме просмотра"

# ==========================================================================
# Размеры и параметры окна
# ==========================================================================
WINDOW_SIZE = "1200x610"
SIDEBAR_WIDTH = 200
BUTTON_WIDTH = 140
BUTTON_HEIGHT = 40
INPUT_FRAME_WIDTH = 200
ENTRY_WIDTH = 230
ENTRY_HEIGHT = 30
CALENDAR_DAY_WIDTH = 80
CALENDAR_DAY_HEIGHT = 80
TREEVIEW_HEIGHT = 15
TREEVIEW_ROW_HEIGHT = 25

# ==========================================================================
# Цвета
# ==========================================================================
BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#000000"
TEXT_COLOR_2 = "#FFFFFF"
SECONDARY_TEXT_COLOR = "#979DA2"
SIDEBAR_COLOR = "#E8F5E9"
TABLE_BG_COLOR = "#E8F5E9"
TABLE_SELECTED_COLOR = "#A5D6A7"
BUTTON_COLOR = "#4CAF50"
BUTTON_HOVER_COLOR = "#45A049"
HIGHLIGHT_COLOR = "#6BBA51"
BORDER_COLOR = "#4CAF50"

# ==========================================================================
# Параметры шрифтов
# ==========================================================================
APP_TITLE_FONT = ("Arial", 26, "bold")
LOGIN_TITLE_FONT = ("Arial", 20, "bold")
WELCOME_FONT = ("Arial", 20, "bold")

TITLE_FONT = ("Arial", 16, "bold")
SUBTITLE_FONT = ("Arial", 14)

LABEL_FONT = ("Arial", 14)
BUTTON_FONT = ("Arial", 14)
TREEVIEW_HEADING_FONT = ("Arial", 10, "bold")
TREEVIEW_FONT = ("Arial", 10)

CALENDAR_DAY_BOLD_FONT = ("Arial", 12, "bold")
CALENDAR_DAY_FONT = ("Arial", 12)
HOME_MESSAGE_FONT = ("Arial", 16)
INFO_TEXT_FONT = ("Arial", 14, "italic")
SEARCH_ENTRY_FONT = ("Arial", 10)

# ==========================================================================
# Параметры стилей
# ==========================================================================
CORNER_RADIUS = 15
BORDER_WIDTH = 2
ICON_SIZE = (25, 25)
ARROW_ICON_SIZE = (30, 30)
CALENDAR_DAY_BORDER_WIDTH = 2
LOGO_SIZE = (400, 250)

# ==========================================================================
# Пути к файлам
# ==========================================================================
LOGO = os.path.join(ROOT_DIR,"src", "assets", "logo.ico")
LOGIN_FILE_PATH = os.path.join(ROOT_DIR, "src", "data", "last_login.json")

BACKGROUND_LOGIN_IMAGE = os.path.join(ROOT_DIR, "src", "assets", "background_login.png")

TRAIN_LOGO_IMAGE = os.path.join(ROOT_DIR, "src", "assets", "train_logo.jpg")

CLOSE_ICON = os.path.join(ROOT_DIR, "src", "assets", "close_icon.png")
SEARCH_ICON = os.path.join(ROOT_DIR, "src", "assets", "search_icon.png")
LEFT_ARROW_ICON = os.path.join(ROOT_DIR, "src", "assets", "left_arrow_icon.png")
RIGHT_ARROW_ICON = os.path.join(ROOT_DIR, "src", "assets", "right_arrow_icon.png")
GENDER_ICON = os.path.join(ROOT_DIR, "src", "assets", "gender_icon.png")
BIRTHDAY_ICON = os.path.join(ROOT_DIR, "src", "assets", "birthday_date_icon.png")
USER_ICON = os.path.join(ROOT_DIR, "src", "assets", "user_icon.png")
POST_ICON = os.path.join(ROOT_DIR, "src", "assets", "post_icon.png")
STATUS_ICON = os.path.join(ROOT_DIR, "src", "assets", "status_icon.png")
CONTACTS_ICON = os.path.join(ROOT_DIR, "src", "assets", "contacts_icon.png")
SALARY_ICON = os.path.join(ROOT_DIR, "src", "assets", "salary_icon.png")
FLIGHT_ICON = os.path.join(ROOT_DIR, "src", "assets", "flight_icon.png")
DEPARTURE_DATE_ICON = os.path.join(ROOT_DIR, "src", "assets", "departure_date_icon.png")
ARRIVAL_DATE_ICON = os.path.join(ROOT_DIR, "src", "assets", "arrival_date_icon.png")
DEPARTURE_TIME_ICON = os.path.join(ROOT_DIR, "src", "assets", "departure_time_icon.png")
ARRIVAL_TIME_ICON = os.path.join(ROOT_DIR, "src", "assets", "arrival_time_icon.png")
BRIGADE_ICON = os.path.join(ROOT_DIR, "src", "assets", "brigade_icon.png")
CALENDAR_ICON = os.path.join(ROOT_DIR, "src", "assets", "calendar_icon.png")

# ==========================================================================
# Названия таблиц и полей
# ==========================================================================
TABLES = {
    "Сотрудники": {
        "columns": ("ID", "ФИО", "Пол", "Дата рождения", "Статус", "Должность", "Почта", "Макс. часы"),
        "fields": [
            ("ФИО:", "entry", None),
            ("Пол:", "combobox", ["М", "Ж"]),
            ("Дата рождения:", "entry", None),
            ("Должность:", "combobox", None),
            ("Почта:", "entry", None),
        ],
        "load_query": """
            SELECT e.ID_Employee, e.Full_Name, e.gender, e.birth_date, e.status, p.Name_Position, e.email, e.max_hours  
            FROM Employees e 
            LEFT JOIN Position p ON e.ID_Position = p.ID_Position
            ORDER BY e.ID_Employee
        """,
        "insert_query": "INSERT INTO Employees (Full_Name, gender, birth_date, ID_Position, email) VALUES (%s, %s, %s, (SELECT ID_Position FROM Position WHERE Name_Position=%s), %s)",
        "update_query": "UPDATE Employees SET Full_Name=%s, gender=%s, birth_date=%s, ID_Position=(SELECT ID_Position FROM Position WHERE Name_Position=%s), email=%s WHERE ID_Employee=%s",
        "delete_query": "DELETE FROM Employees WHERE ID_Employee=%s",
        "search_field": "Full_Name",
        "search_field_type": "string",
        "where_keys": [0]
    },
    "Должности": {
        "columns": ("ID", "Название должности", "Ставка за час"),
        "fields": [
            ("Название должности:", "entry", None),
            ("Ставка за час:", "entry", None)
        ],
        "load_query": "SELECT ID_Position, Name_Position, Salary FROM Position ORDER BY ID_Position",
        "insert_query": "INSERT INTO Position (Name_Position, Salary) VALUES (%s, %s)",
        "update_query": "UPDATE Position SET Name_Position=%s, Salary=%s WHERE ID_Position=%s",
        "delete_query": "DELETE FROM Position WHERE ID_Position=%s",
        "search_field": "Name_Position",
        "search_field_type": "string",
        "where_keys": [0]
    },
    "Рейсы": {
        "columns": ("ID", "Название рейса", "Продолжительность", "Дата отправления", "Дата прибытия", "Время отправления", "Время прибытия"),
        "fields": [
            ("Название рейса:", "entry", None),
            ("Дата отправления:", "entry", None),
            ("Дата прибытия:", "entry", None),
            ("Время отправления:", "entry", None),
            ("Время прибытия:", "entry", None)
        ],
        "load_query": "SELECT ID_Trip, Trip_Name, Duration, Departure_Date, Arrival_Date, Departure_Time, Arrival_Time FROM Trips ORDER BY ID_Trip",
        "insert_query": "INSERT INTO Trips (Trip_Name, Departure_Date, Arrival_Date, Departure_Time, Arrival_Time) VALUES (%s, %s, %s, %s, %s)",
        "update_query": "UPDATE Trips SET Trip_Name=%s, Departure_Date=%s, Arrival_Date=%s, Departure_Time=%s, Arrival_Time=%s WHERE ID_Trip=%s",
        "delete_query": "DELETE FROM Trips WHERE ID_Trip=%s",
        "search_field": "Trip_Name",
        "search_field_type": "string",
        "where_keys": [0]
    },
    "Состав бригады": {
        "columns": ("ID Бригады", "ФИО сотрудника", "Название рейса", "Название бригады", "Дата формирования"),
        "fields": [
            ("ID Бригады:", "entry", None),
            ("ФИО Сотрудника:", "combobox_autocomplete", None),  
            ("Название рейса:", "combobox_autocomplete", None),
            ("Название бригады:", "entry", None),
            ("Дата формирования:", "entry", None)
        ],
        "load_query": """
            SELECT bc.ID_Brigade, 
                   e.Full_Name || ' (' || e.ID_Employee || ')' AS Full_Name, 
                   t.Trip_Name || ' (' || t.ID_Trip || ')' AS Trip_Name, 
                   bc.Brigade_Name, 
                   bc.Formation_Date
            FROM Brigade_Composition bc
            LEFT JOIN Employees e ON bc.ID_Employee = e.ID_Employee
            LEFT JOIN Trips t ON bc.ID_Trip = t.ID_Trip
            ORDER BY bc.ID_Brigade, e.Full_Name
        """,
        "insert_query": """
            INSERT INTO Brigade_Composition (ID_Brigade, ID_Employee, ID_Trip, Brigade_Name, Formation_Date)
            VALUES (%s, %s, %s, %s, %s)
        """,
        "update_query": """
            UPDATE Brigade_Composition 
            SET ID_Brigade=%s, 
                ID_Employee=%s, 
                ID_Trip=%s, 
                Brigade_Name=%s, 
                Formation_Date=%s 
            WHERE ID_Brigade=%s AND ID_Employee=%s
        """,
        "delete_query": """
            DELETE FROM Brigade_Composition 
            WHERE ID_Brigade = %s AND ID_Employee = %s
        """,
        "search_field": "Brigade_Name",
        "search_field_type": "string",
        "where_keys": [0, 1]
    },
    "Календарь смен": {
        "columns": ("ID Бригады", "Дата начала", "Дата окончания", "ID Рейса"),
        "fields": [
            ("ID Бригады:", "entry", None),
            ("Дата начала:", "entry", None),
            ("Дата окончания:", "entry", None),
            ("ID Рейса:", "entry", None)
        ],
        "load_query": """
            SELECT sc.id_brigade, sc.start_date, sc.end_date, sc.id_trip, t.trip_name, t.arrival_time, bc.brigade_name
            FROM shift_calendar sc
            JOIN trips t ON sc.id_trip = t.id_trip
            LEFT JOIN brigade_composition bc ON sc.id_brigade = bc.id_brigade
        """,
        "insert_query": "INSERT INTO shift_calendar (id_brigade, start_date, end_date, id_trip) VALUES (%s, %s, %s, %s)",
        "update_query": "UPDATE shift_calendar SET id_brigade=%s, start_date=%s, end_date=%s, id_trip=%s WHERE id_brigade=%s AND start_date=%s AND end_date=%s",
        "delete_query": "DELETE FROM shift_calendar WHERE id_brigade=%s AND start_date=%s AND end_date=%s",
        "search_field": "sc.id_brigade",
        "search_field_type": "integer",
        "where_keys": [0, 1, 2]
    },
    "Учёт зарплаты": {
        "columns": ("ФИО Сотрудника", "Сумма", "Дата выплаты"),  
        "fields": [
            ("ФИО Сотрудника:", "combobox_autocomplete", None), 
            ("Сумма:", "entry", None),
            ("Дата выплаты:", "entry", None)
        ],
        "load_query": """
            SELECT e.Full_Name || ' (' || e.ID_Employee || ')' AS Full_Name, 
                p.Amount, 
                p.Payment_Date 
            FROM Payroll_Accounting p
            LEFT JOIN Employees e ON p.ID_Employee = e.ID_Employee
        """,
        "insert_query": "INSERT INTO Payroll_Accounting (ID_Employee, Amount, Payment_Date) VALUES (%s, %s, %s)",
        "update_query": "UPDATE Payroll_Accounting SET ID_Employee=%s, Amount=%s, Payment_Date=%s WHERE ID_Employee=%s AND Payment_Date=%s",
        "delete_query": "DELETE FROM Payroll_Accounting WHERE ID_Employee=%s AND Payment_Date=%s",
        "search_field": "e.Full_Name",  
        "search_field_type": "string", 
        "where_keys": [0, 2]
    }
}

# ==========================================================================
# Иконки для полей ввода
# ==========================================================================
ICON_MAPPING = {
    # Таблица "Сотрудники"
    "ФИО:": USER_ICON,
    "Должность:": POST_ICON,
    "Статус:": STATUS_ICON,
    "Почта:": CONTACTS_ICON,

    # Таблица "Должности"
    "Название должности:": POST_ICON,
    "Ставка за час:": SALARY_ICON,

    # Таблица "Рейсы"
    "Название рейса:": FLIGHT_ICON,
    "Дата отправления:": DEPARTURE_DATE_ICON,
    "Дата прибытия:": ARRIVAL_DATE_ICON,
    "Время отправления:": DEPARTURE_TIME_ICON,
    "Время прибытия:": ARRIVAL_TIME_ICON,
    
    # Таблица "Состав бригад"
    "ID Бригады:": BRIGADE_ICON,
    "ФИО сотрудника:": USER_ICON,
    "Название рейса:": FLIGHT_ICON,
    "Название бригады:": BRIGADE_ICON,
    "Дата формирования:": CALENDAR_ICON,

    # Таблица "Учет зарплаты"
    "Дата начала:": DEPARTURE_DATE_ICON,
    "Дата окончания:": ARRIVAL_DATE_ICON,
    "Сумма:": SALARY_ICON,
    "Дата выплаты:": CALENDAR_ICON
}

# ==========================================================================
# Названия месяцев
# ==========================================================================
MONTH_NAMES = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]

# ==========================================================================
# Дни недели
# ==========================================================================
DAYS_OF_WEEK = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

# Роли и доступные таблицы
ROLE_ACCESS = {
    "Кадровик": ["Главная", "Сотрудники", "Должности", "Состав бригады", "Календарь смен"],
    "Бухгалтер": ["Главная", "Сотрудники", "Учёт зарплаты"],
    "Сотрудник": ["Главная", "Календарь смен", "Учёт зарплаты"]
}
