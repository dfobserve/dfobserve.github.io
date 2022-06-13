from astropy.time import Time
from dfobserve.observing import (
    Observation,
    get_moonset,
    get_sunset,
    get_moonrise,
    get_morning_twilight,
    get_moonrise,
)
from dfobserve.webserver import SendWebRequestNB
from dfobserve.utils.CameraUtils import AllScienceExposure
from dfobserve.utils.FilterTilterUtils import AllTiltScienceFilters
from dfobserve.exceptions import *
import pandas as pd
import pytest


def test_get_sunset():
    DATE = "2022-04-21"
    ans = get_sunset(date=DATE).value.split(" ")[1]
    expected = "19:33:02.968"
    assert ans == expected


def test_get_moonset():
    DATE = "2022-04-21"
    ans = get_moonset(date=DATE).value.split(" ")[1]
    expected = "10:14:39.160"
    assert ans == expected


def test_get_moonrise():
    DATE = "2022-04-21"
    ans = get_moonrise(date=DATE).value.split(" ")[1]
    expected = "02:40:08.619"
    assert ans == expected


def test_get_morning_twilight():
    DATE = "2022-04-21"
    ans = get_morning_twilight(date=DATE).value.split(" ")[1]
    expected = "04:55:46.495"
    assert ans == expected


def test_get_morning_twilight_utc():
    DATE = "2022-04-21"
    ans = get_morning_twilight(date=DATE, return_local=False).value.split(" ")[1]
    expected = "10:55:46.495"
    assert ans == expected


def test_get_moonrise():
    DATE = "2022-04-21"
    ans = get_moonrise(date=DATE).value.split(" ")[1]
    expected = "02:40:08.619"
    assert ans == expected


def test_bad_sunset():
    DATE = "2022-04-21"
    obs = Observation(target="NGC 5813")
    with pytest.raises(TargetNotUpError):
        obs.configure_observation(wait_until="sunset")
        obs.construct_observing_plan(date=DATE)


def test_late_risetime():
    DATE = "2022-04-21"
    obs = Observation(target="NGC 7626")
    with pytest.raises(EndOfNightError):
        obs.configure_observation(wait_until="target_rise")
        obs.construct_observing_plan(date=DATE)


def test_bad_moonset():
    DATE = "2022-04-21"
    obs = Observation(target="NGC 7626")
    with pytest.raises(EndOfNightError):
        obs.configure_observation(wait_until="moonset")
        obs.construct_observing_plan(date=DATE)


def test_tilt_set():
    obs = Observation(target="NGC 7626")
    with pytest.raises(ValueError):
        obs.set_tilts("ha", 30)
    with pytest.raises(FilterNotRecognizedError):
        obs.set_tilts("OVII", 15)


def test_long_obsplan():
    obs = Observation(target="GD 71")
    with pytest.raises(TargetUptimeError):
        obs.configure_observation("target_rise")
        obs.configure_calibrations(n_darks=2, n_flats=2)
        obs.configure_standards(n_standards=1)
        obs.construct_observing_plan(date="2022-04-11")


def test_bad_custom_time():
    DATE = "2022-04-21"
    obs = Observation(target="NGC 5813")
    with pytest.raises(DayTimeError):
        obs.configure_observation(wait_until="15:00:00")
        obs.construct_observing_plan(date=DATE)
    with pytest.raises(DayTimeError):
        obs.configure_observation(wait_until="10:00:00")
        obs.construct_observing_plan(date=DATE)


def test_good_custom_time_post_midnight():
    DATE = "2022-04-21"
    obs = Observation(target="NGC 5813")
    obs.configure_observation(wait_until="01:00:00")
    obs.construct_observing_plan(date=DATE)
    expected_start = Time("2022-04-22 01:00:00")
    assert obs.OBS_START == expected_start


def test_good_custom_time_pre_midnight():
    DATE = "2022-04-21"
    obs = Observation(target="NGC 5813")
    obs.configure_observation(wait_until="22:00:00")
    obs.construct_observing_plan(date=DATE)
    expected_start = Time("2022-04-21 22:00:00")
    assert obs.OBS_START == expected_start


def test_observation_calc_target_rise():
    DATE = "2022-04-21"
    obs = Observation(target="NGC 5813")
    r = obs.calc_target_rise(date=DATE).value.split(" ")[1]
    expected = "22:52:10.062"
    assert r == expected


