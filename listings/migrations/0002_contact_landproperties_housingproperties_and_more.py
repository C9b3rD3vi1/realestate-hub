# Generated by Django 4.2.23 on 2025-07-24 12:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='LandProperties',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('image', models.ImageField(upload_to='land_images/')),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('location', models.CharField(max_length=255)),
                ('size', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_available', models.BooleanField(default=True)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Land Properties',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='HousingProperties',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('image', models.ImageField(upload_to='housing_images/')),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('location', models.CharField(max_length=255)),
                ('size', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_available', models.BooleanField(default=True)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Housing Properties',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CarProperties',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('image', models.ImageField(upload_to='car_images/')),
                ('description', models.TextField()),
                ('make', models.CharField(choices=[('toyota', 'Toyota'), ('honda', 'Honda'), ('ford', 'Ford'), ('chevrolet', 'Chevrolet'), ('nissan', 'Nissan'), ('bmw', 'BMW'), ('audi', 'Audi'), ('mercedes', 'Mercedes-Benz'), ('volkswagen', 'Volkswagen'), ('hyundai', 'Hyundai'), ('kia', 'Kia'), ('subaru', 'Subaru'), ('mazda', 'Mazda'), ('volvo', 'Volvo'), ('land_rover', 'Land Rover'), ('jaguar', 'Jaguar'), ('porsche', 'Porsche'), ('tesla', 'Tesla'), ('other', 'Other')], default='toyota', max_length=255)),
                ('model', models.CharField(choices=[('corolla', 'Corolla'), ('civic', 'Civic'), ('mustang', 'Mustang'), ('camaro', 'Camaro'), ('altima', 'Altima'), ('3_series', '3 Series'), ('a4', 'A4'), ('c_class', 'C-Class'), ('golf', 'Golf'), ('elantra', 'Elantra'), ('soul', 'Soul'), ('forester', 'Forester'), ('cx_5', 'CX-5'), ('xc60', 'XC60'), ('discovery', 'Discovery'), ('f_type', 'F-Type'), ('911', '911'), ('model_s', 'Model S'), ('model_3', 'Model 3'), ('202', '202'), ('v8', 'V8'), ('suv', 'SUV'), ('pickup', 'Pickup'), ('sedan', 'Sedan'), ('hatchback', 'Hatchback'), ('convertible', 'Convertible'), ('coupe', 'Coupe'), ('wagon', 'Wagon'), ('van', 'Van'), ('other', 'Other')], default='corolla', max_length=255)),
                ('year_of_manufacture', models.PositiveIntegerField()),
                ('mileage', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fuel_type', models.CharField(choices=[('petrol', 'Petrol'), ('diesel', 'Diesel'), ('electric', 'Electric'), ('hybrid', 'Hybrid')], default='petrol', max_length=50)),
                ('engine_size', models.DecimalField(decimal_places=2, max_digits=10)),
                ('number_of_doors', models.PositiveIntegerField()),
                ('number_of_seats', models.PositiveIntegerField()),
                ('transmission', models.CharField(choices=[('manual', 'Manual'), ('automatic', 'Automatic')], default='automatic', max_length=50)),
                ('color', models.CharField(max_length=50)),
                ('features', models.TextField(blank=True, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('location', models.CharField(max_length=255)),
                ('size', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_available', models.BooleanField(default=True)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Car Properties',
                'ordering': ['-created_at'],
            },
        ),
    ]
