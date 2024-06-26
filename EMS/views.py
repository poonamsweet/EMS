from turtle import pos
import django
from django.shortcuts import redirect, render
from .models import Employee, AddTask
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as authlogin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404


def home(request):
    emp_data = Employee.objects.all()
    task_data = AddTask.objects.all()
    on_leave = emp_data.filter(on_leave=True)
    total_employee = emp_data.count()
    total_task = task_data.count()

    # Combine total_employee and total_task into the chart data
    xValues = ["Total Employees", "Total Tasks", "Total Leave"]
    yValues = [total_employee, total_task, on_leave.count()]
    barColors = ["#b91d47", "#00aba9", "#0gha8"]

    context = {
        'total_employee': total_employee,
        'total_task': total_task,
        'is_user_logged_in': request.user.is_authenticated,
        'xValues': xValues,
        'yValues': yValues,
        'barColors': barColors,
        'chart_title': "Employee and Task Overview"
    }
    return render(request, 'dashboard.html', context)
################ login forms###################################################


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            form = authlogin(request, user)
            messages.success(request, f' welcome {username} !!')
            return redirect('employee-list')
        else:
            messages.info(request, f'account done not exit plz sign in')
    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'title': 'log in'})
    return render(request, 'login.html')


def createEmployeee(request):
    is_user_logged_in = request.user.is_authenticated
    if request.method == "POST":
        name = request.POST['name']
        dob = request.POST['dob']
        doj = request.POST['doj']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        zipcode = request.POST['zipcode']
        country = request.POST['country']
        department = request.POST['department']
        post = request.POST['post']
        emp_obj = Employee.objects.create(name=name, dob=dob, doj=doj, address=address, city=city,
                                          state=state, zipcode=zipcode, country=country, department=department, post=post)
        messages.success(request, "Employee created successfully")
        return redirect('employee-list')
    return render(request, 'create_employeee.html', {'is_user_logged_in': is_user_logged_in})


def employee_list(request):
    emp_data = Employee.objects.all()
    paginator = Paginator(emp_data, 5)  # Show 10 employees per page

    page = request.GET.get('page')
    try:
        employees = paginator.page(page)
    except PageNotAnInteger:
        employees = paginator.page(1)
    except EmptyPage:
        employees = paginator.page(paginator.num_pages)

    is_user_logged_in = request.user.is_authenticated
    d = {'employees': employees, 'is_user_logged_in': is_user_logged_in}
    return render(request, 'employee_list.html', d)


def edit_employee(request, pid):
    is_user_logged_in = request.user.is_authenticated
    emp_data = Employee.objects.get(id=pid)
    if request.method == "POST":
        name = request.POST['name']
        dob = request.POST['dob']
        doj = request.POST['doj']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        zipcode = request.POST['zipcode']
        country = request.POST['country']
        department = request.POST['department']
        post = request.POST['post']
        emp_obj = Employee.objects.filter(id=pid).update(name=name, dob=dob, doj=doj, address=address,
                                                         city=city, state=state, zipcode=zipcode, country=country, department=department, post=post)
        messages.success(request, "Employee Updated successfully")
        return redirect('employee-list')
    return render(request, 'edit_employeee.html', {'emp_data': emp_data, 'is_user_logged_in': is_user_logged_in})


def delete_employee(request, pid):
    data = Employee.objects.get(id=pid)
    data.delete()
    messages.success(request, "Employee Deleted successfully")
    return redirect('employee-list')


def leave_status(request, pid):
    data = Employee.objects.get(id=pid)
    if data.on_leave:
        data.on_leave = False
    else:
        data.leave_count = data.leave_count + 1
        data.on_leave = True
    data.save()
    messages.success(request, "Employee leave status Changed successfully.")
    return redirect('employee_list')


def logoutUser(request):
    logout(request)
    return redirect('login')


def addtask(request):
    is_user_logged_in = request.user.is_authenticated
    if request.method == "POST":
        titles = request.POST.getlist('title[]')
        descriptions = request.POST.getlist('description[]')
        dates = request.POST.getlist('date[]')
        assignees = request.POST.getlist('assignee[]')

        for title, description, date, assignee_id in zip(titles, descriptions, dates, assignees):
            assignee = Employee.objects.get(id=assignee_id)
            task = AddTask.objects.create(
                title=title, description=description, date=date, assignee=assignee)

        # Assuming you have a URL named 'task-list' for redirect
        return redirect('employee-list')
    employees = Employee.objects.all()
    return render(request, 'employee_list.html', {'is_user_logged_in': is_user_logged_in, "employees": employees})


def task_list(request, employee_id=None):
    emp_data = Employee.objects.all()
    is_user_logged_in = request.user.is_authenticated

    if employee_id:
        employee = get_object_or_404(Employee, id=employee_id)
        task_data = AddTask.objects.filter(assignee=employee)
    else:
        task_data = AddTask.objects.all()

    paginator = Paginator(task_data, 5)  # Show 5 tasks per page

    page = request.GET.get('page')
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)

    d = {'tasks': tasks, 'emp_data': emp_data,
         'is_user_logged_in': is_user_logged_in}
    return render(request, 'task_list.html', d)


def edit_task(request, pid):
    is_user_logged_in = request.user.is_authenticated
    task_data = AddTask.objects.get(id=pid)
    assignee_options = Employee.objects.all()  # Retrieve all Assignee options

    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        assignee = request.POST['assignee']
        task_obj = AddTask.objects.filter(id=pid).update(
            title=title, description=description, assignee=assignee)
        messages.success(request, "Task Updated successfully")
        return redirect('employee-list')
    return render(request, 'edit_task.html', {'task_data': task_data, 'is_user_logged_in': is_user_logged_in, 'assignee_options': assignee_options})


def delete_task(request, pid):
    data = AddTask.objects.get(id=pid)
    data.delete()
    messages.success(request, "Task Deleted successfully")
    return redirect('employee-list')
