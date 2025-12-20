from django.contrib import admin

class BaseAdmin(admin.ModelAdmin):
    readonly_fields = ['id','created_at','updated_at']

class BaseStackedInline(admin.StackedInline):

    readonly_fields = ['id']
    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)

        self.__check_attr('created_at')
        self.__check_attr('updated_at')

    def __check_attr(self,attr):
        if hasattr(self.model,attr):
            self.readonly_fields.append(attr)



