import random
import string
import uuid
import datetime
import lorem  # For generating text placeholders

class DynamicContentGenerator:
    """Provides methods to generate dynamic content for API request fields."""

    @staticmethod
    def generate_text(min_words=3, max_words=10):
        """Generate random text with the specified number of words."""
        word_count = random.randint(min_words, max_words)
        return lorem.text()[:word_count*10].strip()

    @staticmethod
    def generate_paragraph(min_sentences=2, max_sentences=5):
        """Generate a paragraph with the specified number of sentences."""
        return lorem.paragraph()

    @staticmethod
    def generate_uuid():
        """Generate a UUID string."""
        return str(uuid.uuid4())

    @staticmethod
    def generate_email():
        """Generate a random email address."""
        username = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
        domain = ''.join(random.choice(string.ascii_lowercase) for _ in range(6))
        return f"{username}@{domain}.com"

    @staticmethod
    def generate_phone():
        """Generate a random phone number."""
        return f"+1{random.randint(200, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}"

    @staticmethod
    def generate_date(start_date=None, end_date=None):
        """Generate a random date between start_date and end_date (or within last year if not specified)."""
        if not start_date:
            start_date = datetime.datetime.now() - datetime.timedelta(days=365)
        if not end_date:
            end_date = datetime.datetime.now()

        if isinstance(start_date, str):
            start_date = datetime.datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.datetime.fromisoformat(end_date)

        time_delta = end_date - start_date
        random_days = random.randint(0, time_delta.days)
        random_date = start_date + datetime.timedelta(days=random_days)
        return random_date.strftime("%Y-%m-%d")

    @staticmethod
    def generate_number(min_val=0, max_val=100):
        """Generate a random number between min_val and max_val."""
        return random.randint(min_val, max_val)

    @staticmethod
    def generate_boolean():
        """Generate a random boolean value."""
        return random.choice([True, False])

    @staticmethod
    def generate_list(generator_func, length=3, **kwargs):
        """Generate a list of items using the specified generator function."""
        return [generator_func(**kwargs) for _ in range(length)]

    @staticmethod
    def from_options(options):
        """Select a random item from the provided options."""
        return random.choice(options)

