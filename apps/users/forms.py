from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django import forms




class _WidgetMixin:
    def _style(self):
        for name, field in self.fields.items():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (css + " input").strip()
            if not field.widget.attrs.get("placeholder"):
                field.widget.attrs["placeholder"] = field.label or name.title()

class CustomAuthenticationForm(AuthenticationForm, _WidgetMixin):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._style()

class CustomUserCreationForm(UserCreationForm, _WidgetMixin):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2", "role", "photo")

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        # приклад: заховати плейн-файл від потворних стилів браузера
        self.fields["photo"].widget.attrs["class"] = "input"
        self._style()