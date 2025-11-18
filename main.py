import os
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont, ImageFilter


# СЛУЖБОВІ ФУНКЦІЇ

def safe_open_image(path: str) -> Image.Image | None: # Безпечно відкриває зображення. Повертає об’єкт Image або None, якщо файл не знайдено чи формат некоректний.
    try:
        img = Image.open(path)
        img = img.convert("RGBA")  # Уніфікуємо режим.
        return img
    except FileNotFoundError:
        print(f"!!! Файл '{path}' не знайдено.")
    except OSError:
        print(f"!!! Файл '{path}' не є коректним зображенням.")
    return None


def ask_existing_path(prompt: str) -> str: # Запитує в користувача шлях до файлу, доки він не вкаже існуючий.
    while True:
        path = input(prompt).strip().strip('"')
        if os.path.isfile(path):
            return path
        print("!!! Файл за вказаним шляхом не знайдено. Спробуйте ще раз.")


def choose_from_menu(prompt: str, options: dict) -> str: # Дає користувачу вибір із меню.
    while True:
        print(prompt)
        for key, desc in options.items():
            print(f"  {key} – {desc}")
        choice = input("Ваш вибір: ").strip()
        if choice in options:
            return choice
        print("!!! Неккоректний вибір. Спробуйте ще раз.\n")


# ОБРОБКА ЗОБРАЖЕНЬ

def resize_to_fit(img: Image.Image, max_width: int, max_height: int) -> Image.Image: # Масштабує зображення пропорційно.
    img_copy = img.copy()
    img_copy.thumbnail((max_width, max_height), Image.LANCZOS)
    return img_copy


def apply_filter(img: Image.Image, filter_choice: str) -> Image.Image: # Застосовує до зображення обраний фільтр.
    if filter_choice == "2":
        return img.convert("L").convert("RGBA")
    elif filter_choice == "3":
        return img.filter(ImageFilter.GaussianBlur(radius=3))
    elif filter_choice == "4":
        return img.filter(ImageFilter.CONTOUR)
    return img


def add_text_centered(
    img: Image.Image,
    text: str,
    y: int,
    font_path: str | None = None,
    font_size: int = 40,
    fill=(255, 255, 255, 255)
) -> None: # Додає текст по центру зображення по осі X на висоті y.
    draw = ImageDraw.Draw(img)

    # Підбір шрифту
    if font_path and os.path.isfile(font_path):
        try:
            font = ImageFont.truetype(font_path, font_size)
        except OSError:
            print("!!! Не вдалося завантажити вказаний шрифт. Використовую стандартний.")
            font = ImageFont.load_default()
    else:
        font = ImageFont.load_default()

    # Обчислення розміру тексту
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        text_width, text_height = draw.textsize(text, font=font)

    x = (img.width - text_width) // 2
    draw.text((x, y), text, font=font, fill=fill)


def paste_photo_on_background(
    background: Image.Image,
    photo: Image.Image,
    position: str = "right_bottom",
    scale: float = 0.4
) -> None: # Вставляє фото на фон у вказане місце. 
    max_width = int(background.width * scale)
    max_height = int(background.height * scale)
    resized = resize_to_fit(photo, max_width, max_height)

    if position == "left_top":
        x, y = 20, 20
    elif position == "right_top":
        x, y = background.width - resized.width - 20, 20
    elif position == "left_bottom":
        x, y = 20, background.height - resized.height - 20
    else:
        x, y = background.width - resized.width - 20, background.height - resized.height - 20

    background.alpha_composite(resized, (x, y))


# ЗБЕРЕЖЕННЯ РЕЗУЛЬТАТІВ 

def save_result_image(img: Image.Image, output_path: str) -> None: # Зберігає результуюче зображення у файл.
    try:
        img.convert("RGB").save(output_path)
        print(f"Листівка збережена у файл: {output_path}")
    except OSError as e:
        print(f"!!! Не вдалося зберегти зображення: {e}")


