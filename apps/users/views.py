from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import EmailAuthenticationForm, UserCreationForm, UserChangeForm, VacationStaffForm, MultipleUserFileForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView,ListView, TemplateView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django_filters.views import FilterView
from .filters import UserStaffFillter, DocumentFilter, VacationFilter
from .models import Document, Vacation
from .password_change import *
from .export import Staff_export
from django.contrib import messages

UserModel = get_user_model()

#fake view for testing
from django.http import HttpResponse
def fake_view(request):
    return HttpResponse("This is a fake view for testing purposes.")

# Login user function
def custom_login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to home page after successful login
        else:
            # If the form is invalid, the error message will be shown on the form
            return render(request, 'app/accounts/login.html', {'form': form})
    else:
        form = EmailAuthenticationForm()
    return render(request, 'app/accounts/login.html', {'form': form})



# Logout user function
def custom_logout(request):
    logout(request)
    return redirect('login')



# Staff List View
class UserStaffView(LoginRequiredMixin,FilterView):
    model = get_user_model()
    filterset_class = UserStaffFillter
    context_object_name = 'users'
    template_name = "app/staff/staff.html"

    # Override to add the form to the context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserCreationForm()  # Inject the form into the context
        return context

    # Handle form submission (manual post method for CreateView functionality)
    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff_list')  # Redirect to course list after submission
        return self.get(request, *args, form=form)

    def get_queryset(self):
        queryset = super().get_queryset()
        if  self.request.user.is_superuser:
            queryset = get_user_model().objects.filter(is_staff=True)
        else:
            queryset = queryset.filter(is_staff=True,organization=self.request.user.organization)
        return queryset



# Staff Create View
# class UserStaffCreateView(LoginRequiredMixin,CreateView):
#     model = get_user_model()
#     form_class = UserCreationForm
#     template_name = "app/staff/staff_new.html"
#     success_url = reverse_lazy('staff_new')
    
#     def form_invalid(self, form):
#         print(form.errors)
#         return super().form_invalid(form)


    # def get_queryset(self):
    #     # Return only the courses associated with the current logged-in user
    #     return self.request.user.courses.all()
   
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['user'] = self.request.user
    #     return kwargs
    
    # def get_initial(self):
    #     initial = super().get_initial()
    #     initial['is_staff'] = True  # Set the initial value as needed
    #     return initial

    # def form_valid(self, form):
    #     # Retain the value of the disabled field
    #     form.cleaned_data['is_staff'] = self.get_initial()['is_staff']
    #     return super().form_valid(form)

    # def form_valid(self, form):
    #     # Add a success message after a successful form submission
    #     messages.success(self.request, 'Your form has been submitted successfully!')
    #     return super().form_valid(form)


# Staff Update View
class UserStaffUpdateView(LoginRequiredMixin,UpdateView):
    model = get_user_model()
    #fields = '__all__'
    template_name = 'app/staff/staff_edit.html'
    form_class = UserChangeForm
    success_url = reverse_lazy('home')
    
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['user'] = self.request.user
    #     return kwargs


# Student - User create
# class StudentUserCreateView(LoginRequiredMixin,CreateView):
#     model = get_user_model()
#     form_class = UserCreationForm
#     template_name = "app/student/student_new.html"
#     success_url = reverse_lazy('home')
    
#     def form_invalid(self, form):
#         print(form.errors)
#         return super().form_invalid(form)
    
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user'] = self.request.user
#         return kwargs
    
#     def get_initial(self):
#         initial = super().get_initial()
#         initial['is_student'] = True  # Set the initial value as needed
#         return initial
    
#     def form_valid(self, form):
#         form.cleaned_data['is_student'] = self.get_initial()['is_student']
#         return super().form_valid(form)


# Student - User Update
# class StudentUserUpdateView(LoginRequiredMixin,UpdateView):
#     model = get_user_model()
#     #fields = '__all__'
#     template_name = 'app/student/student_edit.html'
#     form_class = UserChangeForm
#     success_url = reverse_lazy('home')

    # def form_valid(self, form):
    #     try:
    #         response = super().form_valid(form)
    #         logger.info(f'Member "{self.object}" updated successfully.')
    #         messages.success(self.request, 'Member updated successfully.')
    #         return response
    #     except Exception as e:
    #         logger.error(f'Error updating book: {e}')
    #         form.add_error(None, 'An error occurred while updating the member.')
    #         return super().form_invalid(form)





    # def form_valid(self, form):
    #     try:
    #         response = super().form_valid(form)
    #         logger.info(f'Member "{self.object}" updated successfully.')
    #         messages.success(self.request, 'Member updated successfully.')
    #         return response
    #     except Exception as e:
    #         logger.error(f'Error updating book: {e}')
    #         form.add_error(None, 'An error occurred while updating the member.')
    #         return super().form_invalid(form)

# Upload File to User
@login_required
def upload_files(request):
    logged_in_user = request.user  # Get the logged-in user

    if request.method == 'POST':
        form = MultipleUserFileForm(request.POST, request.FILES, logged_in_user=logged_in_user)
        if form.is_valid():
            selected_user = form.cleaned_data['user']
            filename = form.cleaned_data['filename']
            course = form.cleaned_data['course']
            file = request.FILES.getlist('file')
            for file in file:
                Document.objects.create(user=selected_user, file=file,filename=filename,course=course)
            messages.success(request, 'Files uploaded successfully!')
            return redirect('upload_files')  # Redirect to a success page
        else:
            messages.error(request, 'Please correct the errors below and try again.')
    else:
        form = MultipleUserFileForm(logged_in_user=logged_in_user)

    return render(request, 'app/files/document_upload.html', {'form': form})

# Document list
class DocumentListView(LoginRequiredMixin,FilterView):
    model = Document
    template_name = 'app/files/document_list.html'
    filterset_class = DocumentFilter
    context_object_name = 'documents'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['row_count'] = Document.objects.count()  # Count the rows
        return context
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Document.objects.all()  # Staff can see all articles
        else:
            return Document.objects.filter(user__student__is_student=True, user__is_staff=False,user__student__organization=self.request.user.organization)




class VacationStaffListView(LoginRequiredMixin, FilterView):
    model = Vacation
    template_name = 'app/staff/staff_vacation_list.html'
    filterset_class = VacationFilter
    context_object_name = 'vacations'
    paginate_by = 10

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['vacations_empty'] = not context['vacations'].exists()
    #     return context

    # Override to add the form to the context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = VacationStaffForm()  # Inject the form into the context
        return context

    # Handle form submission (manual post method for CreateView functionality)
    def post(self, request, *args, **kwargs):
        form = VacationStaffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vacation_list')  # Redirect to course list after submission
        return self.get(request, *args, form=form)



class UpdateListView(LoginRequiredMixin,ListView):
    model = ''
    template_name = 'app/update_list.html'
    context_object_name = 'updates'
    
    