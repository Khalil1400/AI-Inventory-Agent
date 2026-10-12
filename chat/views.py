from django.shortcuts import redirect, render
from .agent import run_agent
from .local_commands import run_local_command


def chat_view(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if user_message:
            history = request.session.get('history', [])
            interaction_id = request.session.get('interaction_id')
            history.append({'role': 'user', 'text': user_message})
            try:
                answer = run_local_command(user_message)
                if answer is None:
                    answer, new_id = run_agent(user_message, interaction_id)
                    request.session['interaction_id'] = new_id
            except Exception as exc:
                answer = f'Something went wrong: {exc}'
            history.append({'role': 'agent', 'text': answer})
            request.session['history'] = history
        return redirect('chat')
    return render(request, 'chat.html', {'history': request.session.get('history', [])})


def reset_view(request):
    request.session.flush()
    return redirect('chat')
