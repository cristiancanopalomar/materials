# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('requisitions', '0011_auto_20150717_1818'),
    ]

    operations = [
        migrations.RenameField(
            model_name='agree',
            old_name='material_1',
            new_name='material',
        ),
    ]
