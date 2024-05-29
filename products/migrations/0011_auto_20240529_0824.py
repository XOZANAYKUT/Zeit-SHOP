from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


def set_default_timestamps(apps, schema_editor):
    Rating = apps.get_model('products', 'Rating')
    for rating in Rating.objects.all():
        rating.created_at = django.utils.timezone.now()
        rating.updated_at = django.utils.timezone.now()
        rating.save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0010_auto_20240528_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rating',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='rating',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.RunPython(set_default_timestamps),
        migrations.AlterField(
            model_name='rating',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='rating',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterUniqueTogether(
            name='rating',
            unique_together={('product', 'user')},
        ),
    ]