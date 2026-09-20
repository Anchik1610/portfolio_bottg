# 🚀 Telegram Bot — Портфолио проектов

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![SQLite](https://img.shields.io/badge/SQLite-Database-green?style=for-the-badge&logo=sqlite)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram)
![Status](https://img.shields.io/badge/Status-В_разработке-orange?style=for-the-badge)

**Умный бот для ведения личного портфолио проектов**  
Создавай • Отслеживай • Управляй своими pet-проектами прямо в Telegram

</div>

---

## ✨ О проекте

Это Telegram-бот, который помогает разработчику вести **портфолио своих проектов**.  
Вместо таблиц в Excel или заметок в Notion — всё под рукой в удобном чате.

### Что умеет бот:

| Функция | Описание |
|--------|----------|
| 📁 **Проекты** | Добавляй, редактируй и удаляй проекты |
| 🏷️ **Статусы** | Отслеживай этап: от идеи до релиза |
| 🛠️ **Навыки** | Привязывай технологии к каждому проекту |
| 📊 **Информация** | Быстрый просмотр полной карточки проекта |
| 🗑️ **Очистка** | Удаляй ненужное одной командой |

---

## 🗄️ Структура базы данных

```text
📦 Portfolio DB
 ┣ 📋 Status          — статусы проектов
 ┣ 📁 Project         — сами проекты
 ┣ 🛠️ Skill           — справочник навыков
 ┗ 🔗 ProjectSkill    — связь проектов и навыков