def test_webrequest_nb_all():
    df = SendWebRequestNB(
        "status",
        which="all",
        dryrun=True,
        hardware_config_file="test_hardware_template.txt",
    )
    expected = pd.DataFrame(columns=["Name", "ip", "command"])
    expected["Name"] = [
        "Dragonfly301",
        "Dragonfly302",
        "Dragonfly303",
        "Dragonfly304",
        "Dragonfly305",
        "Dragonfly306",
        "Dragonfly307",
        "Dragonfly308",
        "Dragonfly309",
        "Dragonfly310",
    ]
    expected["ip"] = [
        "192.168.50.11",
        "192.168.50.12",
        "192.168.50.13",
        "192.168.50.14",
        "192.168.50.15",
        "192.168.50.16",
        "192.168.50.17",
        "192.168.50.18",
        "192.168.50.19",
        "192.168.50.20",
    ]
    expected["command"] = ["status"] * 10

    pd.testing.assert_frame_equal(df, expected)


def test_webrequest_nb_ha():
    df = SendWebRequestNB(
        "status",
        which="halpha",
        dryrun=True,
        hardware_config_file="test_hardware_template.txt",
    )
    expected = pd.DataFrame(columns=["Name", "ip", "command"])
    expected["ip"] = ["192.168.50.11", "192.168.50.12", "192.168.50.13"]
    expected["Name"] = ["Dragonfly301", "Dragonfly302", "Dragonfly303"]
    expected["command"] = ["status"] * 3

    pd.testing.assert_frame_equal(df, expected)


def test_webrequest_nb_oiii():
    df = SendWebRequestNB(
        "status",
        which="oiii",
        dryrun=True,
        hardware_config_file="test_hardware_template.txt",
    )
    expected = pd.DataFrame(columns=["Name", "ip", "command"])
    expected["Name"] = ["Dragonfly310"]
    expected["ip"] = ["192.168.50.20"]
    expected["command"] = ["status"]

    pd.testing.assert_frame_equal(df, expected)


def test_webrequest_nb_science():
    df = SendWebRequestNB(
        "status",
        which="science",
        dryrun=True,
        hardware_config_file="test_hardware_template.txt",
    )
    expected = pd.DataFrame(columns=["Name", "ip", "command"])
    expected["Name"] = ["Dragonfly301", "Dragonfly302", "Dragonfly303", "Dragonfly310"]
    expected["ip"] = [
        "192.168.50.11",
        "192.168.50.12",
        "192.168.50.13",
        "192.168.50.20",
    ]
    expected["command"] = ["status"] * 4

    pd.testing.assert_frame_equal(df, expected)


def test_webrequest_nb_science_offs():
    df = SendWebRequestNB(
        "status",
        which="science offs",
        dryrun=True,
        hardware_config_file="test_hardware_template.txt",
    )
    expected = pd.DataFrame(columns=["Name", "ip", "command"])
    expected["Name"] = ["Dragonfly304", "Dragonfly305", "Dragonfly306", "Dragonfly307"]
    expected["ip"] = [
        "192.168.50.14",
        "192.168.50.15",
        "192.168.50.16",
        "192.168.50.17",
    ]
    expected["command"] = ["status"] * 4

    pd.testing.assert_frame_equal(df, expected)


def test_webrequest_nb_OH():
    df = SendWebRequestNB(
        "status",
        which="OH",
        dryrun=True,
        hardware_config_file="test_hardware_template.txt",
    )
    expected = pd.DataFrame(columns=["Name", "ip", "command"])
    expected["Name"] = ["Dragonfly308", "Dragonfly309"]
    expected["ip"] = ["192.168.50.18", "192.168.50.19"]
    expected["command"] = ["status"] * 2
    pd.testing.assert_frame_equal(df, expected)


def test_webrequest_nb_ha_override():
    df = SendWebRequestNB(
        "status",
        which="all",
        ha_command="special_ha_command",
        dryrun=True,
        hardware_config_file="test_hardware_template.txt",
    )
    expected = pd.DataFrame(columns=["Name", "ip", "command"])
    expected["Name"] = [
        "Dragonfly301",
        "Dragonfly302",
        "Dragonfly303",
        "Dragonfly304",
        "Dragonfly305",
        "Dragonfly306",
        "Dragonfly307",
        "Dragonfly308",
        "Dragonfly309",
        "Dragonfly310",
    ]
    expected["ip"] = expected["ip"] = [
        "192.168.50.11",
        "192.168.50.12",
        "192.168.50.13",
        "192.168.50.14",
        "192.168.50.15",
        "192.168.50.16",
        "192.168.50.17",
        "192.168.50.18",
        "192.168.50.19",
        "192.168.50.20",
    ]
    expected["command"] = ["special_ha_command"] * 3 + ["status"] * 7
    pd.testing.assert_frame_equal(df, expected)


