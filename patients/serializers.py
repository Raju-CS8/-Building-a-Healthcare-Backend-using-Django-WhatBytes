import re
from datetime import date
from rest_framework import serializers
from .models import Patient

PHONE_REGEX = re.compile(r'^\+?[0-9\s\-\(\)]{7,25}$')


class PatientSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.name')
    created_by_email = serializers.ReadOnlyField(source='created_by.email')

    class Meta:
        model = Patient
        fields = [
            'id',
            'name',
            'date_of_birth',
            'age',
            'gender',
            'contact_number',
            'email',
            'address',
            'medical_history',
            'created_by',
            'created_by_name',
            'created_by_email',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_by_name', 'created_by_email', 'created_at', 'updated_at']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Patient name cannot be empty.")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Patient name must be at least 2 characters long.")
        return value.strip()

    def validate_contact_number(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Contact number cannot be empty.")
        cleaned = value.strip()
        if not PHONE_REGEX.match(cleaned):
            raise serializers.ValidationError(
                "Invalid contact number format. Must contain 7 to 25 valid phone characters (digits, +, -, spaces, parentheses)."
            )
        return cleaned

    def validate_email(self, value):
        if value:
            return value.strip().lower()
        return value

    def validate_date_of_birth(self, value):
        if value:
            if value > date.today():
                raise serializers.ValidationError("Date of birth cannot be in the future.")
            if value < date(1880, 1, 1):
                raise serializers.ValidationError("Date of birth cannot be earlier than year 1880.")
        return value

    def validate_age(self, value):
        if value is not None and (value < 0 or value > 150):
            raise serializers.ValidationError("Age must be between 0 and 150.")
        return value

    def validate(self, attrs):
        # Auto-compute age if date_of_birth is given but age is omitted
        dob = attrs.get('date_of_birth')
        age = attrs.get('age')

        if dob and age is None:
            today = date.today()
            computed_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            attrs['age'] = max(0, computed_age)

        return attrs


class PatientDetailSerializer(PatientSerializer):
    """
    Detailed patient serializer including doctor assignments.
    """
    assigned_doctors = serializers.SerializerMethodField()

    class Meta(PatientSerializer.Meta):
        fields = PatientSerializer.Meta.fields + ['assigned_doctors']

    def get_assigned_doctors(self, obj):
        mappings = obj.doctor_mappings.select_related('doctor').all()
        return [
            {
                'mapping_id': m.id,
                'doctor_id': m.doctor.id,
                'doctor_name': m.doctor.name,
                'specialization': m.doctor.specialization,
                'contact_number': m.doctor.contact_number,
                'email': m.doctor.email,
                'assigned_at': m.assigned_at,
                'notes': m.notes,
            }
            for m in mappings
        ]
