# Generated migration — Hospital–BloodRequest integration
# Adds an optional FK from BloodRequest to HospitalProfile.
# Existing rows default to NULL (no data migration required).

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blood_requests', '0003_donornotification'),
        ('hospitals', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bloodrequest',
            name='linked_hospital',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='linked_blood_requests',
                to='hospitals.hospitalprofile',
                verbose_name='Linked Hospital Profile',
            ),
        ),
    ]
