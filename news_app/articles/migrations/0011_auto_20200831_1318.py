# Generated by Django 3.0.9 on 2020-08-31 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0010_auto_20200831_1233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsapiquery',
            name='language',
            field=models.CharField(blank=True, choices=[('ar', 'Arabic'), ('de', 'German'), ('en', 'English'), ('es', 'Spanish'), ('fr', 'French'), ('he', 'Hebrew'), ('it', 'Italian'), ('nl', 'Dutch'), ('no', 'Norwegian'), ('pt', 'Portuguese'), ('ru', 'Russian'), ('se', 'Swedish'), ('zh', 'Chinese')], max_length=2, null=True),
        ),
    ]
