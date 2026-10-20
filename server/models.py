"""
SQLAlchemy Models and Validations
---------------------------------

Defines the Author and Post database models for the blog application

Model-level validators enforce data integrity by checking required
attributes, uniqueness, formatting, content length, permitted categories,
and title keywords before values are assigned to model attributes

Invalid values raise a ValueError, preventing invalid assignments
Database constraints provide additional protection when records are saved
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

# Initialize the SQLAlchemy database instance
db = SQLAlchemy()

class Author(db.Model):
    """
    Represents an author in the blog application

    Attributes:
        id (int): Unique identifier for the author
        name (str): Required, unique author name
        phone_number (str): Author's ten-digit phone number
        created_at (datetime): Timestamp when the author was created
        updated_at (datetime): Timestamp of the last update

    Validations:
        - Names must be nonempty strings
        - Names must be unique across authors
        - Phone numbers must contain exactly ten digits
    """

    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    #----------------------
    # Validators
    #----------------------
    @validates('name')
    def validates_name(self, key, name):
        """
        Validate an author's name before assignment

        Ensures the name is a nonempty string and does not belong
        to another author already stored in the database

        Args:
            key (str): Name of the SQLAlchemy attribute being validated
            name (str): Proposed author name

        Returns:
            str: The validated author name

        Raises:
            ValueError: If the name is not a string, is empty or
                whitespace-only, or already belongs to another author
        """
        # Reject values that are not strings
        if not isinstance(name, str):
            raise ValueError("Name must be a string")

        # Reject empty or whitespace-only names
        if not name.strip():
            raise ValueError("Name must be present")

        # Search for matching names while excluding the current author
        # This avoids treating an existing author's own name as a duplicate
        duplicate_name = db.session.query(Author.id).filter(
            Author.name == name,
            Author.id != self.id
        ).first()

        if duplicate_name is not None:
            raise ValueError("Name must be unique")

        return name
    
    @validates('phone_number')
    def validates_phone_number(self, key, phone_number):
        """
        Validate an author's phone number before assignment

        Ensures the phone number is a string containing exactly
        ten numeric characters, without additional formatting

        Args:
            key (str): Name of the SQLAlchemy attribute being validated
            phone_number (str): Proposed phone number.

        Returns:
            str: The validated phone number

        Raises:
            ValueError: If the phone number is missing, is not a
                string, contains non-digit characters, or does not
                contain exactly ten characters
        """

        # Phone numbers are stored as strings to preserve leading zeros
        if not isinstance(phone_number, str):
            raise ValueError("Phone number must be a string")

        if not phone_number:
            raise ValueError("Phone number must be present")

        # Reject incorrect lengths and non-digit characters
        if len(phone_number) != 10 or not phone_number.isdigit():
            raise ValueError("Phone number must be exactly 10 digits")

        return phone_number

    def __repr__(self): 
        """
        Return a readable representation of an Author instance.

        Returns:
            str: String containing the author's ID and name.
        """
        return f'Author(id={self.id}, name={self.name})'

class Post(db.Model):
    """
    Represents a blog post in the application

    Attributes:
        id (int): Unique identifier for the post
        title (str): Required title containing a clickbait keyword
        content (str): Main post content, at least 250 characters
        category (str): Either Fiction or Non-Fiction
        summary (str): Optional summary, maximum 250 characters
        created_at (datetime): Timestamp when the post was created
        updated_at (datetime): Timestamp of the last update

    Validations:
        - Titles must be nonempty strings containing an approved phrase
        - Content must contain at least 250 characters
        - Summaries cannot exceed 250 characters
        - Categories must be Fiction or Non-Fiction
    """

    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String)
    category = db.Column(db.String)
    summary = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    #----------------------
    # Validators
    #----------------------
    @validates('title')
    def validates_title(self, key, title):
        """
        Validate a blog post's title before assignment

        Ensures the title is a nonempty string containing at least
        one of the required clickbait phrases

        Args:
            key (str): Name of the SQLAlchemy attribute being validated
            title (str): Proposed post title

        Returns:
            str: The validated title

        Raises:
            ValueError: If the title is not a string, is empty, or
                does not contain an approved clickbait phrase
        """

        if not isinstance(title, str):
            raise ValueError("Title must be a string")

        # Reject empty or whitespace-only titles
        if not title.strip():
            raise ValueError("Title must be present.")

        # A title must contain at least one of these phrases
        clickbaits = ["Won't Believe", "Secret", "Top", "Guess"]

        # any() returns True when at least one phrase appears in the title
        if not any(clickbait in title for clickbait in clickbaits):
            raise ValueError("Title must contain a clickbait word")

        return title
    
    @validates('content')
    def validates_content(self, key, content):
        """
        Validate the main content of a blog post

        Ensures the content is a string containing at least
        250 characters

        Args:
            key (str): Name of the SQLAlchemy attribute being validated
            content (str): Proposed post content

        Returns:
            str: The validated content

        Raises:
            ValueError: If content is not a string or contains
                fewer than 250 characters
        """

        if not isinstance(content, str):
            raise ValueError("Content must be a string")

        # Exactly 250 characters is valid
        if len(content) < 250:
            raise ValueError("Content is too short")

        return content
    
    @validates('summary')
    def validates_summary(self, key, summary):
        """
        Validate the optional summary of a blog post

        Ensures a provided summary is a string containing
        no more than 250 characters

        Args:
            key (str): Name of the SQLAlchemy attribute being validated
            summary (str or None): Proposed post summary

        Returns:
            str or None: The validated summary, or None if omitted

        Raises:
            ValueError: If a provided summary is not a string or
                exceeds 250 characters
        """

        # A summary is optional, so None is permitted
        if summary is None:
            return None

        if not isinstance(summary, str):
            raise ValueError("Summary must be a string")

        # Reject summaries longer than the permitted maximum
        if len(summary) > 250:
            raise ValueError("Summary is too long")

        return summary
        
    @validates('category')
    def validates_category(self, key, category):
        """
        Validate a blog post's category before assignment

        Restricts category values to the two approved options:
        Fiction and Non-Fiction

        Args:
            key (str): Name of the SQLAlchemy attribute being validated
            category (str): Proposed post category

        Returns:
            str: The validated category

        Raises:
            ValueError: If the category is missing or does not
                match one of the permitted values
        """

        if not category:
            raise ValueError("Category must be present")

        # Only these exact category values are accepted.
        allowed_categories = ['Fiction', 'Non-Fiction']

        if category not in allowed_categories:
            raise ValueError("Category must be 'Fiction' or 'Non-Fiction'")

        return category

    def __repr__(self):
            """
            Return a readable representation of a Post instance.

            Returns:
                str: String containing the post's ID, title,
                    content, and summary.
            """
            return (
                f'Post(id={self.id}, title={self.title} '
                f'content={self.content}, summary={self.summary})'
            )
