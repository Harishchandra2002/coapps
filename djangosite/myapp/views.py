from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import EmployeeRegistrationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from .forms import JobPostForm
from django.core.mail import send_mail, EmailMessage
from .models import Employee, Employee_Data, JobPost
from django.template.loader import render_to_string


# Create your views here.
def userreg(request):
    return render(request, "myapp/userreg.html", {})


def delete_job_post(request):
    if request.method == 'POST':
        job_post_id = request.POST.get('job_post_id')
        print(f"Received job_post_id: {job_post_id}")  # This will print the job_post_id
        try:
            job_post = JobPost.objects.get(id=job_post_id)
            job_post.delete()
            messages.success(request, 'Job post deleted successfully.')
            return redirect('job_post_list')  # Redirect to the job post list page after deletion
        except JobPost.DoesNotExist:
            return render(request, 'myapp/error.html', {'message': 'Job post not found.'})
    else:
        return redirect('error_page')

def publish_job_post1(request):
    if request.method == 'POST':
        job_post_id = request.POST.get('job_post_id')
        print(f"Received job_post_id: {job_post_id}")  # This will print the job_post_id
        try:
            job_post = JobPost.objects.get(id=job_post_id)
            job_post.status = JobPost.PUBLISHED
            job_post.save()
            messages.success(request, 'Job post published successfully!')
        except JobPost.DoesNotExist:
            messages.error(request, 'Job post does not exist.')
        return redirect('job_post_list')  # Redirect to the job post list page
    else:
        return redirect('error_page')

def main1(request):
    return render(request, "myapp/main.html")




def pending_to_publish(request):
    return delete_job_post(request)


def job_post_list(request):
    # Fetch only job posts with a pending status
    job_posts = JobPost.objects.filter(status=JobPost.PENDING)
    return render(request, 'myapp/pending to publish.html', {'job_posts': job_posts})


def job_post(request):
    return render(request, "myapp/job_post.html")


def publish_job_post(request):
    job_post_id = request.POST.get('id')
    print(job_post_id)
    if request.method == 'POST':
        job_post_id = request.POST.get('id')
        try:
            job_post = JobPost.objects.get(id=job_post_id)
            job_post.status = JobPost.PUBLISHED
            job_post.save()
            messages.success(request, 'Job post published successfully!')
        except JobPost.DoesNotExist:
            messages.error(request, 'Job post does not exist.')
    else:
        messages.error(request, 'Invalid request method.')

    return render(request,'myapp/pending to publish.html')  # Redirect to the job post list page

def create_job_post(request):
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job_post = form.save(commit=False)
            job_post.posted_by = request.user
            job_post.posted_on = timezone.now()
            job_post.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = JobPostForm()
    return render(request, 'recruitment/create_job_post.html', {
        'form': form,
        'user': request.user,
        'current_date': timezone.now().strftime('%Y-%m-%d')
    })


def index(request):
    return render(request, 'myapp/index.html')


# views.py


def request_leave(request):
    if request.method == 'POST':
        # Handle form submission
        # Fetch additional employee data from the database
        employee_id = request.POST.get('employee_id')
        employee_data = Employee_Data.objects.filter(emp_id=employee_id).first()
        emp_name = employee_data.employee_name
        leave_balance = employee_data.leave_balance

        # Send email notification to HR
        send_leave_request_notification_to_hr(request.POST, emp_name, leave_balance)
        # return redirect('leave_balance')
    return render(request, 'myapp/request_leave.html')


def approve_leave(request):
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        # Update leave request status in the database (e.g., set approved field to True)

        # Send email notification to the employee
        send_leave_notification_to_employee(emp_id, approved=True)

        return redirect('leave_balance')  # Redirect to leave balance page after approval


def reject_leave(request):
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        # Update leave request status in the database (e.g., set approved field to False)

        # Send email notification to the employee
        send_leave_notification_to_employee(emp_id, approved=False)

        return redirect('leave_balance')  # Redirect to leave balance page after rejection


