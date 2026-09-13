from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from datetime import timedelta
from .models import Task


def register(request):

    if request.method == 'POST':

        form = UserCreationForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect('task_list')

    else:

        form = UserCreationForm()

    return render(
        request,
        'tasks/register.html',
        {'form': form}
    )


@login_required
def task_list(request):

    if request.method == 'POST':

        # Add Task
        if 'add_task' in request.POST:

            title = request.POST.get('title')

            description = request.POST.get(
                'description',
                ''
            )

            priority = request.POST.get(
                'priority',
                'medium'
            )

            category = request.POST.get(
                'category',
                'other'
            )

            due_date = request.POST.get(
                'due_date'
            )

            if title:

                Task.objects.create(
                    user=request.user,
                    title=title,
                    description=description,
                    priority=priority,
                    category=category,
                    due_date=due_date if due_date else None
                )


        # Toggle Task Completion
        elif 'complete_task' in request.POST:

            task_id = request.POST.get(
                'task_id'
            )

            task = Task.objects.get(
                id=task_id,
                user=request.user
            )

            task.completed = not task.completed

            task.save()


        # Toggle Important
        elif 'important_task' in request.POST:

            task_id = request.POST.get(
                'task_id'
            )

            task = Task.objects.get(
                id=task_id,
                user=request.user
            )

            task.important = not task.important

            task.save()


        # Edit Task
        elif 'edit_task' in request.POST:

            task_id = request.POST.get(
                'task_id'
            )

            new_title = request.POST.get(
                'new_title'
            )

            new_description = request.POST.get(
                'new_description',
                ''
            )

            new_priority = request.POST.get(
                'new_priority',
                'medium'
            )

            new_category = request.POST.get(
                'new_category',
                'other'
            )

            new_due_date = request.POST.get(
                'new_due_date'
            )

            if new_title:

                task = Task.objects.get(
                    id=task_id,
                    user=request.user
                )

                task.title = new_title

                task.description = new_description

                task.priority = new_priority

                task.category = new_category

                task.due_date = (
                    new_due_date
                    if new_due_date
                    else None
                )

                task.save()


        # Delete Task
        elif 'delete_task' in request.POST:

            task_id = request.POST.get(
                'task_id'
            )

            task = Task.objects.get(
                id=task_id,
                user=request.user
            )

            task.delete()


        return redirect('task_list')


    # Get all tasks of logged-in user

    all_tasks = Task.objects.filter(
        user=request.user
    )


    # Statistics

    total_tasks = all_tasks.count()

    completed_tasks = all_tasks.filter(
        completed=True
    ).count()

    pending_tasks = all_tasks.filter(
        completed=False
    ).count()


    today = timezone.localdate()


    overdue_tasks = all_tasks.filter(
        completed=False,
        due_date__lt=today
    ).count()


    # Tasks for display

    tasks = all_tasks


    # Get search text

    search_query = request.GET.get(
        'search',
        ''
    ).strip()


    # Apply search

    if search_query:

        tasks = tasks.filter(
            title__icontains=search_query
        )


    # Get selected status filter

    current_filter = request.GET.get(
        'filter',
        'all'
    )


    # Apply status filter

    if current_filter == 'pending':

        tasks = tasks.filter(
            completed=False
        )

    elif current_filter == 'completed':

        tasks = tasks.filter(
            completed=True
        )

    elif current_filter == 'important':

        tasks = tasks.filter(
            important=True
        )


    # Get selected category

    current_category = request.GET.get(
        'category',
        'all'
    )


    # Apply category filter

    if current_category != 'all':

        tasks = tasks.filter(
            category=current_category
        )


    # Get selected sorting option

    current_sort = request.GET.get(
        'sort',
        'newest'
    )


    # Apply sorting

    if current_sort == 'oldest':

        tasks = tasks.order_by(
            'created_at'
        )

    elif current_sort == 'due_date':

        tasks = tasks.order_by(
            'due_date',
            '-created_at'
        )

    elif current_sort == 'priority':

        tasks = tasks.order_by(
            'priority',
            '-created_at'
        )

    else:

        tasks = tasks.order_by(
            '-created_at'
        )


    # Date information

    yesterday = today - timedelta(days=1)


    for task in tasks:

        task_date = timezone.localtime(
            task.created_at
        ).date()


        if task_date == today:

            task.date_label = "Today"

        elif task_date == yesterday:

            task.date_label = "Yesterday"

        else:

            task.date_label = timezone.localtime(
                task.created_at
            ).strftime("%b %d, %Y")


        task.time_label = timezone.localtime(
            task.created_at
        ).strftime("%I:%M %p")


        # Check if task is overdue

        if (
            task.due_date
            and task.due_date < today
            and not task.completed
        ):

            task.is_overdue = True

        else:

            task.is_overdue = False


    return render(
        request,
        'tasks/task_list.html',
        {
            'tasks': tasks,

            'current_filter': current_filter,

            'search_query': search_query,

            'current_category': current_category,

            'current_sort': current_sort,

            'total_tasks': total_tasks,

            'completed_tasks': completed_tasks,

            'pending_tasks': pending_tasks,

            'overdue_tasks': overdue_tasks
        }
    )