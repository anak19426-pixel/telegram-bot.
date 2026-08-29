import os
import json
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Токен не найден в .env файле")

ADMIN_ID = 1240591787  # Ваш Telegram ID (замените на свой)

# ================== ТЕКСТЫ ==================
FAQ_TEXT = """*Часто задаваемые вопросы*

*1. Получение скидки:*  
_Скидка предоставляется на семестр для студентов очной формы обучения бакалавриата и магистратуры. Её размер - от 10% до 100% от стоимости обучения - зависит от места студента в рейтинге по итогам сессии._

*2. Что делать, если заболел во время сессии?*  
_Если вы пропустили зачёт или экзамен по болезни, для того чтобы неявка была признана уважительной, необходимо сразу после выздоровления предоставить справку Л. И. Карзаловой в кабинет 321._

*3. Где смотреть расписание занятий?*  
_Расписание занятий в первую очередь публикуется на сайте ruz.fa.ru. Для удобства его также можно смотреть в приложениях «Кампус»._

*4. Оплата материнским капиталом или образовательным кредитом:*  
_Для оплаты обучения с помощью материнского капитала или образовательного кредита необходимо сначала обратиться в кабинет 321 к Л. И. Карзаловой: для оформления кредита - за счётом, для использования маткапитала - за отсрочкой. После этого со счётом необходимо обратиться в московское отделение Сбербанка._

*5. Куда обратиться за получением справок?*  
_За справками нужно обращаться в студенческий офис (г. Москва, Ленинградский проспект, д. 53) или заказать их на сайте Финансового университета._

*6. Что такое Студенческий совет?*  
_Студенческий совет Финансового университета представляет интересы учащихся, способствует развитию их навыков, организует мероприятия и информирует студентов через медиаканалы._

*7. Что даёт участие в Студсовете?*  
_Участие в студенческом совете развивает профессиональные навыки и личные качества, которые ценятся работодателями, а также даёт возможность стать частью дружного коллектива._"""

STUDY_TEXT = """*Учебный процесс*

*Экзамены*  
Формат: письменный, устный или электронный (на компьютере в университете).  
Продолжительность:  
- письменный/электронный - 1,5 часа;  
- устный - 25 минут на подготовку и 10-12 минут на ответ.  
Дату экзамена назначает Студенческий офис (учебная часть).

*Правила*  
- На экзамене запрещены шпаргалки, неразрешённые материалы, телефоны, смарт-часы и другие средства связи.  
- За использование запрещённых материалов студент может быть удалён с экзамена и получить «неудовлетворительно» без пересдачи в основной период.  
- За нарушение порядка преподаватель может удалить студента с экзамена.  
- При себе необходимо иметь паспорт или другой документ, удостоверяющий личность.  
- При опоздании время экзамена не продлевается.  
- Если студент проспал или опоздал по неуважительной причине, возможность сдачи с другой группой решается индивидуально.

*Баллы*  
Максимум за дисциплину - 100 баллов:  
- 40 баллов - работа в семестре (2 ТКУ по 20 баллов);  
- 60 баллов - экзамен или зачёт.  
По дисциплине с экзаменом итоговые баллы переводятся в 5-балльную оценку. По зачёту выставляется «зачтено» или «не зачтено».

*Апелляция*  
Апелляция подаётся при:  
- технической ошибке в подсчёте баллов;  
- ошибке или неоднозначности в задании;  
- нарушении установленной процедуры экзамена.  
Несогласие с полученной оценкой само по себе основанием для апелляции не является.  
Апелляция подаётся в установленные сроки, обычно в течение 1-2 рабочих дней после объявления результатов.

*Пересдача*  
При оценке «неудовлетворительно» студент направляется на пересдачу.  
Периоды пересдач:  
- зимний - конец января;  
- летний - конец августа.  
Если экзамен не сдан после пересдачи, студент направляется на комиссию. При повторном неудовлетворительном результате возможно отчисление за академическую неуспеваемость.

*Контакты*  
*Деканат*  
Верхняя Масловка, 15  
8 (495) 249-53-00  
hsm@fa.ru  
Пн-пт: 09:00-18:00, сб: 09:00-13:30

*Учебный отдел:* 6648, 5323, 5372  
*Партнёры:* 5266, 1941  
*Научная работа:* 6644  
*Воспитательная работа:* 5343, 5344

*Студенческий офис*  
Ленинградский проспект, 53  
Помощь со справками, документами, переводами, расписанием, академическим отпуском, пересдачами и учебными вопросами.

*Охрана / пропуск*  
+7 (499) 553-13-82  
Утеря, кража или поломка электронной карты.

*Международный отдел*  
inter@fa.ru"""

