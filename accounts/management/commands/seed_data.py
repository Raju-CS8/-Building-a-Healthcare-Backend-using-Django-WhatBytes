from django.core.management.base import BaseCommand
from accounts.models import User
from patients.models import Patient
from doctors.models import Doctor
from mappings.models import PatientDoctorMapping


class Command(BaseCommand):
    help = 'Populates the database with realistic sample healthcare data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding sample healthcare data...")

        # Create demo users
        user, created = User.objects.get_or_create(
            email='intern@healthcare.com',
            defaults={
                'name': 'Intern Developer',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            user.set_password('YourNewPassword123')
            user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user: intern@healthcare.com / YourNewPassword123"))

        # Create doctors
        doctors_data = [
            {
                'name': 'Gregory House',
                'specialization': 'Diagnostic Medicine & Nephrology',
                'contact_number': '+1-555-0101',
                'email': 'drhouse@diagnostics.org',
                'years_of_experience': 22,
                'hospital_affiliation': 'Princeton-Plainsboro Teaching Hospital'
            },
            {
                'name': 'James Wilson',
                'specialization': 'Medical Oncology',
                'contact_number': '+1-555-0102',
                'email': 'drwilson@oncology.org',
                'years_of_experience': 18,
                'hospital_affiliation': 'Princeton-Plainsboro Teaching Hospital'
            },
            {
                'name': 'Lisa Cuddy',
                'specialization': 'Endocrinology',
                'contact_number': '+1-555-0103',
                'email': 'drcuddy@admin.hospital.org',
                'years_of_experience': 20,
                'hospital_affiliation': 'Princeton-Plainsboro Teaching Hospital'
            }
        ]

        doctors = []
        for d_info in doctors_data:
            doc, _ = Doctor.objects.get_or_create(email=d_info['email'], defaults=d_info)
            doctors.append(doc)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(doctors)} doctors."))

        # Create patients
        patients_data = [
            {
                'name': 'John Doe',
                'date_of_birth': '1988-03-14',
                'age': 38,
                'gender': 'male',
                'contact_number': '+1-555-0201',
                'email': 'johndoe@example.com',
                'address': '742 Evergreen Terrace, Springfield',
                'medical_history': 'History of mild seasonal allergies. Non-smoker.',
                'created_by': user
            },
            {
                'name': 'Jane Roe',
                'date_of_birth': '1995-07-22',
                'age': 31,
                'gender': 'female',
                'contact_number': '+1-555-0202',
                'email': 'janeroe@example.com',
                'address': '100 Main Street, Suite 4B, Metropolis',
                'medical_history': 'Type 1 Diabetes managed with insulin pump.',
                'created_by': user
            }
        ]

        patients = []
        for p_info in patients_data:
            patient, _ = Patient.objects.get_or_create(
                name=p_info['name'],
                created_by=p_info['created_by'],
                defaults=p_info
            )
            patients.append(patient)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(patients)} patients."))

        # Create mappings
        if patients and doctors:
            mapping, _ = PatientDoctorMapping.objects.get_or_create(
                patient=patients[0],
                doctor=doctors[0],
                defaults={'notes': 'Assigned for diagnostic workup.'}
            )
            mapping2, _ = PatientDoctorMapping.objects.get_or_create(
                patient=patients[1],
                doctor=doctors[2],
                defaults={'notes': 'Endocrine metabolic management.'}
            )
            self.stdout.write(self.style.SUCCESS("Seeded patient-doctor mappings."))

        self.stdout.write(self.style.SUCCESS("Sample data seeding completed successfully!"))
