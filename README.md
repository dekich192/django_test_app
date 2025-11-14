
# Django Menu App

A reusable Django application for creating and managing hierarchical menus with dynamic URL resolution.

## Project Structure

```
django_test_app/
├── menu/                     # Menu application
│   ├── migrations/           # Database migrations
│   ├── templates/            # Template files
│   ├── templatetags/         # Custom template tags
│   ├── __init__.py
│   ├── admin.py              # Admin interface
│   ├── apps.py               # App config
│   ├── models.py             # Database models
│   └── urls.py               # URL configurations
└── menu_project/             # Project settings
    ├── __init__.py
    ├── settings.py           # Django settings
    ├── urls.py               # Main URL config
    └── wsgi.py               # WSGI config
```

---

## Styling

The menu uses semantic HTML and the following CSS classes:

* **`.menu`** — Main menu container
* **`.menu-item`** — Individual menu item
* **`.active`** — Highlights the active menu item
* **`.has-children`** — Indicates items that have submenus
* **`.expanded`** — Marks expanded submenu items

---

## Requirements

* **Python 3.6+**
* **Django 3.2+**

---

