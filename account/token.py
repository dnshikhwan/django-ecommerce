
# - Import password reset token generator

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


# - Password reset token generator method

class UserVerificationTokenGenerator(PasswordResetTokenGenerator):
    # generator create a unique code for our individual users
    def _make_hash_value(self, user, timestamp):
        # take the user id and once the user click on the link in the email ->
        user_id = six.text_type(user.pk)
        ts = six.text_type(timestamp)
        # -> set the user to active
        is_active = six.text_type(user.is_active)
        return f"{user_id}{ts}{is_active}"


# pass that function into variable so that we can use it other code
user_tokenizer_generate = UserVerificationTokenGenerator()
