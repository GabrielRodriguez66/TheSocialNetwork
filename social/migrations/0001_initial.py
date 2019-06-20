# Generated by Django 2.1.2 on 2019-06-19 15:37

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendRequested',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('pub_date', models.DateTimeField(default=datetime.datetime(2019, 6, 19, 11, 37, 29, 222082), verbose_name='date published')),
            ],
        ),
        migrations.CreateModel(
            name='SocialNetworkUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friends', models.ManyToManyField(related_name='_socialnetworkuser_friends_+', to='social.SocialNetworkUser')),
                ('requesting', models.ManyToManyField(to='social.FriendRequested')),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social.SocialNetworkUser'),
        ),
        migrations.AddField(
            model_name='message',
            name='recipients',
            field=models.ManyToManyField(blank=True, related_name='friend_list', to='social.SocialNetworkUser'),
        ),
        migrations.AddField(
            model_name='friendrequested',
            name='destinatario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receptor', to='social.SocialNetworkUser'),
        ),
        migrations.AddField(
            model_name='friendrequested',
            name='remitente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fuente', to='social.SocialNetworkUser'),
        ),
    ]
