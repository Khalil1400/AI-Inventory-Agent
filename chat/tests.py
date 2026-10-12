from django.test import TestCase

from decimal import Decimal
from .models import Item
from .tools import calculate_cost
from .local_commands import run_local_command


class PriceTests(TestCase):
    def setUp(self):
        Item.objects.create(name='chocolate bar', quantity=10, price=Decimal('2.00'))

    def test_assignment_question_in_chat(self):
        response = self.client.post('/', {'message': 'what is the cost of 3 items of chocolate bar after adding 10% VAT'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('6.60 total', self.client.session['history'][-1]['text'])
        self.assertEqual(Item.objects.get(name='chocolate bar').quantity, 10)

    def test_rounding_and_plural(self):
        Item.objects.filter(name='chocolate bar').update(price=Decimal('1.99'))
        self.assertEqual(calculate_cost('chocolate bars', 3, 10)['total'], '6.57')

    def test_invalid_and_missing_data(self):
        self.assertIn('error', calculate_cost('unknown', 3, 10))
        self.assertIn('error', calculate_cost('chocolate bar', -1, 10))
        self.assertIn('error', calculate_cost('chocolate bar', 3, -10))
        Item.objects.filter(name='chocolate bar').update(price=0)
        self.assertIn('error', calculate_cost('chocolate bar', 3, 10))

    def test_set_price(self):
        run_local_command('set price of chocolate bar to 2.50')
        self.assertEqual(Item.objects.get(name='chocolate bar').price, Decimal('2.50'))
