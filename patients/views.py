from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Patient
from .permissions import IsOwnerOrAdmin
from .serializers import PatientSerializer, PatientDetailSerializer


class PatientListCreateView(generics.ListCreateAPIView):
    """
    POST /api/patients/ - Add a new patient (Authenticated users only)
    GET /api/patients/ - Retrieve all patients created by the authenticated user
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PatientSerializer

    def get_queryset(self):
        # Only retrieve patients created by the authenticated user
        return Patient.objects.filter(created_by=self.request.user)

    @extend_schema(
        summary="List all patients created by current user",
        description="Returns all patient records created by the authenticated user.",
        responses={200: PatientSerializer(many=True)}
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
        summary="Add a new patient",
        description="Creates a new patient record associated with the authenticated user.",
        request=PatientSerializer,
        responses={
            201: PatientSerializer,
            400: OpenApiResponse(description="Validation error")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            patient = serializer.save(created_by=request.user)
            return Response({
                'success': True,
                'message': 'Patient created successfully.',
                'data': self.get_serializer(patient).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Failed to create patient.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/patients/<id>/ - Get details of a specific patient
    PUT /api/patients/<id>/ - Update patient details
    DELETE /api/patients/<id>/ - Delete a patient record
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    queryset = Patient.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PatientDetailSerializer
        return PatientSerializer

    @extend_schema(
        summary="Get details of a specific patient",
        description="Retrieves details and assigned doctors for a specific patient.",
        responses={
            200: PatientDetailSerializer,
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Patient not found")
        }
    )
    def get(self, request, *args, **kwargs):
        patient = self.get_object()
        serializer = self.get_serializer(patient)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update patient details",
        description="Updates full details of a specific patient.",
        request=PatientSerializer,
        responses={
            200: PatientSerializer,
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Patient not found")
        }
    )
    def put(self, request, *args, **kwargs):
        patient = self.get_object()
        serializer = self.get_serializer(patient, data=request.data)
        if serializer.is_valid():
            updated_patient = serializer.save()
            return Response({
                'success': True,
                'message': 'Patient details updated successfully.',
                'data': self.get_serializer(updated_patient).data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'message': 'Validation failed while updating patient.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Partial update patient details",
        description="Partially updates details of a specific patient.",
        request=PatientSerializer,
        responses={200: PatientSerializer, 400: OpenApiResponse(description="Validation error")}
    )
    def patch(self, request, *args, **kwargs):
        patient = self.get_object()
        serializer = self.get_serializer(patient, data=request.data, partial=True)
        if serializer.is_valid():
            updated_patient = serializer.save()
            return Response({
                'success': True,
                'message': 'Patient details updated successfully.',
                'data': self.get_serializer(updated_patient).data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'message': 'Validation failed while updating patient.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a patient record",
        description="Deletes a specific patient record by ID.",
        responses={
            200: OpenApiResponse(description="Patient deleted successfully"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Patient not found")
        }
    )
    def delete(self, request, *args, **kwargs):
        patient = self.get_object()
        patient_id = patient.id
        patient.delete()
        return Response({
            'success': True,
            'message': f'Patient with ID {patient_id} has been deleted successfully.'
        }, status=status.HTTP_200_OK)
