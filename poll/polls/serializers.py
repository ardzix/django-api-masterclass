from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Question, Choice


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

class ChoiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text']

class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    choices = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'pub_date', 'choices']

    def get_choices(self, obj):
        queryset = Choice.objects.filter(question=obj)
        serializer = ChoiceSerializer(queryset, many=True)
        return serializer.data

class QuestionPostSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    choice_id = serializers.IntegerField()

    def validate(self, data, *args, **kwargs):
        cleaned_data = super().validate(data, *args, **kwargs)

        question_id = cleaned_data.get('question_id')
        is_question_exist = Question.objects.filter(id=question_id).exists()
        if not is_question_exist:
            raise serializers.ValidationError({'question_id':'Id pertanyaan yang anda masukkan tidak ada di database'})

        choice_id = cleaned_data.get('choice_id')
        is_choice_exist = Choice.objects.filter(id=choice_id).exists()
        if not is_choice_exist:
            raise serializers.ValidationError({'choice_id':'Id jawaban yang anda masukkan tidak ada di database'})

        choice = Choice.objects.filter(id=choice_id, question_id=question_id).first()

        if not choice:
            raise serializers.ValidationError({'choice_id':'Id jawaban yang anda masukkan tidak ada di dalam pertanyaan'})

        choice.votes = choice.votes + 1
        choice.save()

        return cleaned_data