WELCOME_TEXT = """Привет, студент!

Этот бот был создан Студенческим советом ВШУ, чтобы сделать твоё обучение комфортнее. Здесь ты можешь:

- задать вопрос по учёбе;
- сообщить о поломке в корпусе (сломанная мебель, неработающий свет и др.).

Просто выбери нужную опцию в меню и напиши свой вопрос, а мы постараемся помочь. Ответ придёт в течение 2-х дней.

В случае использования нецензурной лексики, оскорблений, некорректных формулировок или предоставления ложной информации, сообщение будет заблокировано, и ответа не последует.
Бот гарантирует полную конфиденциальность и анонимность при выборе этой опции.

Твой вклад важен - вместе мы сделаем учёбу комфортнее!"""

# ================== РАБОТА С ФАЙЛОМ ==================
QUESTIONS_FILE = "questions.json"

def load_questions():
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_questions(qs):
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(qs, f, ensure_ascii=False, indent=2)

# ================== БОТ ==================
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================== КЛАВИАТУРЫ ==================
def main_keyboard(user_id):
    kb = [
        [InlineKeyboardButton(text="📝 Задать вопрос", callback_data="ask_study")],
        [InlineKeyboardButton(text="🔧 Сообщить о поломке", callback_data="ask_repair")],
        [InlineKeyboardButton(text="❓ FAQ", callback_data="faq")],
        [InlineKeyboardButton(text="📚 Учебный процесс", callback_data="study")],
    ]
    if user_id == ADMIN_ID:
        kb.append([InlineKeyboardButton(text="⚙️ Админ-панель", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def admin_keyboard():
    kb = [
        [InlineKeyboardButton(text="📋 Вопросы по учёбе", callback_data="list_study")],
        [InlineKeyboardButton(text="🔧 Заявки о поломках", callback_data="list_repair")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def question_buttons(questions, prefix):
    kb = []
    for q in questions:
        if q.get("status") != "новый":
            continue
        text = q.get("text", "")[:25]
        if len(q.get("text", "")) > 25:
            text += "..."
        kb.append([InlineKeyboardButton(text=text, callback_data=f"{prefix}_{q.get('id')}")])
    if not kb:
        kb.append([InlineKeyboardButton(text="❌ Нет вопросов", callback_data="noop")])
    kb.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ================== СОСТОЯНИЯ ==================
waiting_question = {}  # {user_id: category}
waiting_answer = {}    # {admin_id: question_id}

# ================== КОМАНДЫ ==================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(WELCOME_TEXT, reply_markup=main_keyboard(message.from_user.id))

@dp.message(Command("admin"))
async def admin_cmd(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await show_admin(message)
    else:
        await message.answer("❌ Нет доступа.")

async def show_admin(message: types.Message):
    qs = load_questions()
    new_cnt = len([q for q in qs if q.get("status") == "новый"])
    ans_cnt = len([q for q in qs if q.get("status") == "отвечен"])
    await message.answer(
        f"⚙️ Админ-панель\n\nНовых: {new_cnt}\nОтвечено: {ans_cnt}",
        reply_markup=admin_keyboard()
    )

# ================== CALLBACK ==================
@dp.callback_query()
async def callback(call: types.CallbackQuery):
    data = call.data
    user_id = call.from_user.id

    # ---- ГЛАВНОЕ МЕНЮ ----
    if data == "ask_study":
        waiting_question[user_id] = "study"
        await call.message.edit_text("📝 Напишите свой вопрос. Отмена: /cancel")
        await call.answer()
        return

    if data == "ask_repair":
        waiting_question[user_id] = "repair"
        await call.message.edit_text("📸 Отправьте фото поломки и напишите место (например, 440 кабинет). Отмена: /cancel")
        await call.answer()
        return

    if data == "faq":
        await call.message.edit_text(FAQ_TEXT, parse_mode="Markdown")
        await call.message.answer("🔙 Меню:", reply_markup=main_keyboard(user_id))
        await call.answer()
        return

    if data == "study":
        await call.message.edit_text(STUDY_TEXT, parse_mode="Markdown")
        await call.message.answer("🔙 Меню:", reply_markup=main_keyboard(user_id))
        await call.answer()
        return

    # ---- АДМИН ----
    if data == "admin_panel":
        if user_id != ADMIN_ID:
            await call.answer("❌ Доступ запрещён", show_alert=True)
            return
        await show_admin(call.message)
        await call.answer()
        return

    if data == "back_to_main":
        await call.message.edit_text("🔙 Главное меню:", reply_markup=main_keyboard(user_id))
        await call.answer()
        return

    if data == "back_to_admin":
        await show_admin(call.message)
        await call.answer()
        return

    if data == "noop":
        await call.answer()
        return

    # ---- СПИСКИ ----
    if data == "list_study":
        if user_id != ADMIN_ID:
            await call.answer("❌ Нет доступа", show_alert=True)
            return
        qs = load_questions()
        qs_study = [q for q in qs if q.get("status") == "новый" and q.get("category") == "study"]
        await call.message.edit_text(
            "📋 Вопросы по учёбе:",
            reply_markup=question_buttons(qs_study, "answer_study")
        )
        await call.answer()
        return

    if data == "list_repair":
        if user_id != ADMIN_ID:
            await call.answer("❌ Нет доступа", show_alert=True)
            return
        qs = load_questions()
        qs_repair = [q for q in qs if q.get("status") == "новый" and q.get("category") == "repair"]
        await call.message.edit_text(
            "🔧 Заявки о поломках:",
            reply_markup=question_buttons(qs_repair, "answer_repair")
        )
        await call.answer()
        return

    # ---- СТАТИСТИКА ----
    if data == "stats":
        if user_id != ADMIN_ID:
            await call.answer("❌ Нет доступа", show_alert=True)
            return
        qs = load_questions()
        new_cnt = len([q for q in qs if q.get("status") == "новый"])
        ans_cnt = len([q for q in qs if q.get("status") == "отвечен"])
        new_study = len([q for q in qs if q.get("status") == "новый" and q.get("category") == "study"])
        new_repair = len([q for q in qs if q.get("status") == "новый" and q.get("category") == "repair"])
        await call.message.edit_text(
            f"📊 Статистика\n\nНовых: {new_cnt}\nОтвечено: {ans_cnt}\n\nВопросов: {new_study}\nПоломок: {new_repair}",
            reply_markup=admin_keyboard()
        )
        await call.answer()
        return

    # ---- ОТВЕТ НА ВОПРОС ----
    if data.startswith("answer_study_"):
        if user_id != ADMIN_ID:
            await call.answer("❌ Нет доступа", show_alert=True)
            return
        q_id = int(data.split("_")[2])
        qs = load_questions()
        q = None
        for item in qs:
            if item.get("id") == q_id and item.get("status") == "новый":
                q = item
                break
        if not q:
            await call.message.edit_text("❌ Вопрос уже обработан.", reply_markup=admin_keyboard())
            await call.answer()
            return
        waiting_answer[ADMIN_ID] = q_id
        await call.message.edit_text(
            f"✍️ Введите ответ на вопрос:\n\n{q.get('text')}\n\n(/cancel_answer - отмена)"
        )
        await call.answer()
        return

    if data.startswith("answer_repair_"):
        if user_id != ADMIN_ID:
            await call.answer("❌ Нет доступа", show_alert=True)
            return
        q_id = int(data.split("_")[2])
        qs = load_questions()
        q = None
        for item in qs:
            if item.get("id") == q_id and item.get("status") == "новый":
                q = item
                break
        if not q:
            await call.message.edit_text("❌ Заявка уже обработана.", reply_markup=admin_keyboard())
            await call.answer()
            return
        if q.get("photo_id"):
            try:
                await bot.send_photo(user_id, photo=q.get("photo_id"), caption=f"📍 {q.get('text')}")
            except Exception as e:
                logging.error(f"Ошибка отправки фото: {e}")
        waiting_answer[ADMIN_ID] = q_id
        await call.message.edit_text(
            f"✍️ Введите ответ на заявку:\n\n{q.get('text')}\n\n(/cancel_answer - отмена)"
        )
        await call.answer()
        return

    await call.answer()

# ================== ОБРАБОТКА СООБЩЕНИЙ ==================
@dp.message(Command("cancel"))
async def cancel(message: types.Message):
    if message.from_user.id in waiting_question:
        del waiting_question[message.from_user.id]
        await message.answer("❌ Отменено.", reply_markup=main_keyboard(message.from_user.id))

@dp.message(Command("cancel_answer"))
async def cancel_answer(message: types.Message):
    if message.from_user.id == ADMIN_ID and ADMIN_ID in waiting_answer:
        del waiting_answer[ADMIN_ID]
        await message.answer("❌ Ответ отменён.", reply_markup=admin_keyboard())

@dp.message(lambda m: m.from_user.id in waiting_question)
async def receive_question(message: types.Message):
    user_id = message.from_user.id
    category = waiting_question.pop(user_id, "study")
    qs = load_questions()
    new_id = max([q.get("id", 0) for q in qs], default=0) + 1

    if category == "repair":
        if not message.photo:
            await message.answer("❌ Отправьте ФОТО поломки.")
            waiting_question[user_id] = "repair"
            return
        photo = message.photo[-1]
        caption = message.caption or "Без описания"
        qs.append({
            "id": new_id,
            "user_id": user_id,
            "category": "repair",
            "text": caption,
            "photo_id": photo.file_id,
            "answer": "",
            "status": "новый"
        })
        save_questions(qs)
        await message.answer("✅ Заявка принята! Администратор ответит.", reply_markup=main_keyboard(user_id))
        try:
            await bot.send_photo(ADMIN_ID, photo=photo.file_id, caption=f"🔧 Новая поломка!\n📍 {caption}")
            await bot.send_message(ADMIN_ID, "📢 Зайдите в админ-панель.")
        except Exception as e:
            logging.error(f"Ошибка: {e}")
    else:
        text = message.text
        if not text:
            await message.answer("❌ Напишите текст вопроса.")
            waiting_question[user_id] = "study"
            return
        qs.append({
            "id": new_id,
            "user_id": user_id,
            "category": "study",
            "text": text,
            "photo_id": None,
            "answer": "",
            "status": "новый"
        })
        save_questions(qs)
        await message.answer("✅ Вопрос принят! Ответ будет в течение 2 дней.", reply_markup=main_keyboard(user_id))
        await bot.send_message(ADMIN_ID, f"📚 Новый вопрос:\n{text}\n📢 Зайдите в админ-панель.")

@dp.message(lambda m: m.from_user.id == ADMIN_ID and ADMIN_ID in waiting_answer)
async def receive_answer(message: types.Message):
    q_id = waiting_answer.pop(ADMIN_ID, None)
    if not q_id:
        await message.answer("❌ Нет активного вопроса.")
        return
    qs = load_questions()
    q = None
    for item in qs:
        if item.get("id") == q_id:
            q = item
            break
    if not q:
        await message.answer("❌ Вопрос не найден.")
        return
    q["answer"] = message.text
    q["status"] = "отвечен"
    save_questions(qs)
    try:
        if q.get("category") == "repair":
            text = f"✅ Ответ на заявку о поломке:\n📍 {q.get('text')}\n\n{message.text}"
        else:
            text = f"✅ Ответ на вопрос:\n{q.get('text')}\n\n{message.text}"
        await bot.send_message(q.get("user_id"), text)
        await message.answer("✅ Ответ отправлен!")
    except Exception as e:
        await message.answer(f"⚠️ Ответ сохранён, но не отправлен: {e}")
    await message.answer("🔙 Вернуться в админ-панель:", reply_markup=admin_keyboard())

# ================== ЗАПУСК ==================
async def main():
    if not os.path.exists(QUESTIONS_FILE):
        save_questions([])
    logging.info("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())