"""
Django admin: asosiy kontent (zal, kategoriya, banner) faqat superuser tomonidan
o‘zgartiriladi. Oddiy `is_staff` foydalanuvchilar bu modellarni ko‘rmaydi va
o‘chira olmaydi — ma’lumotlar tasodifiy yoki noto‘g‘ri huquq orqali yo‘qolmaydi.
"""


class SuperuserOnlyModelAdminMixin:
    """Zallar, kategoriyalar, rasmlar, bannerlar — faqat superuser."""

    def has_module_permission(self, request):
        return bool(request.user.is_active and request.user.is_superuser)

    def has_add_permission(self, request):
        return bool(request.user.is_active and request.user.is_superuser)

    def has_change_permission(self, request, obj=None):
        return bool(request.user.is_active and request.user.is_superuser)

    def has_delete_permission(self, request, obj=None):
        return bool(request.user.is_active and request.user.is_superuser)

    def has_view_permission(self, request, obj=None):
        return bool(request.user.is_active and request.user.is_superuser)


class SuperuserDeleteOnlyMixin:
    """Ko‘rish/o‘zgartirish staff uchun mumkin; o‘chirish faqat superuser (moderatsiya)."""

    def has_delete_permission(self, request, obj=None):
        return bool(request.user.is_active and request.user.is_superuser)
