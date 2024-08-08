from rest_framework.serializers import ModelSerializer

from goods.models import Sneakers


class SneakersSerializer(ModelSerializer):
    class Meta:
        model = Sneakers
        fields = '__all__'