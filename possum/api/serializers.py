from rest_framework import serializers

class UpdateTileStatusSerializer(serializers.Serializer):
    band_number = serializers.IntegerField(
        default=1,
        help_text="Band number (1 or 2)"
    )
    field_name = serializers.CharField()
    tile_numbers = serializers.ListField(
        child=serializers.CharField(allow_null=True),
        help_text="List of 4 tile numbers (e.g. [11315, 11316, 11318, 11401]. If tile is empty then use null e.g. [11315, 11316,null,null]"
    )
    status = serializers.CharField(
        help_text="Status to set for the tiles, e.g. 'Completed'"
    )

class UpdateTileTimestampSerializer(serializers.Serializer):
    band_number = serializers.IntegerField(
        default=1,
        help_text="Band number (1 or 2)"
    )
    tile_number = serializers.IntegerField(
        help_text="Tile number e.g. 11315"
    )
    timestamp = serializers.DateTimeField(
        allow_null=True,
        help_text="A timestamp when the job has completed e.g. '2026-07-02 05:55:07.574618' or null to set to current time."
    )    
