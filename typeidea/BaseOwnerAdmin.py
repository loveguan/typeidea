from django.contrib import admin

class BaseOwnerAdmin(admin.ModelAdmin):
    exclude = ('owner',)

    def get_queryset(self, request):

        try:
            qs = super(BaseOwnerAdmin, self).get_queryset(request)
            qs=qs.filter(owner=request.user)
        except:
            qs=None
        return qs

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(BaseOwnerAdmin, self).save_model(request, obj, form, change)