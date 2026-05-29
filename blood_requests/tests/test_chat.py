from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from blood_requests.models import BloodRequest, DonorResponse, ChatMessage
from donors.models import DonorProfile

User = get_user_model()

class SecureChatTests(TestCase):

    def setUp(self):
        # Create Seeker
        self.seeker = User.objects.create_user(
            username='seeker_user',
            password='password123',
            role='seeker',
            first_name='John',
            last_name='Seeker'
        )
        
        # Create Donor
        self.donor = User.objects.create_user(
            username='donor_user',
            password='password123',
            role='donor',
            first_name='Jane',
            last_name='Donor'
        )
        self.donor_profile = DonorProfile.objects.create(
            user=self.donor,
            blood_group='O',
            rh_factor='-',
            age=25,
            availability_status='available'
        )

        # Create External User (unrelated to request or response)
        self.external = User.objects.create_user(
            username='external_user',
            password='password123',
            role='donor'
        )

        # Create Blood Request
        self.request = BloodRequest.objects.create(
            requester=self.seeker,
            patient_name='Patient Alpha',
            blood_group='O',
            rh_factor='-',
            units_required=2,
            hospital_name='Central Hospital',
            status='open'
        )

        # Create Donor Response
        self.response = DonorResponse.objects.create(
            blood_request=self.request,
            donor=self.donor,
            status='interested',
            message='I can donate tomorrow.'
        )

    def test_chat_message_creation(self):
        """Verify ChatMessage model saves and stringifies correctly."""
        msg = ChatMessage.objects.create(
            donor_response=self.response,
            sender=self.donor,
            message='Hello, I am ready to coordinate.'
        )
        self.assertEqual(msg.message, 'Hello, I am ready to coordinate.')
        self.assertEqual(msg.sender, self.donor)
        self.assertEqual(msg.donor_response, self.response)
        self.assertIn('donor_user', str(msg))

    def test_access_control_chat_room(self):
        """Only seeker and responding donor can access chat room; others receive 403."""
        # Seeker is allowed
        self.client.force_login(self.seeker)
        response = self.client.get(reverse('chat_room', args=[self.response.id]))
        self.assertEqual(response.status_code, 200)

        # Donor is allowed
        self.client.force_login(self.donor)
        response = self.client.get(reverse('chat_room', args=[self.response.id]))
        self.assertEqual(response.status_code, 200)

        # External user gets 403 Forbidden
        self.client.force_login(self.external)
        response = self.client.get(reverse('chat_room', args=[self.response.id]))
        self.assertEqual(response.status_code, 403)

    def test_access_control_messages_api(self):
        """Only seeker and responding donor can fetch/post messages; others receive 403."""
        # External user trying to GET messages
        self.client.force_login(self.external)
        response = self.client.get(reverse('chat_messages', args=[self.response.id]))
        self.assertEqual(response.status_code, 403)

        # External user trying to POST message
        response = self.client.post(reverse('chat_messages', args=[self.response.id]), {'message': 'Hack!'})
        self.assertEqual(response.status_code, 403)

    def test_messages_api_get_and_post(self):
        """Verify get and post endpoints for message coordination."""
        self.client.force_login(self.donor)
        
        # Post a message via POST endpoint
        response = self.client.post(reverse('chat_messages', args=[self.response.id]), {
            'message': 'Hi Seeker, let\'s coordinate!'
        })
        self.assertEqual(response.status_code, 200)
        
        json_resp = response.json()
        self.assertEqual(json_resp['message'], 'Hi Seeker, let\'s coordinate!')
        self.assertEqual(json_resp['is_me'], True)
        self.assertIn('id', json_resp)
        
        message_id = json_resp['id']

        # Get messages via GET endpoint
        self.client.force_login(self.seeker)
        response = self.client.get(reverse('chat_messages', args=[self.response.id]))
        self.assertEqual(response.status_code, 200)
        
        get_json = response.json()
        self.assertEqual(len(get_json['messages']), 1)
        self.assertEqual(get_json['messages'][0]['message'], 'Hi Seeker, let\'s coordinate!')
        self.assertEqual(get_json['messages'][0]['is_me'], False)  # For Seeker, it was sent by Donor

        # Test polling filtering with last_id
        response = self.client.get(reverse('chat_messages', args=[self.response.id]), {'last_id': message_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['messages']), 0) # No newer messages

        # Post another message and verify it is returned with last_id filtering
        ChatMessage.objects.create(
            donor_response=self.response,
            sender=self.seeker,
            message='Thank you so much!'
        )

        response = self.client.get(reverse('chat_messages', args=[self.response.id]), {'last_id': message_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['messages']), 1)
        self.assertEqual(response.json()['messages'][0]['message'], 'Thank you so much!')

    def test_unread_message_counting_and_marking_read(self):
        """Verify unread counts are calculated correctly and marked as read upon viewing."""
        # Seeker sends 2 messages
        ChatMessage.objects.create(donor_response=self.response, sender=self.seeker, message='Message 1')
        ChatMessage.objects.create(donor_response=self.response, sender=self.seeker, message='Message 2')

        # Seeker unread count for donor should be 2
        # (meaning the donor has 2 unread messages from the seeker)
        self.client.force_login(self.donor)
        response = self.client.get(reverse('donor_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check that response context includes the unread count
        my_responses = response.context['my_responses']
        self.assertEqual(my_responses[0].unread_count, 2)

        # Donor enters the chat room
        response = self.client.get(reverse('chat_room', args=[self.response.id]))
        self.assertEqual(response.status_code, 200)

        # Verify messages are now marked as read
        self.assertEqual(self.response.chat_messages.filter(is_read=False).count(), 0)

        # Seeker unread count for donor is now 0 on dashboard
        response = self.client.get(reverse('donor_dashboard'))
        self.assertEqual(response.context['my_responses'][0].unread_count, 0)

    def test_global_unread_messages_count_and_chat_list(self):
        """Verify global unread context processor and central chat list view."""
        # Originally unread count is 0
        self.client.force_login(self.donor)
        response = self.client.get(reverse('donor_dashboard'))
        self.assertEqual(response.context['total_unread_chats'], 0)

        # Seeker sends a message
        ChatMessage.objects.create(donor_response=self.response, sender=self.seeker, message='Global message test')

        # Now, the donor's global unread count should be 1
        response = self.client.get(reverse('donor_dashboard'))
        self.assertEqual(response.context['total_unread_chats'], 1)

        # Access chat list view
        response = self.client.get(reverse('chat_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['chat_rooms']), 1)
        self.assertEqual(response.context['chat_rooms'][0]['unread_count'], 1)
        self.assertEqual(response.context['chat_rooms'][0]['last_message'].message, 'Global message test')

