from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from halls import models, forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.forms.utils import ErrorList
import urllib
import requests

YOUTUBE_API_KEY = 'AIzaSyBe4JQtiNcdoiNIy6ufBOwBzStIHLr1uVY'


def home(request):
    recent_halls = models.Hall.objects.all().order_by('-id')[:3]
    return render(request, 'halls/home.html', {'recent_halls': recent_halls})


@login_required(login_url='halls:login')
def dashboard(request):
    halls = models.Hall.objects.filter(user=request.user)
    return render(request, 'halls/dashboard.html', {'halls': halls})


@login_required(login_url='halls:login')
def video_search(request):
    search_form = forms.SearchFrom(request.GET)
    if search_form.is_valid():
        encoded_search_term = search_form.cleaned_data['search_term']
        response = requests.get(f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=6&q={encoded_search_term}&key={YOUTUBE_API_KEY}')
        return JsonResponse(response.json())
    return JsonResponse({'error': 'Not able to validate form'})


@login_required(login_url='halls:login')
def add_video(request, pk):
    form = forms.VideoForm()
    search_form = forms.SearchFrom()
    hall = models.Hall.objects.get(pk=pk)
    if not hall.user == request.user:
        raise Http404
    if request.method == 'POST':
        form = forms.VideoForm(request.POST)
        if form.is_valid():
            video = models.Video()
            video.hall = hall
            video.url = form.cleaned_data['url']
            parsed_url = urllib.parse.urlparse(video.url)
            video_id = urllib.parse.parse_qs(parsed_url.query).get('v')
            if video_id:
                video.youtube_id = video_id[0]
                response = requests.get(f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id[0]}&key={YOUTUBE_API_KEY}')
                json_res = response.json()
                video.title = json_res['items'][0]['snippet']['title']
                video.save()

                return redirect('halls:detail_hall', pk)
            else:
                errors = form._errors.setdefault('url', ErrorList())
                errors.append('Needs to be an Youtube url')

    return render(request, 'halls/add_video.html', {'form': form,
                                                    'hall': hall,
                                                    'search_form': search_form})


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('halls:home')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        view = super(SignUpView, self).form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)

        return view


class CreateHallView(LoginRequiredMixin, generic.CreateView):
    model = models.Hall
    fields = ['title']
    template_name = 'halls/create_hall.html'
    success_url = reverse_lazy('halls:dashboard')
    login_url = 'halls:login'

    def form_valid(self, form):
        form.instance.user = self.request.user
        super(CreateHallView, self).form_valid(form)

        return redirect('halls:dashboard')


class DetailHallView(generic.DetailView):
    model = models.Hall
    template_name = 'halls/detailed_hall.html'


class UpdateHallView(LoginRequiredMixin, generic.UpdateView):
    model = models.Hall
    template_name = 'halls/update_hall.html'
    fields = ['title']
    success_url = reverse_lazy('halls:dashboard')
    login_url = 'halls:login'

    def get_object(self, queryset=None):
        hall = super(UpdateHallView, self).get_object()
        if not hall.user == self.request.user:
            raise Http404
        return hall


class DeleteHallView(LoginRequiredMixin, generic.DeleteView):
    model = models.Hall
    template_name = 'halls/delete_hall.html'
    success_url = reverse_lazy('halls:dashboard')
    login_url = 'halls:login'

    def get_object(self, queryset=None):
        hall = super(DeleteHallView, self).get_object()
        if not hall.user == self.request.user:
            raise Http404
        return hall


class DeleteVideoView(LoginRequiredMixin, generic.DeleteView):
    model = models.Video
    template_name = 'halls/delete_video.html'
    success_url = reverse_lazy('halls:dashboard')
    login_url = 'halls:login'

    def get_object(self, queryset=None):
        video = super(DeleteVideoView, self).get_object()
        if not video.hall.user == self.request.user:
            raise Http404
        return video
