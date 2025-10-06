from django.utils import timezone
from django.forms.models import model_to_dict
from django.contrib.auth.models import User

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from .models import Movie, Show, Booking
from .serializers import AuthErrorSerializer, BookSeatRequestSerializer, GenericError, RegisterSerializer, MovieSerializer, ShowSerializer, BookingSerializer


# -------------------------------
# User Registration
# -------------------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        token_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token) 
        }

        return Response(
            {**serializer.data, **token_data},
            status=status.HTTP_201_CREATED
        )


# -------------------------------
# Movies Endpoints
# -------------------------------
@extend_schema(
    methods=['GET'],
    responses={
        200: OpenApiResponse(
            response=MovieSerializer,
            description="Fetch all movies",
            examples=[
                OpenApiExample(
                    name="Sample Movie",
                    value=[
                        {
                            "id": 1,
                            "title": "Godfather",
                            "duration_minutes": 121
                        }
                    ],
                    response_only=True
                )
            ]
        )
    }
)
@extend_schema(
    methods=['POST'],
    request=MovieSerializer,
    responses={
        201: MovieSerializer,
        400: OpenApiResponse(description="Invalid input data")
    }
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def movies_list(request):
    """
    List all movies, or create a new movie
    """
    if request.method == 'GET':
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)
    
    serializer = MovieSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------
