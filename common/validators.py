from datetime import date
from rest_framework import serializers


def validate_user_age(request):
    birthdate = request.auth.get('birthdate') if request.auth else None

    if not birthdate:
        raise serializers.ValidationError(
            'Укажите дату рождения, чтобы создать продукт.'
        )

    birthdate = date.fromisoformat(birthdate)
    today = date.today()

    age = today.year - birthdate.year

    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1

    if age < 18:
        raise serializers.ValidationError(
            'Вам должно быть 18 лет, чтобы создать продукт.'
        )