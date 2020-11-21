from django.urls import path
from .views.mango_views import Mangos, MangoDetail

urlpatterns = [
	  # Restful routing
    path('mangos/', Mangos.as_view(), name='mangos'),
    path('mangos/<int:pk>/', MangoDetail.as_view(), name='mango_detail')
]
