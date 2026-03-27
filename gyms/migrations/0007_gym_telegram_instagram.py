from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gyms', '0006_alter_gymrating_options_gymrating_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='gym',
            name='telegram_url',
            field=models.URLField(blank=True, default='', max_length=500, verbose_name='Telegram'),
        ),
        migrations.AddField(
            model_name='gym',
            name='instagram_url',
            field=models.URLField(blank=True, default='', max_length=500, verbose_name='Instagram'),
        ),
    ]
