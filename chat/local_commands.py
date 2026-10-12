import re

from django.db import transaction
from .models import Item


def find_item(name):
    item = Item.objects.filter(name__iexact=name).first()
    if item is not None:
        return item
    # Reuse an existing singular/plural label, e.g. Hammer and hammers.
    alternate = name[:-1] if name.lower().endswith('s') else name + 's'
    return Item.objects.filter(name__iexact=alternate).first()


def run_local_command(message):
    text = message.strip().rstrip('.!?').strip()
    price_command = re.fullmatch(r'set price of (.+?) to (\d+(?:\.\d{1,2})?)', text, re.IGNORECASE)
    if price_command:
        from decimal import Decimal
        name, price = price_command.groups()
        item = find_item(name.strip())
        if item is None:
            return f'No item named {name} is in the inventory.'
        value = Decimal(price)
        if not 0 < value <= Decimal('99999999.99'):
            return 'Price must be positive and no greater than 99999999.99.'
        item.price = value
        item.save(update_fields=['price'])
        return f'Price of {item.name} set to {value:.2f} per item.'
    cost_command = re.fullmatch(r'(?:what is the |what\'s the )?cost of (\d+) (?:items? of )?(.+?) (?:after adding|with|including) (\d+(?:\.\d+)?)\s*%\s*VAT', text, re.IGNORECASE)
    if cost_command:
        from .tools import calculate_cost
        quantity, name, vat = cost_command.groups()
        result = calculate_cost(name.strip(), int(quantity), vat)
        if 'error' in result:
            return result['error']
        return (f"Price: {result['subtotal']}. VAT: {result['vat']}. "
                f"{result['total']} total.")
    command = re.fullmatch(r'(?:please\s+)?(add|remove)\s+([+-]?\d+)\s+(.+?)(?:\s+(?:to|from)\s+(?:(?:the|my)\s+)?(?:inventory|stock))?', text, re.IGNORECASE)
    if command:
        action, amount, name = command.groups()
        quantity = int(amount)
        name = name.strip()
        if not name or len(name) > 100 or not 0 < quantity <= 2147483647:
            return 'Use an item name up to 100 characters and a positive whole-number quantity.'
        with transaction.atomic():
            item = find_item(name)
            if action.lower() == 'add':
                if item:
                    if item.quantity + quantity > 2147483647:
                        return 'That quantity is too large.'
                    item.quantity += quantity
                    item.save(update_fields=['quantity'])
                else:
                    item = Item.objects.create(name=name, quantity=quantity)
                return f'Added {quantity} {item.name}. Total in stock: {item.quantity}.'
            if item is None:
                return f'No item named {name} is in the inventory.'
            if quantity > item.quantity:
                return f'Cannot remove {quantity}. Only {item.quantity} {item.name} in stock.'
            item.quantity -= quantity
            item.save(update_fields=['quantity'])
            return f'Removed {quantity} {item.name}. Remaining: {item.quantity}.'
    if text.lower() in ('list', 'list items', 'list inventory', 'show inventory', 'show stock', 'inventory', 'what is in stock', "what's in stock"):
        items = Item.objects.order_by('name')
        return '; '.join(f'{item.name}: {item.quantity}' for item in items) or 'The inventory is empty.'
    lookup = re.fullmatch(r'(?:check(?: stock(?: of| for)?)?|how many)\s+(.+?)(?:\s+(?:do we have|are in stock))?', text, re.IGNORECASE)
    if lookup:
        name = lookup.group(1).strip()
        item = find_item(name)
        return f'{item.name}: {item.quantity} in stock.' if item else f'No item named {name} is in the inventory.'
    return None
