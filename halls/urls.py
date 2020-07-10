from django.urls import path
from halls import views
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'halls'

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('halls/create/', views.CreateHallView.as_view(), name='create'),
    path('halls/<int:pk>/', views.DetailHallView.as_view(), name='detail_hall'),
    path('halls/<int:pk>/update', views.UpdateHallView.as_view(), name='update_hall'),
    path('halls/<int:pk>/delete', views.DeleteHallView.as_view(), name='delete_hall'),
    path('vidoes/<int:pk>/delete', views.DeleteVideoView.as_view(), name='delete_video'),
    path('halls/<int:pk>/addvideo', views.add_video, name='add_video'),
    path('video/search', views.video_search, name='video_search'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
