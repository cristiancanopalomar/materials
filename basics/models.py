import json
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .rename import rename_file
from .tasks import send_trigger_email
from django.utils.translation import ugettext_lazy as _


class Process(models.Model):
    """
    differentiating according to the type code,
    we hold the joint in materials and activities.

    'M'
        0   'ALUMBRADO'
        1   'CAJAS'
    'A'
        1   'INSPECCIONES'
        2   'CARTERA'
    """
    type_code = (
        ('M', 'material'),
        ('A', 'activity'),
    )
    code_process = models.PositiveIntegerField()
    description = models.CharField(
        max_length=15,
        help_text='description of the material or activity',
    )
    type_process = models.CharField(
        max_length=1,
        choices=type_code,
    )
    created_process = models.DateTimeField(
        _('creation date'),
        auto_now_add=True,
        help_text='item creation date',
    )
    active_process = models.BooleanField(
        default=True
    )

    class Meta:
        unique_together = ('code_process', 'type_process')
        verbose_name = u'code [process - activity]'
        verbose_name_plural = u'code [process - activity]'

    def __unicode__(self):
        return unicode(self.description)


class Component(models.Model):
    """
    here the material or component serial is entered
    (including configuration or type of measure).

    You can also add an image :)
    """
    type_unit = (
        ( 'M', 'meters'),
        ('CU', 'units' ),
    )
    type_process = models.ForeignKey(
        'Process',
        limit_choices_to={
            'type_process': 'M',
            'active_process': True,
        },
    )
    code_component = models.PositiveIntegerField(
        unique=True,
    )
    code_sap = models.CharField(
        max_length=10,
        primary_key=True,
        unique=True,
        help_text='material code (trading system SAP)',
    )
    description = models.CharField(
        max_length=100,
        help_text='description of the Component',
    )
    image = models.ImageField(
        upload_to=rename_file(
            'upload/basic/component',
        ),
    )
    unit = models.CharField(
        max_length=2,
        choices=type_unit,
    )
    created_component = models.DateTimeField(
        _('creation date'),
        auto_now_add=True,
        help_text='item creation date',
    )
    active_component = models.BooleanField(
        default=True,
    )

    @staticmethod
    def autocomplete_search_fields():
        return ("code_sap__iexact", "code_component__icontains",)

    class Meta:
        unique_together = ('code_component', 'code_sap', 'description')
        verbose_name = u'component not serialized'
        verbose_name_plural = u'component not serialized'

    def __unicode__(self):
        return unicode(self.description)

# notify users belonging to systems
@receiver(post_save, sender=Component)
def send_notification(sender, instance, created, **kwargs):
    if created:
        user_group = User.objects.all().values_list(
            'email',
            flat=True,
        ).filter(
            groups__name='system',
        )
        # conf email
        send_trigger_email.delay(
            subject_email = 'a new item was created',
            from_email = "CRISTIAN.CANO@eec.com.co",
            to_email = list(user_group),
            content_email = """
                <h2>Hello,</h2>
                <p>we know that play an important role in our app,
                so we inform you of the most important changes as follows:</p>
                <br>
                <li> in the component module, a new item '{}' is added.</li>
                <br><p>
                for more information, we invite you to enter the admin panel.</p>
            """.format(instance),
            content_type = 'text/html',
        )


class Prototype(models.Model):
    """
    We define the basic structure for the creation
    of the material (in the system gemini).

    in code all the information is concatenated.
    """
    code_prototype = models.CharField(
        max_length=50,
        primary_key=True,
        unique=True,
    )
    type_prototype = models.CharField(
        max_length=15,
    )
    model = models.CharField(
        max_length=10,
    )
    make = models.CharField(
        max_length=3,
    )
    seal_series = models.CharField(
        max_length=2,
        blank=True,
    )
    code_color = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    format_prototype = models.CharField(
        max_length=10,
        help_text='other material format (used in gemini)'
    )
    created_prototype = models.DateTimeField(
        _('creation date'),
        auto_now_add=True,
        help_text='item creation date',
    )
    active_prototype = models.BooleanField(
        default=True,
    )

    class Meta:
		unique_together = ('code_prototype', 'type_prototype', 'format_prototype')
		verbose_name = u'component serialized'
		verbose_name_plural = u'component serialized'

    def __unicode__(self):
        return unicode(self.code_prototype)


class Sap(models.Model):
    type_move = (
        ('MV', 'sap movement'),
        ('DT', 'sap destination'),
        ('DV', 'division'),
        ('CT', 'storehouse center'),
        ('AM', 'storehouse')
    )
    code_sap = models.CharField(
        max_length=10,
        primary_key=True,
        unique=True,
    )
    description = models.CharField(
        max_length=25,
        help_text='',
    )
    type_sap = models.CharField(
        max_length=2,
        choices=type_move,
    )
    created_sap = models.DateTimeField(
        _('creation date'),
        auto_now_add=True,
        help_text='item creation date',
    )
    active_sap = models.BooleanField(
        default=True,
    )

    @staticmethod
    def autocomplete_search_fields():
        return ("code_sap__iexact", "description__icontains",)

    class Meta:
		unique_together = ('code_sap', 'description')
		verbose_name = u'sap records'
		verbose_name_plural = u'sap records'

    def __unicode__(self):
        return unicode(self.description)


@receiver(post_save, sender=Sap)
def send_notification(sender, instance, created, **kwargs):
    if created:
        user_group = User.objects.all().values_list(
            'email',
            flat=True,
        ).filter(
            groups__name__in=[
                'area',
                'manager',
                'system',
            ]
        )
        # conf email
        send_trigger_email.delay(
            subject_email = 'a new item was created',
            from_email = "CRISTIAN.CANO@eec.com.co",
            to_email = list(user_group),
            content_email = """
                <h2>Hello,</h2>
                <p>we know that play an important role in our app,
                so we inform you of the most important changes as follows:</p>
                <br>
                <li> in the sap module, a new item '{}' is added.</li>
                <br><p>
                for more information, we invite you to enter the admin panel.</p>
            """.format(instance),
            content_type = 'text/html',
        )
