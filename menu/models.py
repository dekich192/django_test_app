from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse, resolve, Resolver404
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class MenuItem(models.Model):
    """Model representing a menu item with hierarchical structure."""
    MENU_CHOICES = [
        ('main', _('Главное меню')),
        ('footer', _('Нижнее меню')),
        ('sidebar', _('Боковое меню')),
    ]
    
    title = models.CharField(max_length=100, verbose_name=_('Название'))
    menu_name = models.CharField(
        max_length=50,
        choices=MENU_CHOICES,
        default='main',
        verbose_name=_('Название меню'),
        help_text=_('Идентификатор меню для отображения в шаблонах')
    )
    url = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='URL',
        help_text=_('URL или именованный URL-шаблон (например: about или products:list)'),
        db_index=True
    )
    named_url = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Именованный URL'),
        help_text=_('Имя URL-шаблона (например: about или products:list)')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Родительский пункт меню')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Активно'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        verbose_name = _('Пункт меню')
        verbose_name_plural = _('Пункты меню')
        ordering = ['menu_name', 'order', 'title']
        unique_together = ('menu_name', 'url', 'parent')

    def __str__(self):
        return f"{self.title} ({self.get_menu_name_display()})"

    def clean(self):
        # Prevent circular references
        parent = self.parent
        while parent is not None:
            if parent == self:
                raise ValidationError(_('Обнаружена циклическая ссылка в меню'))
            parent = parent.parent

    def get_absolute_url(self):
        if self.named_url:
            try:
                return reverse(self.named_url)
            except:
                pass
        return self.url or '#'

    def is_active_for_path(self, path):
        """Check if this menu item is active for the given path."""
        if not self.is_active:
            return False
            
        # Check direct URL match
        if self.get_absolute_url() == path:
            return True
            
        # Check if this is a parent of the current page
        if self.url and path.startswith(self.url.rstrip('/') + '/'):
            return True
            
        # Check named URL pattern
        if self.named_url:
            try:
                resolved = resolve(path)
                if resolved.url_name == self.named_url or \
                   resolved.view_name == self.named_url:
                    return True
            except Resolver404:
                pass
                
        return False
