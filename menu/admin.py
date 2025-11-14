from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .models import MenuItem


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'menu_name_display', 'parent_link', 'url_display', 'is_active', 'order')
    list_filter = ('menu_name', 'is_active', 'parent')
    search_fields = ('title', 'url', 'named_url')
    list_editable = ('is_active', 'order')
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('title', 'menu_name')
        }),
        (_('Ссылка'), {
            'fields': ('url', 'named_url'),
            'description': _('Заполните либо URL, либо Именованный URL')
        }),
        (_('Иерархия и отображение'), {
            'fields': ('parent', 'is_active', 'order')
        }),
    )
    
    def menu_name_display(self, obj):
        return obj.get_menu_name_display()
    menu_name_display.short_description = _('Меню')
    menu_name_display.admin_order_field = 'menu_name'
    
    def url_display(self, obj):
        if obj.named_url:
            return f'[{obj.named_url}]'
        return obj.url or '—'
    url_display.short_description = _('URL')
    
    def parent_link(self, obj):
        if obj.parent:
            url = reverse('admin:menu_menuitem_change', args=[obj.parent.id])
            return mark_safe(f'<a href="{url}">{obj.parent.title}</a>')
        return "—"
    parent_link.short_description = _('Родительский пункт')
    parent_link.admin_order_field = 'parent__title'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            # Only show items from the same menu when selecting a parent
            obj_id = request.resolver_match.kwargs.get('object_id')
            if obj_id:
                current_menu = MenuItem.objects.filter(id=obj_id).values_list('menu_name', flat=True).first()
                if current_menu:
                    kwargs['queryset'] = MenuItem.objects.filter(menu_name=current_menu).exclude(id=obj_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(MenuItem, MenuItemAdmin)