def test_webrequest_nb_oiii_override():
    df = SendWebRequestNB(
        "status",
        which="all",
        oiii_command="special_oiii_command",
        dryrun=True,
        hardware_config_file="test_hardware_template.txt",
    )
    expected = pd.DataFrame(columns=["Name", "ip", "command"])
    expected["Name"] = [
        "Dragonfly301",
        "Dragonfly302",
        "Dragonfly303",
        "Dragonfly304",
        "Dragonfly305",
        "Dragonfly306",
        "Dragonfly307",
        "Dragonfly308",
        "Dragonfly309",
        "Dragonfly310",
    ]
    expected["ip"] = expected["ip"] = [
        "192.168.50.11",
        "192.168.50.12",
        "192.168.50.13",
        "192.168.50.14",
        "192.168.50.15",
        "192.168.50.16",
        "192.168.50.17",
        "192.168.50.18",
        "192.168.50.19",
        "192.168.50.20",
    ]
    expected["command"] = ["status"] * 9 + ["special_oiii_command"]
    pd.testing.assert_frame_equal(df, expected)


def test_webrequest_nb_ha_off_override():
    df = SendWebRequestNB(
        "status",
        which="all",
        ha_off_command="ha_off_command",
        dryrun=True,
        hardware_config_file="test_hardware_template.txt",
    )
    expected = pd.DataFrame(columns=["Name", "ip", "command"])
    expected["Name"] = [
        "Dragonfly301",
        "Dragonfly302",
        "Dragonfly303",
        "Dragonfly304",
        "Dragonfly305",
        "Dragonfly306",
        "Dragonfly307",
        "Dragonfly308",
        "Dragonfly309",
        "Dragonfly310",
    ]
    expected["ip"] = expected["ip"] = [
        "192.168.50.11",
        "192.168.50.12",
        "192.168.50.13",
        "192.168.50.14",
        "192.168.50.15",
        "192.168.50.16",
        "192.168.50.17",
        "192.168.50.18",
        "192.168.50.19",
        "192.168.50.20",
    ]
    expected["command"] = ["status"] * 3 + ["ha_off_command"] * 2 + ["status"] * 5
    pd.testing.assert_frame_equal(df, expected)


def test_webrequest_nb_oiii_off_override():
    df = SendWebRequestNB(
        "status",
        which="all",
        oiii_off_command="oiii_off_command",
        dryrun=True,
        hardware_config_file="test_hardware_template.txt",
    )
    expected = pd.DataFrame(columns=["Name", "ip", "command"])
    expected["Name"] = [
        "Dragonfly301",
        "Dragonfly302",
        "Dragonfly303",
        "Dragonfly304",
        "Dragonfly305",
        "Dragonfly306",
        "Dragonfly307",
        "Dragonfly308",
        "Dragonfly309",
        "Dragonfly310",
    ]
    expected["ip"] = expected["ip"] = [
        "192.168.50.11",
        "192.168.50.12",
        "192.168.50.13",
        "192.168.50.14",
        "192.168.50.15",
        "192.168.50.16",
        "192.168.50.17",
        "192.168.50.18",
        "192.168.50.19",
        "192.168.50.20",
    ]
    expected["command"] = ["status"] * 5 + ["oiii_off_command"] * 2 + ["status"] * 3
    pd.testing.assert_frame_equal(df, expected)


def test_webrequest_nb_oh_override():
    df = SendWebRequestNB(
        "status",
        which="all",
        OH_command="command",
        dryrun=True,
        hardware_config_file="test_hardware_template.txt",
    )
    expected = pd.DataFrame(columns=["Name", "ip", "command"])
    expected["Name"] = [
        "Dragonfly301",
        "Dragonfly302",
        "Dragonfly303",
        "Dragonfly304",
        "Dragonfly305",
        "Dragonfly306",
        "Dragonfly307",
        "Dragonfly308",
        "Dragonfly309",
        "Dragonfly310",
    ]
    expected["ip"] = expected["ip"] = [
        "192.168.50.11",
        "192.168.50.12",
        "192.168.50.13",
        "192.168.50.14",
        "192.168.50.15",
        "192.168.50.16",
        "192.168.50.17",
        "192.168.50.18",
        "192.168.50.19",
        "192.168.50.20",
    ]
    expected["command"] = ["status"] * 8 + ["command"] * 1 + ["status"] * 1
    pd.testing.assert_frame_equal(df, expected)


def test_webrequest_nb_oh_off_override():
    df = SendWebRequestNB(
        "status",
        which="all",
        OH_off_command="command",
        dryrun=True,
        hardware_config_file="test_hardware_template.txt",
    )
    expected = pd.DataFrame(columns=["Name", "ip", "command"])
    expected["Name"] = [
        "Dragonfly301",
        "Dragonfly302",
        "Dragonfly303",
        "Dragonfly304",
        "Dragonfly305",
        "Dragonfly306",
        "Dragonfly307",
        "Dragonfly308",
        "Dragonfly309",
        "Dragonfly310",
    ]
    expected["ip"] = expected["ip"] = [
        "192.168.50.11",
        "192.168.50.12",
        "192.168.50.13",
        "192.168.50.14",
        "192.168.50.15",
        "192.168.50.16",
        "192.168.50.17",
        "192.168.50.18",
        "192.168.50.19",
        "192.168.50.20",
    ]
    expected["command"] = ["status"] * 7 + ["command"] * 1 + ["status"] * 2
    pd.testing.assert_frame_equal(df, expected)