def send_leave_notification_to_employee(emp_id, approved):
    # Retrieve employee data
    employee_data = Employee_Data.objects.get(emp_id=emp_id)
    employee_email = employee_data.employee_email
    employee_name = employee_data.employee_name

    # Compose email subject and message based on approval status
    subject = 'Leave Request Update'
    if approved:
        message = f'Hello {employee_name},\n\nYour leave request has been approved.'
    else:
        message = f'Hello {employee_name},\n\nYour leave request has been rejected.'

    # Send email
    send_mail(
        subject,
        message,
        'harishchandravallabhu@gmail.com',  # Update with your email address
        [employee_email],
    )


def send_leave_request_notification_to_hr(data, emp_name, leave_balance):
    subject = 'Leave Request Notification'
    # Render HTML template with leave request details
    html_message = render_to_string('myapp/hr_notification.html', {
        'emp_id': data['employee_id'],
        'emp_name': emp_name,
        'leave_balance': leave_balance,
        'start_date': data['start_date'],
        'end_date': data['end_date'],
        'reason': data['reason'],
        'leave_type': data['leave_type'],
    })
    from_email = 'harishchandravallabhu@gmail.com'  # Update with your email
    to_email = 'vallabhuharish03@gmail.com'  # Update with HR's email

    # Send email with HTML content
    send_mail(
        subject,
        '',  # Blank message as we are using html_message parameter
        from_email,
        [to_email],
        html_message=html_message,  # Include HTML content
    )


from django.core.exceptions import ValidationError


def insertuser(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        id_proof = request.FILES.get('id_proof')
        resume = request.FILES.get('resume')

        # Check if email already exists
        if Employee.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'errors': 'Email already exists'}, status=400)

        # Create and save Employee object
        employee = Employee(name=name, email=email, address=address, id_proof=id_proof, resume=resume)
        employee.full_clean()  # Validate model fields
        employee.save()

        # Redirect to the approval_pending page or any other page as needed
        return redirect('approval_pending')
    else:
        return JsonResponse({'success': False, 'errors': 'Method not allowed'}, status=405)


def approval_pending(request):
    # Retrieve details from the latest Employee object
    latest_employee = Employee.objects.last()
    if latest_employee:
        name = latest_employee.name
        email = latest_employee.email
        address = latest_employee.address

        # Generate employee ID
        last_employee_data = Employee_Data.objects.last()
        if last_employee_data:
            emp_id = last_employee_data.emp_id + 1
        else:
            emp_id = 50001

        # Save employee data to the database
        password = email  # Assuming password is same as email
        leave_balance = 10
        employee_data = Employee_Data.objects.create(
            emp_id=emp_id,
            employee_name=name,
            employee_email=email,
            password=password,
            leave_balance=leave_balance
        )

        # Send email to the user with employee details
        subject = 'Registration Confirmation'
        message = f'Hello {name},\n\nThank you for your registration. Your details are as follows:\n\nEmployee ID: {emp_id}\nUser ID: {email}\nPassword: {password}\n\nWe will process your request shortly.\n\nRegards,\nHarish Vallabhu'

        # Send confirmation email to the user
        email_to_user = EmailMessage(
            subject,
            message,
            to=[email],
        )
        email_to_user.send()

        # Compose email content for admin
        admin_subject = 'Pending Registration Approval'
        admin_message = f'Hello Harish,\n\nThis is to notify you about a pending registration approval for:\n\nName: {name}\nEmail: {email}\nAddress: {address}\n\nEmployee ID: {emp_id}\n\nPlease take necessary action.\n\nRegards,\nHarish Vallabhu'

        # Send email to admin
        send_mail(
            admin_subject,
            admin_message,
            'harishchandravallabhu@gmail.com',
            ['vallabhuharish03@gmail.com'],
        )

        # Render the approval_pending.html template
        return render(request, 'myapp/approval_pending.html', {})
    else:
        # Handle case when there are no Employee objects in the database
        return JsonResponse({'error': 'No employee data found'}, status=404)
