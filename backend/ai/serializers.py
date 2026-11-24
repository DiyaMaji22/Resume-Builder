from rest_framework import serializers


class ExistingExperienceSerializer(serializers.Serializer):
    position = serializers.CharField(max_length=200, allow_blank=True)
    company = serializers.CharField(max_length=200, allow_blank=True)
    description = serializers.CharField(max_length=2000, allow_blank=True)


class SuggestContextSerializer(serializers.Serializer):
    currentText = serializers.CharField(max_length=2000, required=False, allow_blank=True)
    position = serializers.CharField(max_length=200, required=False, allow_blank=True)
    company = serializers.CharField(max_length=200, required=False, allow_blank=True)
    existingExperience = ExistingExperienceSerializer(many=True, required=False, max_length=10)
    skills = serializers.ListField(child=serializers.CharField(max_length=50), required=False, max_length=50)


class SuggestRequestSerializer(serializers.Serializer):
    field = serializers.ChoiceField(choices=["summary", "experience_description"])
    context = SuggestContextSerializer()
