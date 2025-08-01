# In users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User, UserProgress, Certificate
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'
        
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'is_superadmin')

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ('username', 'email', 'is_superadmin', 'is_staff', 'date_joined')
    list_filter = ('is_superadmin', 'is_staff', 'is_active')
    
    # Define completely custom fieldsets
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'profile_picture')}),
        ('Permissions', {'fields': ('is_superadmin', 'is_active', 'is_staff', 'is_superuser', 
                                  'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_superadmin', 
                     'is_staff', 'is_active'),
        }),
    )
    
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_overall_progress', 'display_videos_passed', 'total_retries', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('overall_progress', 'total_retries', 'last_updated', 'display_videos_passed_list', 'display_videos_failed_list')
    
    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        ('Progress Statistics', {
            'fields': ('overall_progress', 'total_retries', 'last_updated')
        }),
        ('Videos', {
            'fields': ('display_videos_passed_list', 'display_videos_failed_list'),
            'classes': ('collapse',),
        })
    )
    
    def display_overall_progress(self, obj):
        """Format the overall progress as a percentage with color"""
        progress = float(obj.overall_progress)
        color = 'green' if progress >= 70 else 'orange' if progress >= 40 else 'red'
        # Don't use format specifier with format_html
        formatted_progress = '{:.1f}'.format(progress)
        return format_html('<span style="color:{};">{}</span>', color, formatted_progress + '%')
    display_overall_progress.short_description = 'Overall Progress'
    
    def display_videos_passed(self, obj):
        """Display number of passed videos vs total videos"""
        from videos.models import Video
        total_videos = Video.objects.filter(is_active=True).count()
        passed_count = obj.videos_passed.count()
        return format_html("{}/{}", passed_count, total_videos)
    display_videos_passed.short_description = 'Videos Passed'
    
    def display_videos_passed_list(self, obj):
        """Display list of passed videos"""
        if obj.videos_passed.count() == 0:
            return "No videos passed"
        
        # Start with an empty list
        html_content = format_html("<ul>")
        
        # Add each item individually with format_html
        for video in obj.videos_passed.all():
            item_html = format_html("<li>{}</li>", video.title)
            html_content = format_html("{}{}", html_content, item_html)
        
        # Close the list
        html_content = format_html("{}</ul>", html_content)
        return html_content
    display_videos_passed_list.short_description = 'Passed Videos'
    
    def display_videos_failed_list(self, obj):
        """Display list of failed videos"""
        if obj.videos_failed.count() == 0:
            return "No videos failed"
        
        # Start with an empty list
        html_content = format_html("<ul>")
        
        # Add each item individually with format_html
        for video in obj.videos_failed.all():
            item_html = format_html("<li>{}</li>", video.title)
            html_content = format_html("{}{}", html_content, item_html)
        
        # Close the list
        html_content = format_html("{}</ul>", html_content)
        return html_content
    display_videos_failed_list.short_description = 'Failed Videos'
    
    # Actions buttons and manual recalculation have been removed
    # Progress is automatically updated whenever quiz attempts change
    # Manual progress recalculation and reset views have been removed
    # Progress is automatically updated whenever quiz attempts change

class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'unique_id', 'issue_date', 'is_downloaded')
    list_filter = ('issue_date', 'is_downloaded')
    search_fields = ('user__username', 'user__email', 'unique_id')
    readonly_fields = ('issue_date',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProgress, UserProgressAdmin)
admin.site.register(Certificate, CertificateAdmin)