def save_report_txt(output_image_path: str, user_params: dict, report_path: str) -> None: # Зберігає текстовий звіт із параметрами створення листівки.
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("ЗВІТ ПРО СТВОРЕННЯ ЛИСТІВКИ\n")
            f.write("=" * 40 + "\n")
            f.write(f"Час створення: {datetime.now()}\n")
            f.write(f"Файл з листівкою: {output_image_path}\n\n")
            f.write("Використані параметри:\n")
            for key, value in user_params.items():
                f.write(f"- {key}: {value}\n")
        print(f"Звіт збережено у файл: {report_path}")
    except OSError as e:
        print(f"!!! Не вдалося зберегти звіт: {e}")


# ГОЛОВНА ЛОГІКА ПРОГРАМИ 

def create_personal_card() -> None: # Основна функція, яка організовує діалог з користувачем та створення персоналізованої листівки.
    print("ПРОГРАМА СТВОРЕННЯ ЛИСТІВКИ\n")

    # 1. Ввід вихідних даних.
    bg_path = ask_existing_path("Введіть шлях до фонового зображення: ")
    background = safe_open_image(bg_path)
    if background is None:
        print("!!! Неможливо продовжити без фонового зображення.")
        return

    background = resize_to_fit(background, 1200, 800)

    name = input("Введіть ім'я одержувача: ").encode("utf-8", "ignore").decode("utf-8").strip()
    message = input("Введіть коротке привітання/повідомлення: ").strip()

    # Додаткове фото.
    photo_choice = choose_from_menu(
        "\nБажаєте додати особисте фото на листівку?",
        {"1": "Так", "2": "Ні"}
    )

    user_photo = None
    if photo_choice == "1":
        photo_path = ask_existing_path("Введіть шлях до фотографії: ")
        user_photo = safe_open_image(photo_path)
        if user_photo is None:
            print("!!! Фото не буде використане через помилку читання.")

    # Вибір фільтра.
    filter_choice = choose_from_menu(
        "\nОберіть фільтр для фонового зображення:",
        {
            "1": "Без фільтру",
            "2": "Чорно-білий",
            "3": "Розмивання",
            "4": "Контур"
        }
    )

    # Позиція фото, якщо воно є.
    position_choice = "4"
    if user_photo is not None:
        position_choice = choose_from_menu(
            "\nОберіть розташування фото:",
            {
                "1": "Лівий верхній кут",
                "2": "Правий верхній кут",
                "3": "Лівий нижній кут",
                "4": "Правий нижній кут"
            }
        )

    # Шлях для збереження.
    default_output = "postcard.png"
    output_path = input(
        f"\nВведіть ім'я файлу для збереження листівки "
        f"(за замовчуванням {default_output}): "
    ).strip()
    if not output_path:
        output_path = default_output

    # 2. Обробка зображення.
    print("\nОбробка фонового зображення...")
    card = apply_filter(background, filter_choice)

    # 3. Додавання фото (якщо є).
    if user_photo is not None:
        print("Додаємо фото на листівку...")
        pos_map = {
            "1": "left_top",
            "2": "right_top",
            "3": "left_bottom",
            "4": "right_bottom"
        }
        paste_photo_on_background(card, user_photo, position=pos_map[position_choice])

    # 4. Додавання тексту.
    print("Додаємо текст...")
    font_path = None
    y_offset = 40

    if name:
        add_text_centered(card, f"Для {name}", y_offset, font_path, font_size=45)
        y_offset += 70

    if message:
        add_text_centered(card, message, y_offset, font_path, font_size=35)

    # 5. Збереження результатів.
    save_result_image(card, output_path)

    # Звіт.
    report_name = os.path.splitext(output_path)[0] + "_report.txt"
    params = {
        "Фонове зображення": bg_path,
        "Ім'я одержувача": name if name else "(не вказано)",
        "Повідомлення": message if message else "(не вказано)",
        "Було додано фото": "так" if user_photo is not None else "ні",
        "Використаний фільтр": filter_choice,
        "Позиція фото": position_choice if user_photo is not None else "(немає фото)"
    }
    save_report_txt(output_path, params, report_name)

    print("\nГотово! Листівка успішно створена.")


# ТОЧКА ВХОДУ 

if __name__ == "__main__":
    try:
        create_personal_card()
    except Exception as e:
        # Загальний «страхувальний» обробник на випадок неочікуваних помилок
        print("\n Під час виконання програми сталася непередбачена помилка:")
        print(e)
        print("Програма буде завершена.")