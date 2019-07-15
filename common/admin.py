from django.contrib import admin

from common.models import EmailTemplate, Configuration, ConfigurationFireBase, PushTemplate

admin.site.register(EmailTemplate)
admin.site.register(Configuration)
admin.site.register(PushTemplate)
admin.site.register(ConfigurationFireBase)
