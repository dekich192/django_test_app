from django import template
from django.urls import resolve, Resolver404
from django.utils.safestring import mark_safe
from django.db.models import Q
from ..models import MenuItem

register = template.Library()

@register.simple_tag(takes_context=True)
def draw_menu(context, menu_name):
    """
    Renders a hierarchical menu by its name.
    
    Args:
        context: The template context
        menu_name: The name of the menu to render (must match menu_name in MenuItem)
        
    Returns:
        Rendered HTML for the menu
    """
    request = context.get('request')
    if not request:
        return ''
        
    current_path = request.path
    
    # Get all active menu items for this menu
    menu_items = MenuItem.objects.filter(
        is_active=True,
        menu_name=menu_name
    ).order_by('order', 'title')
    
    if not menu_items.exists():
        return ''
    
    # Find the selected menu item based on the current URL
    selected_item = None
    best_match_length = 0
    
    for item in menu_items:
        if item.is_active_for_path(current_path):
            # Prefer the most specific (longest) URL match
            url_length = len(item.get_absolute_url())
            if url_length > best_match_length:
                selected_item = item
                best_match_length = url_length
    
    # Get all items that should be expanded
    expanded_items = set()
    if selected_item:
        # Add all ancestors of the selected item
        current = selected_item
        while current:
            expanded_items.add(current.id)
            current = current.parent
    
    # Also expand the first level by default if no item is selected
    if not expanded_items:
        expanded_items.update(menu_items.filter(parent__isnull=True).values_list('id', flat=True))
    
    # Render a single menu item and its children
    def render_menu_item(item, level=0):
        is_expanded = item.id in expanded_items
        has_children = item.children.exists()
        is_active = selected_item and (item == selected_item or item.id in expanded_items)
        
        # Build CSS classes
        classes = ['menu-item']
        if is_active:
            classes.append('active')
        if has_children:
            classes.append('has-children')
        if is_expanded:
            classes.append('expanded')
        
        # Start the list item
        html = f'<li class="{" ".join(classes)}">'
        
        # Add the link
        url = item.get_absolute_url()
        html += f'<a href="{url}" class="menu-link">{item.title}</a>'
        
        # Add children if any and if this item is expanded
        if has_children and is_expanded:
            children = item.children.filter(is_active=True).order_by('order', 'title')
            if children:
                html += '<ul class="submenu">'
                for child in children:
                    html += render_menu_item(child, level + 1)
                html += '</ul>'
        
        html += '</li>'
        return html
    
    # Start building the menu HTML
    menu_html = f'<nav class="menu menu-{menu_name}" data-menu-name="{menu_name}">\n<ul class="menu-root">\n'
    
    # Add the root items
    root_items = menu_items.filter(parent__isnull=True)
    for item in root_items:
        menu_html += render_menu_item(item)
    
    menu_html += '</ul>\n</nav>'
    
    return mark_safe(menu_html)


@register.inclusion_tag('menu/breadcrumbs.html', takes_context=True)
def breadcrumbs(context, menu_name=None):
    """
    Renders breadcrumbs for the current page based on menu structure.
    """
    request = context.get('request')
    if not request:
        return {'breadcrumbs': []}
        
    current_path = request.path
    breadcrumbs_list = []
    
    # Find the deepest matching menu item
    menu_items = MenuItem.objects.filter(
        is_active=True,
        menu_name=menu_name
    ) if menu_name else MenuItem.objects.filter(is_active=True)
    
    matching_items = []
    for item in menu_items:
        if item.is_active_for_path(current_path):
            matching_items.append(item)
    
    # Sort by URL length (longest first) to get the most specific match
    matching_items.sort(key=lambda x: len(x.get_absolute_url()), reverse=True)
    
    if matching_items:
        # Get the most specific match
        current_item = matching_items[0]
        
        # Build breadcrumbs by walking up the hierarchy
        while current_item:
            breadcrumbs_list.insert(0, {
                'title': current_item.title,
                'url': current_item.get_absolute_url(),
                'is_active': current_item == matching_items[0]
            })
            current_item = current_item.parent
    
    return {'breadcrumbs': breadcrumbs_list}
