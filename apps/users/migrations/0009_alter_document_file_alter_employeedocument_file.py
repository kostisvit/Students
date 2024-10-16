# Generated by Django 4.2 on 2024-10-06 14:32

from django.db import migrations, models
import users.models
import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_document_file_employeedocument'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='file',
            field=models.FileField(upload_to=users.models.student_directory_path, validators=[users.validators.validate_file_extension, users.validators.file_size_validator]),
        ),
        migrations.AlterField(
            model_name='employeedocument',
            name='file',
            field=models.FileField(upload_to=users.models.user_directory_path, validators=[users.validators.validate_file_extension, users.validators.file_size_validator]),
        ),
    ]
