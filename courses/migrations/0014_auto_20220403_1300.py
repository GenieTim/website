# Generated by Django 3.2.12 on 2022-04-03 11:00

import courses.models.voucher
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0013_alter_userprofile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='voucher',
            name='amount',
            field=models.IntegerField(blank=True, help_text='Value of the voucher in CHF.', null=True),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='expires',
            field=models.DateField(blank=True, help_text='If not set, the voucher will not expire.', null=True),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='key',
            field=models.CharField(default=courses.models.voucher.generate_key, help_text='Used to redeem voucher.', max_length=8, unique=True),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='pdf_file',
            field=models.FileField(blank=True, help_text='Will be generated.', null=True, upload_to='voucher/'),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='percentage',
            field=models.IntegerField(blank=True, help_text='Reduction in percent (0-100).', null=True),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='subscription',
            field=models.ForeignKey(blank=True, help_text='The voucher was applied for this subscription.', null=True, on_delete=django.db.models.deletion.PROTECT, to='courses.subscribe'),
        ),
        migrations.AddConstraint(
            model_name='voucher',
            constraint=models.CheckConstraint(check=models.Q(('percentage__isnull', True), models.Q(('percentage__gte', 0), ('percentage__lte', 100)), _connector='OR'), name='percentage is null or between 0 and 100'),
        ),
        migrations.AddConstraint(
            model_name='voucher',
            constraint=models.CheckConstraint(check=models.Q(('amount__isnull', True), ('amount__gte', 0), _connector='OR'), name='amount is null or non-negative'),
        ),
        migrations.AddConstraint(
            model_name='voucher',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('amount__isnull', False), ('amount__gt', 0), models.Q(('percentage__isnull', True), ('percentage', 0), _connector='OR')), models.Q(('percentage__isnull', False), ('percentage__gt', 0), models.Q(('amount__isnull', True), ('amount', 0), _connector='OR')), _connector='OR'), name='either amount or percentage set (not both'),
        ),
        migrations.AlterField(
            model_name='subscribe',
            name='paymentmethod',
            field=models.CharField(blank=True, choices=[('counter', 'counter'), ('course', 'course'), ('online', 'online'), ('voucher', 'voucher'), ('reduction', 'price reduction')], max_length=30, null=True),
        ),
        migrations.CreateModel(
            name='PriceReduction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('comment', models.CharField(blank=True, max_length=128, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_reductions', to='courses.subscribe')),
                ('used_voucher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='price_reductions', to='courses.voucher')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]