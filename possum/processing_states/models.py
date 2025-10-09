from django.db import models


VALIDATED_STATE = (
        ('Good', 'Good'),
        ('Bad', 'Bad'),
        ('Running', 'Running'),
        ('Failed', 'Failed'),
        ('WaitingForValidation', 'WaitingForValidation'))

PIPELINE_STATE = (
        ('Completed', 'Completed'),
        ('Running', 'Running'),
        ('Failed', 'Failed'),
        ('WaitingForValidation', 'WaitingForValidation'),)

PARTIAL_TILES_TYPE = (
        ('center', 'center'),
        ('edge', 'edge'),
        ('corner', 'corner'),
        ('edge - crosses projection boundary!', 'edge - crosses projection boundary!'),
        ('corner - crosses projection boundary!', 'corner - crosses projection boundary!'),)

class PartialTilePipelineRegionsBand1(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id')
    observation = models.ForeignKey('survey.Observation', models.DO_NOTHING, db_column='observation')
    sbid = models.BigIntegerField(db_column='sbid')
    tile1 = models.ForeignKey('survey.Tile', models.DO_NOTHING, db_column='tile1', to_field='tile', related_name='band1_tile1')
    tile2 = models.ForeignKey('survey.Tile', models.DO_NOTHING, blank=True, null=True, db_column='tile2', to_field='tile', related_name='band1_tile2')
    tile3 = models.ForeignKey('survey.Tile', models.DO_NOTHING, blank=True, null=True, db_column='tile3', to_field='tile', related_name='band1_tile3')
    tile4 = models.ForeignKey('survey.Tile', models.DO_NOTHING, blank=True, null=True, db_column='tile4', to_field='tile', related_name='band1_tile4')
    type = models.CharField(choices=PARTIAL_TILES_TYPE, db_column='type')
    number_sources = models.PositiveIntegerField(blank=True, null=True, db_column='number_sources')
    _1d_pipeline = models.CharField(choices=PIPELINE_STATE, db_column='1d_pipeline', blank=True, null=True)

    class Meta:
        verbose_name = "Partial Tile 1D Pipeline - Band 1"
        managed = False
        db_table = 'partial_tile_1d_pipeline_band1'
        unique_together = (('observation', 'sbid', 'tile1', 'tile2', 'tile3', 'tile4', 'type'),)

class PartialTilePipelineRegionsBand2(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id')
    observation = models.ForeignKey('survey.Observation', models.DO_NOTHING, db_column='observation', to_field='name')
    sbid = models.BigIntegerField(db_column='sbid')
    tile1 = models.ForeignKey('survey.Tile', models.DO_NOTHING, db_column='tile1', related_name='band2_tile1')
    tile2 = models.ForeignKey('survey.Tile', models.DO_NOTHING, blank=True, null=True, db_column='tile2', related_name='band2_tile2')
    tile3 = models.ForeignKey('survey.Tile', models.DO_NOTHING, blank=True, null=True, db_column='tile3', related_name='band2_tile3')
    tile4 = models.ForeignKey('survey.Tile', models.DO_NOTHING, blank=True, null=True, db_column='tile4', related_name='band2_tile4')
    type = models.CharField(choices=PARTIAL_TILES_TYPE, db_column='type')
    number_sources = models.PositiveIntegerField(blank=True, null=True, db_column='number_sources')
    _1d_pipeline = models.CharField(choices=PIPELINE_STATE, db_column='1d_pipeline', blank=True, null=True)

    class Meta:
        verbose_name = "Partial Tile 1D Pipeline - Band 2"
        managed = False
        db_table = 'partial_tile_1d_pipeline_band2'
        unique_together = (('observation', 'sbid', 'tile1', 'tile2', 'tile3', 'tile4', 'type'),)

class ObservationStatesBand1(models.Model):
    name = models.OneToOneField('survey.Observation', models.DO_NOTHING, db_column='name', to_field='name', primary_key=True)
    sbid = models.ForeignKey('survey.Observation', to_field="sbid", db_column='sbid', on_delete=models.DO_NOTHING, related_name='band1_states')
    _1d_pipeline_validation = models.CharField(blank=True, null=True, db_column='1d_pipeline_validation')
    single_SB_1D_pipeline = models.CharField(blank=True, null=True, db_column='single_sb_1d_pipeline')
    comments = models.TextField(blank=True, null=True, db_column='comments')
    mfs_update = models.DateTimeField(blank=True, null=True)
    mfs_state = models.TextField(blank=True, null=True)
    cube_update = models.DateTimeField(blank=True, null=True)
    cube_state = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Observation States - Band 1"
        managed = False
        db_table = 'observation_state_band1'

class ObservationStatesBand2(models.Model):
    name = models.OneToOneField('survey.Observation', models.DO_NOTHING, db_column='name', to_field='name', primary_key=True)
    sbid = models.ForeignKey('survey.Observation', to_field="sbid", db_column='sbid', on_delete=models.DO_NOTHING, related_name='band2_states')
    _1d_pipeline_validation = models.CharField(blank=True, null=True, db_column='1d_pipeline_validation')
    single_SB_1D_pipeline = models.CharField(blank=True, null=True, db_column='single_sb_1d_pipeline')
    comments = models.TextField(blank=True, null=True, db_column='comments')
    mfs_update = models.DateTimeField(blank=True, null=True)
    mfs_state = models.TextField(blank=True, null=True)
    cube_update = models.DateTimeField(blank=True, null=True)
    cube_state = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Observation States - Band 2"
        managed = False
        db_table = 'observation_state_band2'

class TileStatesBand1(models.Model):
    tile_id = models.OneToOneField('survey.Tile', models.DO_NOTHING, db_column='tile_id', to_field='tile', primary_key=True)
    _3d_pipeline = models.DateTimeField(blank=True, null=True, db_column='3d_pipeline')
    _3d_pipeline_val = models.CharField( blank=True, null=True, choices=VALIDATED_STATE, db_column='3d_pipeline_val')
    _3d_pipeline_ingest = models.CharField(blank=True, null=True, db_column='3d_pipeline_ingest')
    _3d_pipeline_validator = models.CharField(blank=True, null=True, db_column='3d_pipeline_validator')
    _3d_val_link = models.CharField(blank=True, null=True, db_column='3d_val_link')
    _3d_val_comments = models.TextField(blank=True, null=True, db_column='3d_val_comments')
    cube_state = models.TextField(blank=True, null=True)
    mfs_state = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = "Tile States - Band 1"
        managed = False
        db_table = 'tile_state_band1'

class TileStatesBand2(models.Model):
    tile_id = models.OneToOneField('survey.Tile', models.DO_NOTHING, db_column='tile_id', to_field='tile', primary_key=True)
    _3d_pipeline = models.CharField(blank=True, null=True, db_column='3d_pipeline')
    _3d_pipeline_val = models.CharField( blank=True, null=True, choices=VALIDATED_STATE, db_column='3d_pipeline_val')
    _3d_pipeline_ingest = models.CharField(blank=True, null=True, db_column='3d_pipeline_ingest')
    _3d_pipeline_validator = models.CharField(blank=True, null=True, db_column='3d_pipeline_validator')
    _3d_val_link = models.CharField(blank=True, null=True, db_column='3d_val_link')
    _3d_val_comments = models.TextField(blank=True, null=True, db_column='3d_val_comments')
    cube_state = models.TextField(blank=True, null=True)
    mfs_state = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = "Tile States - Band 2"
        managed = False
        db_table = 'tile_state_band2'
