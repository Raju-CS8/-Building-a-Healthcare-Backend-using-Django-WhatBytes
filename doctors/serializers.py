import re
from rest_framework import serializers
from .models import Doctor

PHONE_REGEX = re.compile(r'^\+?[0-9\s\-\(\)]{7,25}$')


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            'id',
            'name',
            'specialization',
            'contact_number',
            'email',
            'years_of_experience',
            'hospital_affiliation',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Doctor name cannot be empty.")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Doctor name must be at least 2 characters long.")
        return value.strip()

    def validate_specialization(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Specialization cannot be empty.")
        return value.strip()

    def validate_email(self, value):
        normalized = value.strip().lower()
        doctor_id = self.instance.id if self.instance else None
        if Doctor.objects.filter(email=normalized).exclude(id=doctor_id).exists():
            raise serializers.ValidationError("A doctor with this email already exists.")
        return normalized

    def validate_contact_number(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Contact number cannot be empty.")
        cleaned = value.strip()
        if not PHONE_REGEX.match(cleaned):
            raise serializers.ValidationError(
                "Invalid contact number format. Must contain 7 to 25 valid phone characters (digits, +, -, spaces, parentheses)."
            )
        return cleaned

    def validate_years_of_experience(self, value):
        if value is not None and (value < 0 or value > 80):
            raise serializers.ValidationError("Years of experience must be between 0 and 80.")
        return value


class DoctorDetailSerializer(DoctorSerializer):
    """
    Detailed Doctor serializer with assigned patients count and list.
    """
    assigned_patients = serializers.SerializerMethodField()

    class Meta(DoctorSerializer.Meta):
        fields = DoctorSerializer.Meta.fields + ['assigned_patients']

    def get_assigned_patients(self, obj):
        mappings = obj.patient_mappings.select_related('patient').all()
        return [
            {
                'mapping_id': m.id,
                'patient_id': m.patient.id,
                'patient_name': m.patient.name,
                'patient_gender': m.patient.gender,
                'contact_number': m.patient.contact_number,
                'assigned_at': m.assigned_at,
                'notes': m.notes,
            }
            for m in mappings
        ]
