# utils.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.utils import timezone

def generate_certificate(user, total_marks, total_questions):
    # Create a HttpResponse object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{user.username}.pdf"'

    # Create a PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Draw the text on the PDF
    p.drawString(100, height - 100, "Certificate of Completion")
    p.drawString(100, height - 150, f"This is to certify that {user.get_full_name()} has successfully completed the quiz.")
    p.drawString(100, height - 200, f"Total Marks: {total_marks} out of {total_questions}")
    p.drawString(100, height - 250, f"Date: {timezone.now().date()}")

    p.showPage()
    p.save()

    return response


