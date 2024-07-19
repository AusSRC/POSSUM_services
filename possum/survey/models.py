from django.db import models


VALIDATED_STATE = (
        ('ACCEPTED', 'ACCEPTED'),
        ('REJECTED', 'REJECTED'),)

PIPELINE_STATE = (
        ('COMPLETED', 'COMPLETED'),
        ('SUBMITTED', 'SUBMITTED'),
        ('QUEUED', 'QUEUED'),
        ('RUNNING', 'RUNNING'),
        ('FAILED', 'FAILED'),
        ('CANCELLED', 'CANCELLED'),)


class AssociatedTile(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.ForeignKey('Observation', models.DO_NOTHING, db_column='name', to_field='name', blank=True, null=True)
    tile = models.ForeignKey('Tile', models.DO_NOTHING, db_column='tile', to_field='tile', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'associated_tile'
        unique_together = (('name', 'tile'),)


class FieldTile(models.Model):
    id = models.BigAutoField(primary_key=True)
    tile = models.ForeignKey('Tile', models.DO_NOTHING, db_column='tile', to_field='tile', blank=True, null=True)
    name = models.ForeignKey('Observation', models.DO_NOTHING, db_column='name', to_field='name', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'field_tile'
        unique_together = (('name', 'tile'),)


class Observation(models.Model):
    name = models.TextField(primary_key=True)
    ra_deg = models.DecimalField(max_digits=65535, decimal_places=4, blank=True, null=True)
    dec_deg = models.DecimalField(max_digits=65535, decimal_places=4, blank=True, null=True)
    gl = models.DecimalField(max_digits=65535, decimal_places=4, blank=True, null=True)
    gb = models.DecimalField(max_digits=65535, decimal_places=4, blank=True, null=True)
    rotation = models.FloatField(blank=True, null=True)
    duration = models.BigIntegerField(blank=True, null=True)
    centrefreq = models.BigIntegerField(blank=True, null=True)
    bandwidth = models.BigIntegerField(blank=True, null=True)
    footprint = models.TextField(blank=True, null=True)
    band = models.SmallIntegerField(blank=True, null=True)
    obs_start = models.DateTimeField(blank=True, null=True)
    sbid = models.BigIntegerField(blank=True, null=True)
    processed_date = models.DateTimeField(blank=True, null=True)
    validated_date = models.DateTimeField(blank=True, null=True)
    validated_state = models.TextField(blank=True, null=True)
    mfs_update = models.DateTimeField(blank=True, null=True)
    mfs_state = models.TextField(blank=True, null=True)
    cube_update = models.DateTimeField(blank=True, null=True)
    cube_state = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'observation'


class Tile(models.Model):
    tile = models.BigIntegerField(primary_key=True)
    ra_deg = models.DecimalField(max_digits=65535, decimal_places=4, blank=True, null=True)
    dec_deg = models.DecimalField(max_digits=65535, decimal_places=4, blank=True, null=True)
    gl = models.DecimalField(max_digits=65535, decimal_places=4, blank=True, null=True)
    gb = models.DecimalField(max_digits=65535, decimal_places=4, blank=True, null=True)
    oned_pipeline_main_band1 = models.DateTimeField(db_column='1d_pipeline_main_band1', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    oned_pipeline_borders_band1 = models.DateTimeField(db_column='1d_pipeline_borders_band1', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    threed_pipeline_band1 = models.DateTimeField(db_column='3d_pipeline_band1', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    oned_pipeline_main_band2 = models.DateTimeField(db_column='1d_pipeline_main_band2', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    oned_pipeline_borders_band2 = models.DateTimeField(db_column='1d_pipeline_borders_band2', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    threed_pipeline_band2 = models.DateTimeField(db_column='3d_pipeline_band2', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    band1_cube_state = models.TextField(blank=True, null=True)
    band1_mfs_state = models.TextField(blank=True, null=True)
    band2_mfs_state = models.TextField(blank=True, null=True)
    band2_cube_state = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.tile)

    class Meta:
        managed = False
        db_table = 'tile'


class Validation(models.Model):
    id = models.BigAutoField(primary_key=True)
    field_id = models.ForeignKey('Observation', db_column='field_id', on_delete=models.DO_NOTHING, to_field='name', blank=True, null=True)
    project_code = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    observation_start_time = models.DateTimeField(blank=True, null=True)
    observation_end_time  = models.DateTimeField(blank=True, null=True)
    holography_model_file = models.TextField(blank=True, null=True)
    holography_observation_date  = models.DateTimeField(blank=True, null=True)
    rms = models.FloatField(blank=True, null=True)
    freq_channel_0 = models.FloatField(blank=True, null=True)
    chan_width = models.FloatField(blank=True, null=True)
    solar_flux = models.FloatField(blank=True, null=True)
    solar_flux_uncertainty = models.FloatField(blank=True, null=True)
    solar_distance = models.FloatField(blank=True, null=True)
    solar_pa = models.FloatField(blank=True, null=True)
    solar_ra = models.TextField(blank=True, null=True)
    solar_dec = models.FloatField(blank=True, null=True)
    number_of_components_all = models.IntegerField(blank=True, null=True)
    avg_flux_i = models.FloatField(blank=True, null=True)
    stddev_i = models.FloatField(blank=True, null=True)
    avg_flux_v = models.FloatField(blank=True, null=True)
    stddev_v = models.FloatField(blank=True, null=True)
    number_of_components_i = models.IntegerField(blank=True, null=True)
    number_of_components_v = models.IntegerField(blank=True, null=True)
    avg_pol_frac = models.FloatField(blank=True, null=True)
    med_pol_frac = models.FloatField(blank=True, null=True)
    avg_fd = models.FloatField(blank=True, null=True)
    med_fd = models.FloatField(blank=True, null=True)
    stddev_fd = models.FloatField(blank=True, null=True)
    number_of_components_10_1e5 = models.IntegerField(blank=True, null=True)
    avg_flux_i_10_1e5 = models.FloatField(blank=True, null=True)
    stddev_flux_i_10_1e5 = models.FloatField(blank=True, null=True)
    avg_flux_v_10_1e5 = models.FloatField(blank=True, null=True)
    stddev_flux_v_10_1e5 = models.FloatField(blank=True, null=True)
    number_of_components_i_10_1e5 = models.IntegerField(blank=True, null=True)
    number_of_components_bax_max_pi_10_1e5 = models.IntegerField(blank=True, null=True)
    avg_pol_frac_10_1e5 = models.FloatField(blank=True, null=True)
    med_pol_frac_10_1e5 = models.FloatField(blank=True, null=True)
    avg_fd_10_1e5 = models.FloatField(blank=True, null=True)
    med_fd_10_1e5 = models.FloatField(blank=True, null=True)
    stddev_fd_10_1e5 = models.FloatField(blank=True, null=True)
    oppermann_map_fd = models.FloatField(blank=True, null=True)
    oppermann_map_fd_uncertainty = models.FloatField(blank=True, null=True)
    possum_status = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.field_id)

    class Meta:
        managed = False
        db_table = 'validation'