# Shows Endpoints
# -------------------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def shows_list(request, movie_id):
    """
    List all shows for a movie, or create a new show
    """
    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return Response({"message": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        shows = Show.objects.filter(movie_id=movie_id)
        serializer = ShowSerializer(shows, many=True)
        return Response(serializer.data)
    
    serializer = ShowSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(movie_id=movie_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['POST'],
    description="Book a ticket for a show. If the seat was previously cancelled, it will be re-booked.",
    request=BookSeatRequestSerializer,
    responses={
        201: OpenApiResponse(
            response=BookingSerializer,
            description="Booking created successfully",
            examples=[
                OpenApiExample(
                    name="New Booking",
                    value={
                        "id": 7,
                        "user": "tabsheer",
                        "show": {
                            "id": 1,
                            "movie": {
                                "id": 1,
                                "title": "Godfather",
                                "duration_minutes": 121
                            },
                            "screen_name": "PVR Cinemas",
                            "date_time": "2025-10-05T14:30:00Z",
                            "total_seats": 300
                        },
                        "seat_number": 3,
                        "status": "booked",
                        "created_at": "2025-10-06T12:10:00.123456Z"
                    },
                    response_only=True
                )
            ]
        ),
        200: OpenApiResponse(
            response=BookingSerializer,
            description="Existing cancelled booking re-booked",
            examples=[
                OpenApiExample(
                    name="Rebook Cancelled Seat",
                    value={
                        "id": 6,
                        "user": "tabsheer",
                        "show": {
                            "id": 1,
                            "movie": {
                                "id": 1,
                                "title": "Godfather",
                                "duration_minutes": 121
                            },
                            "screen_name": "PVR Cinemas",
                            "date_time": "2025-10-05T14:30:00Z",
                            "total_seats": 300
                        },
                        "seat_number": 2,
                        "status": "booked",
                        "created_at": "2025-10-06T12:15:00.654321Z"
                    },
                    response_only=True
                )
            ]
        ),
        400: OpenApiResponse(
            response=GenericError,
            description="Invalid seat number",
            examples=[
                OpenApiExample(
                    name="Bad Seat Number",
                    value={"message": "Seat number should be between 1 and 300"},
                    response_only=True
                )
            ]
        ),
        403: OpenApiResponse(
            response=GenericError,
            description="Seat already occupied",
            examples=[
                OpenApiExample(
                    name="Forbidden",
                    value={"message": "Seat is already occupied"},
                    response_only=True
                )
            ]
        ),
        404: OpenApiResponse(
            response=GenericError,
            description="Show not found",
            examples=[
                OpenApiExample(
                    name="Not Found",
                    value={"message": "Show not found"},
                    response_only=True
                )
            ]
        ),
        401: OpenApiResponse(
            response=AuthErrorSerializer,
            description="Authentication error",
            examples=[
                OpenApiExample(
                    name="Unauthorized - Missing Token",
                    value={"detail": "Authentication credentials were not provided."},
                    response_only=True
                ),
                OpenApiExample(
                    name="Unauthorized - Invalid Token",
                    value={
                        "detail": "Given token not valid for any token type",
                        "code": "token_not_valid",
                        "messages": [
                            {
                                "token_class": "AccessToken",
                                "token_type": "access",
                                "message": "Token is invalid"
                            }
                        ]
                    },
                    response_only=True
                )
            ]
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_seat(request, show_id):
    """
    Book a ticket on an available show
    """
    try:
        show = Show.objects.get(id=show_id)
    except Show.DoesNotExist:
        return Response({"message": "Show not found"}, status=status.HTTP_404_NOT_FOUND)

    seat_number = request.data.get('seat_number')

    if seat_number > show.total_seats or seat_number < 1:
        return Response(
            {"message": f"Seat number should be between 1 and {show.total_seats}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        booking = Booking.objects.get(show_id=show_id, seat_number=seat_number)
    except Booking.DoesNotExist:
        booking = None


    if booking and str(booking.status) == "booked":
        return Response({"message": "Seat is already occupied"}, status=status.HTTP_403_FORBIDDEN)

    # Existing cancelled booking
    if booking and str(booking.status) == "cancelled":
        updated = booking
        updated.status = "booked"
        updated.created_at = timezone.now()
        updated.user = request.user

        updated_data = model_to_dict(updated)
        serializer = BookingSerializer(booking, data=updated_data, partial=True)

        user_id = booking.user.id
        
        if serializer.is_valid():
            serializer.save(show_id=show_id, user_id=user_id)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # New booking    
    data = request.data.copy()
    data['status'] = 'booked'
    data['created_at'] = timezone.now()
    serializer = BookingSerializer(data=data)

    user_id = request.user.id

    if serializer.is_valid():
        serializer.save(show_id=show_id, user_id=user_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -------------------------------
# Bookings Endpoints
# -------------------------------
@extend_schema(
    methods=['POST'],
    description="Cancel a booking. Only the user who booked can cancel.",
    responses={
        200: OpenApiResponse(
            response=BookingSerializer,
            description="Booking cancelled successfully",
            examples=[
                OpenApiExample(
                    name="Cancelled Booking",
                    value={
                        "id": 6,
                        "user": "tabsheer",
                        "show": {
                            "id": 1,
                            "movie": {
                                "id": 1,
                                "title": "Godfather",
                                "duration_minutes": 121
                            },
                            "screen_name": "PVR Cinemas",
                            "date_time": "2025-10-05T14:30:00Z",
                            "total_seats": 300
                        },
                        "seat_number": 2,
                        "status": "cancelled",
                        "created_at": "2025-10-06T11:58:56.347252Z"
                    },
                    response_only=True
                )
            ]
        ),
        403: OpenApiResponse(
            response=GenericError,
            description="You are not authorized to perform this action",
            examples=[
                OpenApiExample(
                    name="Forbidden",
                    value={"message": "You are not authorized to perform this action"},
                    response_only=True
                )
            ]
        ),
        404: OpenApiResponse(
            response=GenericError,
            description="Booking not found",
            examples=[
                OpenApiExample(
                    name="Booking Not Found",
                    value={"message": "You can't cancel seat which is not been booked"},
                    response_only=True
                )
            ]
        ),
        401: OpenApiResponse(
            response=AuthErrorSerializer,
            description="Authentication error",
            examples=[
                OpenApiExample(
                    name="Unauthorized - Missing Token",
                    value={"detail": "Authentication credentials were not provided."},
                    response_only=True
                ),
                OpenApiExample(
                    name="Unauthorized - Invalid Token",
                    value={
                        "detail": "Given token not valid for any token type",
                        "code": "token_not_valid",
                        "messages": [
                            {
                                "token_class": "AccessToken",
                                "token_type": "access",
                                "message": "Token is invalid"
                            }
                        ]
                    },
                    response_only=True
                )
            ]
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):
    """
    Cancel a booking
    """
    booking_exists = Booking.objects.filter(id=booking_id).exists()
    if not booking_exists:
        return Response(
            {"message": "You can't cancel seat which is not been booked"},
            status=status.HTTP_404_NOT_FOUND
        )

    booking = Booking.objects.get(id=booking_id)
    
    if str(request.user) != str(booking.user):
        return Response(
            {"message": "You are not authorized to perform this action"},
            status=status.HTTP_403_FORBIDDEN
        )

    updated = booking
    updated.status = "cancelled"
    updated_data = model_to_dict(updated)
    
    serializer = BookingSerializer(booking, data=updated_data, partial=True)

    user_id = request.user.id
    show_id = booking.show.id

    if serializer.is_valid():
        serializer.save(show_id=show_id, user_id=user_id)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    responses={
        200: OpenApiResponse(
            response=BookingSerializer,
            description="Fetch all bookings of the logged-in user",
            examples=[
                OpenApiExample(
                    name="Sample Bookings Response",
                    value=[
                        {
                            "id": 6,
                            "user": "tabsheer",
                            "show": {
                                "id": 1,
                                "movie": {
                                    "id": 1,
                                    "title": "Godfather",
                                    "duration_minutes": 121
                                },
                                "screen_name": "PVR Cinemas",
                                "date_time": "2025-10-05T14:30:00Z",
                                "total_seats": 300
                            },
                            "seat_number": 2,
                            "status": "cancelled",
                            "created_at": "2025-10-06T11:58:56.347252Z"
                        }
                    ],
                    response_only=True
                )
            ]
        ),
        401: OpenApiResponse(
            response=AuthErrorSerializer, 
            description="Authentication failed",
            examples=[
                OpenApiExample(
                    name="No Credentials",
                    value={"detail": "Authentication credentials were not provided."},
                    response_only=True
                ),
                OpenApiExample(
                    name="Invalid Token",
                    value={
                        "detail": "Given token not valid for any token type",
                        "code": "token_not_valid",
                        "messages": [
                            {
                                "token_class": "AccessToken",
                                "token_type": "access",
                                "message": "Token is invalid"
                            }
                        ]
                    },
                    response_only=True
                )
            ]
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bookings(request):
    """
    Get all bookings of the currently logged in user
    """
    user_id = request.user.id

    bookings = Booking.objects.filter(user_id=user_id)
    serializer = BookingSerializer(bookings, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

