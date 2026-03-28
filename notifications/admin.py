from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from sporton_backend.admin_mixins import SuperuserOnlyModelAdminMixin
from .models import Notification, NotificationRecipient

User = get_user_model()


class CheckboxUserWidget(forms.CheckboxSelectMultiple):
    """Checkboxli foydalanuvchi tanlash widget-i — 'Barchasini tanlash' tugmasi bilan."""

    def render(self, name, value, attrs=None, renderer=None):
        original = super().render(name, value, attrs, renderer)
        select_all_id = f"select_all_{name}"
        html = f"""
        <div class="checkbox-users-wrapper">
            <div style="margin-bottom:10px; padding:10px 12px; background:#f0f6ff;
                        border-radius:8px; border:1.5px solid #c7deff; display:flex; align-items:center; gap:10px;">
                <input type="checkbox" id="{select_all_id}"
                       style="width:17px;height:17px;accent-color:#0057d9;cursor:pointer;"
                       onchange="
                           var checks = document.querySelectorAll('[name={name}]');
                           checks.forEach(function(c) {{ c.checked = this.checked; }}.bind(this));
                       ">
                <label for="{select_all_id}"
                       style="font-weight:800; font-size:14px; color:#0057d9; cursor:pointer; user-select:none;">
                    ✅ Barchasini tanlash / Tanlashni bekor qilish
                </label>
            </div>
            <div class="checkbox-users-list" style="
                max-height:320px; overflow-y:auto; border:1.5px solid #e2e8f0;
                border-radius:10px; padding:8px 4px; background:#fafbfc;">
                {original}
            </div>
            <div style="margin-top:8px; font-size:12px; color:#6b7280;">
                <span id="selected_count_{name}">0</span> ta tanlandi
            </div>
        </div>
        <script>
        (function() {{
            function updateState() {{
                var checks = document.querySelectorAll('[name={name}]');
                var count = Array.from(checks).filter(function(c) {{ return c.checked; }}).length;
                var el = document.getElementById('selected_count_{name}');
                if (el) el.textContent = count;
                
                // Update select-all state
                var allBox = document.getElementById('{select_all_id}');
                if (allBox) {{
                    allBox.checked = count === checks.length && checks.length > 0;
                    allBox.indeterminate = count > 0 && count < checks.length;
                }}

                // --- Button Logic ---
                var isSendToAll = document.querySelector('[name=send_to_all]') ? document.querySelector('[name=send_to_all]').checked : false;
                var saveBtn = document.querySelector('input[name="_save"]');
                if (saveBtn) {{
                    saveBtn.value = "📤 Yuborish (Send)";
                    if (isSendToAll || count > 0) {{
                        saveBtn.disabled = false;
                        saveBtn.style.opacity = '1';
                        saveBtn.style.cursor = 'pointer';
                    }} else {{
                        saveBtn.disabled = true;
                        saveBtn.style.opacity = '0.5';
                        saveBtn.style.cursor = 'not-allowed';
                    }}
                }}
            }}

            function initAdminUI() {{
                var addAnother = document.querySelector('input[name="_addanother"]');
                var continueEditing = document.querySelector('input[name="_continue"]');
                if (addAnother) addAnother.style.display = 'none';
                if (continueEditing) continueEditing.style.display = 'none';
                updateState();
            }}

            document.addEventListener('change', function(e) {{
                if (
                    (e.target && e.target.name === '{name}') || 
                    (e.target && e.target.name === 'send_to_all') ||
                    (e.target && e.target.id === '{select_all_id}')
                ) {{
                    updateState();
                }}
            }});
            
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', initAdminUI);
            }} else {{
                initAdminUI();
            }}
        }})();
        </script>
        """
        return mark_safe(html)


class NotificationAdminForm(forms.ModelForm):
    send_to_all = forms.BooleanField(
        required=False,
        initial=True,
        label="📣 Barchaga jo'natish",
        help_text="Bu belgilangan bo'lsa barcha ro'yxatdan o'tgan foydalanuvchilarga yuboriladi. "
                  "Olib tashlasangiz, quyidan alohida foydalanuvchilarni belgilaysiz.",
    )
    specific_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by('username'),
        required=False,
        label="👥 Foydalanuvchilarni tanlang",
        help_text="'Barchaga jo'natish' ni olib tashlang va kerakli foydalanuvchilarni belgilang.",
        widget=CheckboxUserWidget,
    )

    class Meta:
        model = Notification
        fields = ('title', 'message', 'from_user', 'send_to_all', 'specific_users')

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Django formlarida save_m2m avtomatik yaratiladi, lekin bu forma-da explicit m2m yo'q
        return instance


@admin.register(Notification)
class NotificationAdmin(SuperuserOnlyModelAdminMixin, admin.ModelAdmin):
    form = NotificationAdminForm
    list_display  = ('id', 'title', 'recipients_count', 'created_at')
    search_fields = ('title', 'message')
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        # Asosiy obyektni saqlaymiz
        super().save_model(request, obj, form, change)
        
        # Recipients ni yaratish (frontendga notification yetib borishi uchun muhim!)
        send_to_all = form.cleaned_data.get('send_to_all', True)
        specific_users = form.cleaned_data.get('specific_users')

        if send_to_all or not specific_users:
            users = User.objects.all()
        else:
            users = specific_users

        # Eski qabul qiluvchilarni tozalab, yangidan qo'shamiz
        NotificationRecipient.objects.filter(notification=obj).delete()
        recipients = [
            NotificationRecipient(notification=obj, user=u) for u in users
        ]
        if recipients:
            NotificationRecipient.objects.bulk_create(
                recipients, batch_size=200, ignore_conflicts=True
            )

    @admin.display(description='Yuborilganlar soni')
    def recipients_count(self, obj):
        count = obj.recipients.count()
        color = '#22c55e' if count > 0 else '#9ca3af'
        return format_html(
            '<span style="font-weight:800;color:{};">👥 {} ta</span>',
            color, count,
        )


@admin.register(NotificationRecipient)
class NotificationRecipientAdmin(SuperuserOnlyModelAdminMixin, admin.ModelAdmin):
    list_display  = ('id', 'notification', 'user', 'is_read', 'read_at')
    list_filter   = ('is_read', 'notification')
    search_fields = ('user__username', 'notification__title')
    readonly_fields = ('notification', 'user', 'is_read', 'read_at')

    def has_add_permission(self, request):
        return False
