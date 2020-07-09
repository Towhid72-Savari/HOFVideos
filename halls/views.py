from django.http import Http404
from django.shortcuts import render, redirect, reverse
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
    return render(request, 'halls/home.html')


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

                return redirect('detail_hall', pk)
            else:
                errors = form._errors.setdefault('url', ErrorList())
                errors.append('Needs to be an Youtube url')

    return render(request, 'halls/add_video.html', {'form': form,
                                                    'hall': hall,
                                                    'search_form': search_form})


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        view = super(SignUpView, self).form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)

        return view


class CreateHallView(generic.CreateView):
    model = models.Hall
    fields = ['title']
    template_name = 'halls/create_hall.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        super(CreateHallView, self).form_valid(form)

        return redirect('home')


class DetailHallView(generic.DetailView):
    model = models.Hall
    template_name = 'halls/detailed_hall.html'


class UpdateHallView(generic.UpdateView):
    model = models.Hall
    template_name = 'halls/update_hall.html'
    fields = ['title']
    success_url = reverse_lazy('home')


class DeleteHallView(generic.DeleteView):
    model = models.Hall
    template_name = 'halls/delete_hall.html'
    success_url = reverse_lazy('home')
