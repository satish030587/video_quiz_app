import io
import uuid
from django.http import HttpResponse, FileResponse
from django.utils import timezone
from django.template.loader import render_to_string
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .models import Certificate, User, UserProgress
from videos.models import Video
from .serializers import CertificateSerializer
from .permissions import IsSuperAdmin

def generate_certificate_pdf(user, certificate_id):
    """Generate a PDF certificate for the user"""
    buffer = io.BytesIO()
    
    # Create the PDF object, using the buffer as its "file."
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # We'll use the default fonts
    
    # Draw a border
    c.setStrokeColor(colors.black)
    c.setLineWidth(3)
    c.rect(0.5*inch, 0.5*inch, width-inch, height-inch)
    
    # Title
    c.setFont('Courier-Bold', 24)
    c.drawCentredString(width/2, height-2*inch, "Certificate of Completion")
    
    # Draw the company logo
    # c.drawImage('path/to/logo.png', width/2-inch, height-1.5*inch, width=2*inch, height=1*inch)
    
    # User's name
    c.setFont('Courier-Bold', 18)
    c.drawCentredString(width/2, height/2+inch, f"{user.first_name} {user.last_name}")
    
    # Description
    styles = getSampleStyleSheet()
    style = ParagraphStyle(
        'Normal',
        fontName='Courier',
        fontSize=12,
        alignment=1,  # Center alignment
        leading=14
    )
    
    description = f"""This certifies that <b>{user.first_name} {user.last_name}</b> has successfully 
    completed all video quizzes in our educational platform demonstrating understanding 
    and knowledge of the subject matter."""
    
    p = Paragraph(description, style)
    p.wrapOn(c, width-3*inch, height)
    p.drawOn(c, 1.5*inch, height/2)
    
    # Date
    date_str = timezone.now().strftime("%B %d, %Y")
    c.setFont('Courier', 12)
    c.drawCentredString(width/2, height/2-inch, f"Issued on: {date_str}")
    
    # Certificate ID
    c.setFont('Courier', 10)
    c.drawCentredString(width/2, height/2-1.5*inch, f"Certificate ID: {certificate_id}")
    
    # Signature
    c.setFont('Courier-Bold', 12)
    c.drawCentredString(width/2, 2*inch, "Authorized Signature")
    c.line(width/2-inch, 1.8*inch, width/2+inch, 1.8*inch)
    
    # Save the PDF
    c.showPage()
    c.save()
    
    # Get the value from the buffer and return it
    buffer.seek(0)
    return buffer

class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for certificates
    """
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_superadmin:
            return Certificate.objects.all()
        return Certificate.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_certificates(self, request):
        """Get current user's certificates"""
        certificates = Certificate.objects.filter(user=request.user)
        serializer = self.get_serializer(certificates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a certificate for the user if eligible"""
        user = request.user
        
        # Check if user has already received a certificate
        if Certificate.objects.filter(user=user).exists():
            return Response(
                {"detail": "You have already received a certificate."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user has completed all videos
        try:
            progress = UserProgress.objects.get(user=user)
            total_videos = Video.objects.filter(is_active=True).count()
            passed_videos = progress.videos_passed.count()
            
            if passed_videos < total_videos:
                return Response(
                    {"detail": f"You need to complete all videos ({passed_videos}/{total_videos} completed)."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate unique certificate ID
            certificate_id = str(uuid.uuid4())
            
            # Create certificate record
            certificate = Certificate.objects.create(
                user=user,
                unique_id=certificate_id
            )
            
            serializer = self.get_serializer(certificate)
            return Response(serializer.data)
            
        except UserProgress.DoesNotExist:
            return Response(
                {"detail": "User progress not found."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download certificate PDF"""
        certificate = self.get_object()
        
        # Check if certificate belongs to current user or is superadmin
        if certificate.user != request.user and not request.user.is_superadmin:
            return Response(
                {"detail": "You don't have permission to download this certificate."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # If already has PDF file, return it
        if certificate.pdf_file:
            certificate.is_downloaded = True
            certificate.save()
            return FileResponse(certificate.pdf_file, as_attachment=True, filename=f"certificate_{certificate.unique_id}.pdf")
        
        # Generate PDF
        pdf_buffer = generate_certificate_pdf(certificate.user, certificate.unique_id)
        
        # Mark as downloaded
        certificate.is_downloaded = True
        certificate.save()
        
        # Return the PDF
        return FileResponse(pdf_buffer, as_attachment=True, filename=f"certificate_{certificate.unique_id}.pdf")
