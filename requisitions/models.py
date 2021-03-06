from django.db import models
from basics.models import Component, Sap
from basics.rename import random, rename_file
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


class Requisition(models.Model):
    request = models.CharField(
        max_length=20,
        primary_key=True,
        unique=True,
        default=random()
    )
    created_requisition = models.DateTimeField(
        auto_now_add=True,
    )
    description = models.TextField(
        help_text='description of the requisition',
    )
    conclude = models.BooleanField(
        default=False,
    )

    @staticmethod
    def autocomplete_search_fields():
        return ("request__iexact", "request__icontains",)

    class Meta:
        unique_together = ('request', 'description')
        verbose_name = u'requisition'
        verbose_name_plural = u'requisitions'

    def __unicode__(self):
        return unicode(self.request)


class Reserve(models.Model):
    request = models.ForeignKey(
        Requisition,
        primary_key=True,
        unique=True,
    )
    reserve = models.CharField(
        max_length=10,
        unique=True,
    )
    sap_movement = models.ForeignKey(
        Sap,
        limit_choices_to={
            'type_sap': 'MV',
        },
        related_name='sap movement',
    )
    sap_destination = models.ForeignKey(
        Sap,
        limit_choices_to={
            'type_sap': 'DT',
        },
        related_name='sap destination',
    )
    division = models.ForeignKey(
        Sap,
        limit_choices_to={
            'type_sap': 'DV',
        },
        related_name='division',
    )
    order = models.CharField(
        _('order of budget'),
        max_length=25,
    )
    created_reserve = models.DateTimeField(
        _('creation date'),
        auto_now_add=True,
        help_text='item creation date',
    )
    support = models.FileField(
        upload_to=rename_file(
            'upload/requisition/reserve',
        ),
    )
    closing = models.BooleanField(
        default=False,
    )

    class Meta:
        unique_together = ('request', 'reserve',)
        verbose_name = u'reserve'
        verbose_name_plural = u'reserves'

    def __unicode__(self):
        return unicode(self.request)

@receiver(post_save, sender=Reserve)
def update_instance(sender, instance, created, **kwargs):
    if created:
        Material.objects.all().filter(
            request=instance,
        ).update(
            request_reserve=instance,
        )


class Material(models.Model):
    request = models.ForeignKey(
        Requisition,
        help_text='request number',
    )
    request_reserve = models.ForeignKey(
        Reserve,
        null=True,
        help_text='request number',
    )
    code_sap = models.ForeignKey(
        Component,
        help_text='sap basic model code',
    )
    solicitude = models.DecimalField(
        _('quantity applied'),
        max_digits=7,
        decimal_places=2,
        default=0,
    )
    created_solicitude = models.DateTimeField(
        _('creation date'),
        auto_now_add=True,
        help_text='item creation date',
    )
    center = models.ForeignKey(
        Sap,
        null=True,
        limit_choices_to={
            'type_sap': 'CT',
        },
        related_name='storehouse center',
    )
    warehouse = models.ForeignKey(
        Sap,
        null=True,
        limit_choices_to={
            'type_sap': 'AM',
        },
        related_name='storehouse',
    )
    generated = models.DecimalField(
        _('quantity generated'),
        max_digits=7,
        decimal_places=2,
        default=0,
    )
    created_generated = models.DateTimeField(
        _('creation date'),
        null=True,
        help_text='item creation date',
    )
    delivered = models.DecimalField(
        _('quantity delivered'),
        max_digits=7,
        decimal_places=2,
        default=0,
    )
    created_delivered = models.DateTimeField(
        _('creation date'),
        null=True,
        help_text='item creation date',
    )
    approved = models.BooleanField(
        default=False,
    )
    active = models.BooleanField(
        default=True,
    )
    dispatched = models.BooleanField(
        default=False,
    )

    class Meta:
        unique_together = ('request', 'code_sap')
        verbose_name = u'requested material'
        verbose_name_plural = u'requested material'

    def __unicode__(self):
        return unicode(self.code_sap)


class Agree(models.Model):
    request = models.ForeignKey(
        Requisition,
        primary_key=True,
        unique=True,
    )
    material = models.ManyToManyField(
        Material,
        limit_choices_to={
            'approved': False,
            'active': True,
        }
    )
    description = models.TextField()
    created_agree = models.DateTimeField(
        _('creation date'),
        auto_now_add=True,
        help_text='item creation date',
    )

    class Meta:
        unique_together = ('request',)
        verbose_name = u'accept request'
        verbose_name_plural = u'accept request'

    def __unicode__(self):
        return unicode(self.request)

@receiver(m2m_changed, sender=Agree.material.through)
def send_notification(sender, instance, action, **kwargs):
    if action in ['post_add']:
        approve_order = Agree.objects.all().values_list(
            'material',
            flat=True,
        ).filter(
            request=instance,
        )
        Material.objects.all().filter(
            request=instance,
            id__in=approve_order,
        ).update(
            active=False,
            approved=True,
        )
        Material.objects.all().filter(
            request=instance,
            active=True,
            approved=False,
        ).update(
            active=False,
        )
