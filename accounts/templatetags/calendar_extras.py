from django import template
from django.utils import timezone
from urllib.parse import quote
from datetime import timedelta

register = template.Library()


def _safe_replace(d, year):
    try:
        return d.replace(year=year)
    except ValueError:
        return d.replace(year=year, day=28)


@register.filter
def google_calendar_url(birthday_date, user_name):
    if not birthday_date:
        return ''
    today = timezone.now().date()
    this_year_bd = _safe_replace(birthday_date, today.year)
    if this_year_bd < today:
        this_year_bd = _safe_replace(birthday_date, today.year + 1)
    end_day = this_year_bd + timedelta(days=1)
    title = f'День рождения {user_name}'
    details = 'Не забудьте поздравить!'
    url = (
        f'https://calendar.google.com/calendar/render'
        f'?action=TEMPLATE'
        f'&text={quote(title)}'
        f'&dates={this_year_bd.strftime("%Y%m%d")}/{end_day.strftime("%Y%m%d")}'
        f'&details={quote(details)}'
        f'&ctz=Europe/Moscow'
    )
    return url
