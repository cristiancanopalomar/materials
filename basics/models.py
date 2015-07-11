from django.db import models
from .rename import rename_file


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
    active_component = models.BooleanField(
        default=True,
    )

    class Meta:
        unique_together = ('code_component', 'code_sap', 'description')
        verbose_name = u'component not serialized'
        verbose_name_plural = u'component not serialized'

    def __unicode__(self):
        return unicode(self.description)


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

    class Meta:
		unique_together = ('code_prototype', 'type_prototype', 'format_prototype')
		verbose_name = u'component serialized'
		verbose_name_plural = u'component serialized'

	def __unicode__(self):
		return unicode(self.code_prototype)
