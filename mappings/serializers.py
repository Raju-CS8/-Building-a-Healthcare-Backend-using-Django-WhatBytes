from rest_framework import serializers
from .models import PatientDoctorMapping
from patients.models import Patient
from doctors.models import Doctor
from patients.serializers import PatientSerializer
from doctors.serializers import DoctorSerializer


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        source='doctor',
        write_only=True
    )
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = [
            'id',
            'patient_id',
            'doctor_id',
            'patient',
            'doctor',
            'assigned_at',
            'notes',
        ]
        read_only_fields = ['id', 'patient', 'doctor', 'assigned_at']

    def validate(self, attrs):
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')

        # Check unique constraint if creating new mapping
        if self.instance is None:
            if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
                raise serializers.ValidationError(
                    f"Doctor '{doctor.name}' is already assigned to Patient '{patient.name}'."
                )

        return attrs


class AssignedDoctorItemSerializer(serializers.Serializer):
    mapping_id = serializers.IntegerField()
    assigned_at = serializers.DateTimeField()
    notes = serializers.CharField(allow_blank=True, allow_null=True)
    doctor = DoctorSerializer()
