from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages

class PaymentTests(TestCase):
    def setUp(self):
        self.payment_url = reverse('payment')
        
    def test_payment_page_loads(self):
        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Payment Details")

    def test_subscription_flow(self):
        # Test Professional plan
        response = self.client.post(
            reverse('subscribe', kwargs={'plan_id': 'professional'}),
            {'duration': '30'}
        )
        self.assertRedirects(response, self.payment_url + '?plan=professional&amount=499.00&duration=30&total=578.84')
        
        # Verify payment page shows correct data
        payment_response = self.client.get(response.url)
        self.assertContains(payment_response, "KES 499.00")
        self.assertContains(payment_response, "Professional Plan")