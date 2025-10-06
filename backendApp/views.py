from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from backendApp.serializers import BookingSerializer, MovieSerializer, ShowSerializer
from .models import Movie, Show, Booking
from .serializers import RegisterSerializer
from django.forms.models import model_to_dict

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
    elif request.method == 'POST':
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def shows_list(request, movie_id):
    """
    List all shows for a movie, or create a new show
    """
    movie = Movie.objects.filter(id=movie_id)
    if not movie:
        return Response({"message": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        shows = Show.objects.filter(movie_id=movie_id)
        serializer = ShowSerializer(shows, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ShowSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(movie_id=movie_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_seat(request, show_id):
    """
    Book a ticket on an available show
    """
    show = Show.objects.filter(id=show_id)
    if not show:
        return Response({"message": "Show not found"}, status=status.HTTP_404_NOT_FOUND)

    seat_number = request.data.get('seat_number')

    booking = Booking.objects.filter(show_id=show_id, seat_number=seat_number, status='booked').exists()

    if booking:
        return Response({"message": "Seat is already occupied"}, status=status.HTTP_403_FORBIDDEN)

    data = request.data.copy()
    data['status'] = 'booked'
    data['created_at'] = timezone.now()
    serializer = BookingSerializer(data=data)
    if serializer.is_valid():
        serializer.save(show_id=show_id, user_id=2)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):
    """
    Cancel a booking
    """
    booking_exists = Booking.objects.filter(id=booking_id).exists()
    if not booking_exists:
        return Response({"message": "You can't cancel seat which is not been booked"}, status=status.HTTP_404_NOT_FOUND)

    booking = Booking.objects.get(id=booking_id)
       
    print(str(request.user), booking.user)
    
    if str(request.user) != str(booking.user):
        return Response({"message": "You are not authorized to perform this action"}, status=status.HTTP_403_FORBIDDEN)

    updated = booking
    updated.status = "cancelled"
    updated_data = model_to_dict(updated)
    
    serializer = BookingSerializer(booking, data=updated_data, partial=True)

    user = User.objects.get(username=booking.user)
    user_id = user.id
    show_id = booking.show.id

    if serializer.is_valid():
        serializer.save(show_id=show_id, user_id=user_id)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bookings(request):
    """
    Get all bookings of the currently logged in user
    """
    username = str(request.user)

    user = User.objects.get(username=username)
    user_id = user.id

    bookings = Booking.objects.filter(user_id=user_id)
    serializer = BookingSerializer(bookings, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


    

    

    
    

    
    

