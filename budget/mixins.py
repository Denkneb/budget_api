from django.db import IntegrityError


class SingleInstanceMixin:

    def save(self, *args, **kwargs):
        model = self.__class__
        if (model.objects.count() > 0 and self.pk != model.objects.get().pk):
            raise IntegrityError('Can only create 1 %s instance' % model.__name__)
        super(SingleInstanceMixin, self).save(*args, **kwargs)