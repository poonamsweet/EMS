from turtle import pos
import django
from django.shortcuts import redirect, render
from .models import  Employee
from django.contrib import messages 
from django.contrib.auth import authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as authlogin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def home(request):
    emp_data = Employee.objects.filter()
    on_leave = emp_data.filter(on_leave=True)
    is_user_logged_in = request.user.is_authenticated
    d = {'total_employee': emp_data.count(), 'on_leave': on_leave.count(), 'is_user_logged_in': is_user_logged_in}
    return render(request, 'dashboard.html', d)

################ login forms################################################### 

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            form = authlogin(request, user)
            messages.success(request, f' welcome {username} !!')
            return redirect('employee_list')
        else:
            messages.info(request, f'account done not exit plz sign in')
    form = AuthenticationForm()
    return render(request, 'login.html', {'form':form, 'title':'log in'})
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
        emp_obj = Employee.objects.create(name=name,dob=dob,doj=doj,address=address,city=city,state=state,zipcode=zipcode,country=country,department=department,post=post)
        messages.success(request, "Employee created successfully")
        return redirect('employee_list')
    return render(request, 'create_employeee.html', {'is_user_logged_in': is_user_logged_in})

def employee_list(request):
    emp_data = Employee.objects.all()
    paginator = Paginator(emp_data, 2)  # Show 10 employees per page

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
    emp_data =Employee.objects.get(id=pid)
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
        emp_obj = Employee.objects.filter(id=pid).update(name=name,dob=dob,doj=doj,address=address,city=city,state=state,zipcode=zipcode,country=country,department=department,post=post)
        messages.success(request, "Employee Updated successfully")
        return redirect('employee_list')
    return render(request, 'edit_employeee.html', {'emp_data':emp_data, 'is_user_logged_in': is_user_logged_in})

def delete_employee(request, pid):
    data = Employee.objects.get(id=pid)
    data.delete()
    messages.success(request, "Employee Deleted successfully")
    return redirect('employee_list')

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