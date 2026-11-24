from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import PatientDoctorMapping
from patients.models import Patient
from doctors.models import Doctor
from .serializers import PatientDoctorMappingSerializer


class MappingListCreateView(generics.ListCreateAPIView):
    """
    POST /api/mappings/ - Assign a doctor to a patient
    GET /api/mappings/ - Retrieve all patient-doctor mappings
    """
    permission_classes = [IsAuthenticated]
    queryset = PatientDoctorMapping.objects.select_related('patient', 'doctor').all()
    serializer_class = PatientDoctorMappingSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get('patient_id')
        doctor_id = self.request.query_params.get('doctor_id')

        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)

        return queryset

    @extend_schema(
        summary="Retrieve all patient-doctor mappings",
        description="Returns all active assignments between patients and doctors.",
        responses={200: PatientDoctorMappingSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Assign a doctor to a patient",
        description="Creates an assignment mapping between a patient and a doctor.",
        request=PatientDoctorMappingSerializer,
        responses={
            201: PatientDoctorMappingSerializer,
            400: OpenApiResponse(description="Validation error or duplicate assignment")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            mapping = serializer.save()
            return Response({
                'success': True,
                'message': f"Doctor '{mapping.doctor.name}' successfully assigned to patient '{mapping.patient.name}'.",
                'data': self.get_serializer(mapping).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Failed to assign doctor to patient.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class MappingDetailOrPatientDoctorsView(APIView):
    """
    GET /api/mappings/<patient_id>/ - Get all doctors assigned to a specific patient
    DELETE /api/mappings/<id>/ - Remove a doctor from a patient (delete mapping by ID)
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get all doctors assigned to a specific patient",
        description="Returns all doctors assigned to the specified patient ID.",
        responses={
            200: OpenApiResponse(description="List of assigned doctors"),
            404: OpenApiResponse(description="Patient not found")
        }
    )
    def get(self, request, identifier):
        patient = get_object_or_404(Patient, pk=identifier)
        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('doctor')

        doctors_data = [
            {
                'mapping_id': m.id,
                'assigned_at': m.assigned_at,
                'notes': m.notes,
                'doctor': {
                    'id': m.doctor.id,
                    'name': m.doctor.name,
                    'specialization': m.doctor.specialization,
                    'contact_number': m.doctor.contact_number,
                    'email': m.doctor.email,
                    'years_of_experience': m.doctor.years_of_experience,
                    'hospital_affiliation': m.doctor.hospital_affiliation,
                }
            }
            for m in mappings
        ]

        return Response({
            'success': True,
            'patient': {
                'id': patient.id,
                'name': patient.name,
                'gender': patient.gender,
                'contact_number': patient.contact_number,
                'email': patient.email
            },
            'assigned_doctors_count': len(doctors_data),
            'doctors': doctors_data,
            'data': doctors_data
        }, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Remove a doctor from a patient",
        description="Deletes a patient-doctor mapping record by its mapping ID.",
        responses={
            200: OpenApiResponse(description="Mapping removed successfully"),
            404: OpenApiResponse(description="Mapping not found")
        }
    )
    def delete(self, request, identifier):
        # Find mapping by primary key
        mapping = get_object_or_404(PatientDoctorMapping, pk=identifier)
        mapping_id = mapping.id
        patient_name = mapping.patient.name
        doctor_name = mapping.doctor.name
        mapping.delete()

        return Response({
            'success': True,
            'message': f"Assignment (ID {mapping_id}) between Doctor '{doctor_name}' and Patient '{patient_name}' has been successfully removed."
        }, status=status.HTTP_200_OK)


class PatientDoctorsExplicitView(APIView):
    """
    Explicit alias:
    GET /api/mappings/patient/<patient_id>/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id)
        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('doctor')

        doctors_data = [
            {
                'mapping_id': m.id,
                'assigned_at': m.assigned_at,
                'notes': m.notes,
                'doctor': {
                    'id': m.doctor.id,
                    'name': m.doctor.name,
                    'specialization': m.doctor.specialization,
                    'contact_number': m.doctor.contact_number,
                    'email': m.doctor.email,
                    'years_of_experience': m.doctor.years_of_experience,
                    'hospital_affiliation': m.doctor.hospital_affiliation,
                }
            }
            for m in mappings
        ]

        return Response({
            'success': True,
            'patient': {
                'id': patient.id,
                'name': patient.name,
                'gender': patient.gender,
                'contact_number': patient.contact_number,
                'email': patient.email
            },
            'assigned_doctors_count': len(doctors_data),
            'doctors': doctors_data,
            'data': doctors_data
        }, status=status.HTTP_200_OK)
