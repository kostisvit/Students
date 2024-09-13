from django.shortcuts import render
from .models import Student
from .filters import StudentFilter
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin




# Member list view
class StudentListView(LoginRequiredMixin,FilterView):
    model = Student
    template_name = 'app/student/student.html'
    context_object_name = 'students'
    filterset_class = StudentFilter
    paginate_by = 10
    
    def get_filterset_kwargs(self, filterset_class):
        # Get the default kwargs from the parent method
        kwargs = super().get_filterset_kwargs(filterset_class)
        # Add the current user to the kwargs
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add a flag indicating if the members list is empty
        context['students_empty'] = not context['students'].exists()
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            # Apply filter for superuser
            queryset = queryset.filter(is_student=True)  # Replace with your actual filter conditions for superusers
        else:
            # Apply different filter for regular users
            queryset = queryset.filter(user__organization=self.request.user.organization, is_student=True)  # Replace with your actual filter conditions for regular users
        return queryset
