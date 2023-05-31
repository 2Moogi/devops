from rest_framework import serializers
from todo.models import Todo

        
#투두 생성
class TodoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ('title', 'year', 'month', 'day', 'writer','done', 'color', 'time', 'description','id')

#투두 수정
class TodoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ('title', 'year', 'month', 'day','writer','done','color','description','time', 'id')
    def update(instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.year = validated_data.get("year", instance.year)
        instance.month = validated_data.get("month", instance.month)
        instance.day = validated_data.get("day", instance.day)
        instance.writer = validated_data.get("writer", instance.writer)
        
        instance.done = validated_data.get("done", instance.done)
        instance.color = validated_data.get("color", instance.color)
        instance.description = validated_data.get("description", instance.description)
        instance.time = validated_data.get("time", instance.time)
        
        instance.save()

        return instance