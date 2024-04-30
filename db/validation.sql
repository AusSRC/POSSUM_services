\c possum

CREATE TABLE possum.validation (
    id bigint primary key,
    field_id varchar,
    project_code varchar,
    link text,
    observation_start_time timestamp without time zone,
    observation_end_time timestamp without time zone,
    holography_model_file text,
    holography_observation_date timestamp without time zone,
    rms float,
    freq_channel_0 float,  -- MHz
    chan_width float, -- MHz
    solar_flux float,  -- sfu
    solar_flux_uncertainty float, -- sfu
    solar_distance float,  -- deg
    solar_pa float, -- deg
    solar_ra varchar, -- hms
    solar_dec float, -- deg
    number_of_components_all int,
    avg_flux_i float, -- mJy/beam
    stddev_i float, -- mJy/beam
    avg_flux_v float, -- mJy/beam
    stddev_v float, -- mJy/beam
    number_of_components_i int,
    number_of_components_v int,
    avg_pol_frac float,
    med_pol_frac float,
    avg_fd float,
    med_fd float,
    stddev_fd float,
    number_of_components_10_1e5 int,
    avg_flux_i_10_1e5 float,  -- mJy/beam
    stddev_flux_i_10_1e5 float,  --mJy/beam
    avg_flux_v_10_1e5 float,  -- mJy/beam
    stddev_flux_v_10_1e5 float,  --mJy/beam
    number_of_components_i_10_1e5 int,
    number_of_components_bax_max_pi_10_1e5 int,
    avg_pol_frac_10_1e5 float,
    med_pol_frac_10_1e5 float,
    avg_fd_10_1e5 float,
    med_fd_10_1e5 float,
    stddev_fd_10_1e5 float,
    oppermann_map_fd float,
    oppermann_map_fd_uncertainty float,
    possum_status varchar
);
ALTER TABLE possum.validation ADD FOREIGN KEY ("field_id") REFERENCES possum.observation ("name");

