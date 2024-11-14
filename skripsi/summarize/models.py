# models.py
from django.db import models

class Paragraph(models.Model):
    text = models.TextField()