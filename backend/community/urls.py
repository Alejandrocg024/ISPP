from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from products.views import ProductsView  
from django.conf import settings
from django.conf.urls.static import static  
from community.views import PostViewClass
from community.views import GetUserFromTokenView


router = routers.DefaultRouter()
router.register('community', PostViewClass, basename='community')  # Register the community class

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('add-post', PostViewClass.create, name='add_post'),
    path('update-post/<int:pk>', PostViewClass.update, name='update_post'),
    path('delete-post/<int:pk>', PostViewClass.destroy, name='delete_post'),
    path('search-post', PostViewClass.get_queryset, name='search_post'),
    path('search-post/<int:pk>', PostViewClass.retrieve, name='search_post'),
    path('list-post', PostViewClass.list, name='list_post'),
    path('get_from_user', PostViewClass.get_post_by_usernames, name='get_from_user'),
    path('get_user_from_token', GetUserFromTokenView.as_view(), name='get_user_from_token'),
    path('get_post_by_user/<int:userid>', PostViewClass.get_post_by_userids, name='get_post_by_user'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)