def test_webrequest_nb_all_flathaving_command():
    df = SendWebRequestNB(
        "status",
        which="all",
        all_flathaving_command="command",
        dryrun=True,
        hardware_config_file="test_hardware_template.txt",
    )
    expected = pd.DataFrame(columns=["Name", "ip", "command"])
    expected["Name"] = [
        "Dragonfly301",
        "Dragonfly302",
        "Dragonfly303",
        "Dragonfly304",
        "Dragonfly305",
        "Dragonfly306",
        "Dragonfly307",
        "Dragonfly308",
        "Dragonfly309",
        "Dragonfly310",
    ]
    expected["ip"] = expected["ip"] = [
        "192.168.50.11",
        "192.168.50.12",
        "192.168.50.13",
        "192.168.50.14",
        "192.168.50.15",
        "192.168.50.16",
        "192.168.50.17",
        "192.168.50.18",
        "192.168.50.19",
        "192.168.50.20",
    ]
    expected["command"] = ["command"] * 3 + ["status"] * 4 + ["command"] * 3
    pd.testing.assert_frame_equal(df, expected)


def test_webrequest_nb_combo():
    df = SendWebRequestNB(
        "status",
        which="science offs",
        all_flathaving_command="flathaving",
        ha_off_command="ha_off_command",
        dryrun=True,
        hardware_config_file="test_hardware_template.txt",
    )
    expected = pd.DataFrame(columns=["Name", "ip", "command"])
    expected["Name"] = [
        "Dragonfly301",
        "Dragonfly302",
        "Dragonfly303",
        "Dragonfly304",
        "Dragonfly305",
        "Dragonfly306",
        "Dragonfly307",
        "Dragonfly308",
        "Dragonfly309",
        "Dragonfly310",
    ]
    expected["ip"] = expected["ip"] = [
        "192.168.50.11",
        "192.168.50.12",
        "192.168.50.13",
        "192.168.50.14",
        "192.168.50.15",
        "192.168.50.16",
        "192.168.50.17",
        "192.168.50.18",
        "192.168.50.19",
        "192.168.50.20",
    ]
    expected["command"] = (
        ["flathaving"] * 3
        + ["ha_off_command"] * 2
        + ["status"] * 2
        + ["flathaving"] * 3
    )
    pd.testing.assert_frame_equal(df, expected)


def test_AllScienceExposure():
    r = AllScienceExposure(
        exptime=10,
        off_exptime=1,
        n_offs=10,
        debug=True,
        hardware_config_file="test_hardware_template.txt",
    )

    sci_expected = "expose?type=light&time=10"
    offs_expected = "expose?type=light&time=1&n=10"

    expected = pd.DataFrame(columns=["Name", "ip", "command"])
    expected["Name"] = [
        "Dragonfly301",
        "Dragonfly302",
        "Dragonfly303",
        "Dragonfly304",
        "Dragonfly305",
        "Dragonfly306",
        "Dragonfly307",
        "Dragonfly308",
        "Dragonfly309",
        "Dragonfly310",
    ]
    expected["ip"] = expected["ip"] = [
        "192.168.50.11",
        "192.168.50.12",
        "192.168.50.13",
        "192.168.50.14",
        "192.168.50.15",
        "192.168.50.16",
        "192.168.50.17",
        "192.168.50.18",
        "192.168.50.19",
        "192.168.50.20",
    ]

    expected["command"] = [sci_expected] * 3 + [offs_expected] * 4 + [sci_expected] * 3
    pd.testing.assert_frame_equal(r, expected)


def test_AllTiltScienceFilters():
    r = AllTiltScienceFilters(
        ha_tilt=5.0,
        oiii_tilt=7.0,
        debug=True,
        hardware_config_file="test_hardware_template.txt",
    )
    expected = pd.DataFrame(columns=["Name", "ip", "command"])
    expected["Name"] = [
        "Dragonfly301",
        "Dragonfly302",
        "Dragonfly303",
        "Dragonfly310",
    ]
    expected["ip"] = expected["ip"] = [
        "192.168.50.11",
        "192.168.50.12",
        "192.168.50.13",
        "192.168.50.20",
    ]
    ha_command = f"device/filtertilter?command=set&argument=5.0"
    oiii_command = f"device/filtertilter?command=set&argument=7.0"
    expected["command"] = [ha_command] * 3 + [oiii_command]
    pd.testing.assert_frame_equal(r, expected)
