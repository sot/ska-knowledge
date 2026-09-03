"""Verify every symbol the ska-knowledge router table claims exists."""

import importlib
import sys

CLAIMS = [
    ("chandra_aca.aca_image", "get_aca_images"),
    ("chandra_aca.aca_image", "ACAImage"),
    ("chandra_aca.maude_decom", "get_aca_images"),
    ("chandra_aca.transform", "yagzag_to_radec"),
    ("chandra_aca.transform", "radec_to_yagzag"),
    ("chandra_aca.transform", "pixels_to_yagzag"),
    ("chandra_aca.transform", "yagzag_to_pixels"),
    ("chandra_aca.transform", "mag_to_count_rate"),
    ("chandra_aca.star_probs", "acq_success_prob"),
    ("chandra_aca.drift", "get_aca_offsets"),
    ("cheta.fetch", "MSID"),
    ("cheta.fetch", "MSIDset"),
    ("cheta.fetch", "get_telem"),
    ("cheta.fetch_sci", "Msid"),
    ("cxotime", "CxoTime"),
    ("Quaternion", "Quat"),
    ("Quaternion", "normalize"),
    ("agasc", "get_agasc_cone"),
    ("agasc", "get_star"),
    ("agasc", "get_stars"),
    ("agasc", "get_agasc_filename"),
    ("kadi.commands", "get_cmds"),
    ("kadi.commands.states", "get_states"),
    ("kadi.commands.states", "get_continuity"),
    ("kadi.commands.states", "reduce_states"),
    ("kadi.commands.observations", "get_observations"),
    ("kadi.commands.observations", "get_starcats"),
    ("kadi.events", "manvrs"),
    ("kadi.events", "dwells"),
    ("kadi.events", "obsids"),
    ("mica.starcheck", "get_starcheck_catalog"),
    ("mica.starcheck", "get_starcat"),
    ("mica.starcheck", "get_dither"),
    ("mica.archive.aca_l0", "get_aca_images"),
    ("mica.archive.aca_dark", "get_dark_cal_props"),
    ("mica.archive.asp_l1", "get_files"),
    ("mica.archive.obspar", "get_obspar"),
    ("mica.stats.acq_stats", "get_stats"),
    ("mica.stats.guide_stats", "get_stats"),
    ("proseco", "get_aca_catalog"),
    ("sparkles", "run_aca_review"),
    ("xija", "ThermalModel"),
    ("xija.get_model_spec", "get_xija_model_spec"),
    ("ska_sun", "pitch"),
    ("ska_sun", "position"),
    ("ska_sun", "nominal_roll"),
    ("maude", "get_msids"),
    ("ska_helpers.chandra_models", "get_data"),
    ("chandra_maneuver", "duration"),
    ("parse_cm.backstop", "read_backstop"),
]

# ska3-aca only: the monitor/trending family. Skipped unless running in ska3-aca.
# NOTE: jobwatch.skawatch is deliberately absent -- it cannot be imported off HEAD
# (module-level glob of /home/kadi/... at skawatch.py:136).
CLAIMS_ACA = [
    # Base classes live in jobwatch.jobwatch; the Ska-configured subclasses are in
    # jobwatch.skawatch / jobwatch.hourly_watch, and skawatch is not importable off HEAD.
    ("jobwatch.jobwatch", "JobWatch"),
    ("jobwatch.jobwatch", "FileWatch"),
    ("jobwatch.jobwatch", "DbWatch"),
    ("fss_check.check_fss", "get_large_pitch_roll_error_intervals"),
    ("fss_check.check_fss", "get_spm_pitch_roll"),
    ("aca_hi_bgd.update_bgd_events", "get_events"),
    ("kalman_watch.kalman_perigee_mon", "EventPerigee"),
    ("kalman_watch.low_kalman_mon", "main"),
    ("kalman_watch.monitor_win_perigee", "main"),
    ("attitude_error_mon.att_err_mon", "att_err_hist"),
    ("aca_weekly_report.report", "get_acq_anoms"),
    ("ska_report_ranges", "in_month"),
    ("ska_report_ranges", "get_update_ranges"),
    ("ska_report_ranges", "timerange"),
]

# Symbols that exist only above a given package version. ska3-aca lags ska3-flight on
# chandra_aca (4.53.0 vs 4.56.0 as of 2026-09-03), so these must not be asserted blindly.
CLAIMS_VERSION_GATED = [
    ("chandra_aca", "4.56.0", "chandra_aca.aca_image", "get_aca_images_cheta"),
]

CONSOLE_SCRIPTS_ACA = [
    "skawatch_daily", "skawatch_hourly", "fss_check_daily_fss", "aca_hi_bgd_update",
    "kalman_watch_low_kalman_mon", "kalman_watch_kalman_perigee_mon",
    "kalman_watch_monitor_win_perigee", "attitude_error_mon", "aca_weekly_report",
]


def main():
    print(f"python  : {sys.executable}")
    ok, bad, noimport = [], [], []
    for modname, attr in CLAIMS:
        try:
            mod = importlib.import_module(modname)
        except Exception as err:  # noqa: BLE001
            noimport.append((modname, attr, f"{type(err).__name__}: {err}"))
            continue
        if hasattr(mod, attr):
            ok.append((modname, attr))
        else:
            bad.append((modname, attr))

    print(f"\n== OK ({len(ok)}) ==")
    for m, a in ok:
        print(f"  {m}.{a}")
    if bad:
        print(f"\n== MISSING ATTRIBUTE ({len(bad)}) ==")
        for m, a in bad:
            print(f"  {m}.{a}")
    if noimport:
        print(f"\n== IMPORT FAILED ({len(noimport)}) ==")
        for m, a, e in noimport:
            print(f"  {m}.{a}  -> {e}")

    # Version-gated symbols: present only at/above a stated package version
    from packaging.version import Version

    print("\n== version-gated ==")
    for pkgname, minver, modname, attr in CLAIMS_VERSION_GATED:
        try:
            pkg = importlib.import_module(pkgname)
            have = getattr(pkg, "__version__", "0")
            mod = importlib.import_module(modname)
            present = hasattr(mod, attr)
            expected = Version(have) >= Version(minver)
            verdict = "ok" if present == expected else "MISMATCH"
            print(f"  {modname}.{attr}: {pkgname} {have} "
                  f"(needs >= {minver}) present={present} -> {verdict}")
            if verdict != "ok":
                bad.append((modname, attr))
        except Exception as err:  # noqa: BLE001
            print(f"  {modname}.{attr}: could not check ({type(err).__name__}: {err})")

    # ska3-aca extras: only meaningful in that environment
    import shutil

    try:
        importlib.import_module("kalman_watch")
        in_aca = True
    except Exception:  # noqa: BLE001
        in_aca = False

    if in_aca:
        aca_bad = []
        for modname, attr in CLAIMS_ACA:
            try:
                mod = importlib.import_module(modname)
            except Exception as err:  # noqa: BLE001
                aca_bad.append((modname, attr, f"{type(err).__name__}: {err}"))
                continue
            if not hasattr(mod, attr):
                aca_bad.append((modname, attr, "missing attribute"))
        missing_scripts = [s for s in CONSOLE_SCRIPTS_ACA if not shutil.which(s)]
        print(f"\n== ska3-aca: {len(CLAIMS_ACA) - len(aca_bad)}/{len(CLAIMS_ACA)} symbols, "
              f"{len(CONSOLE_SCRIPTS_ACA) - len(missing_scripts)}/{len(CONSOLE_SCRIPTS_ACA)} "
              f"console scripts ==")
        for m, a, e in aca_bad:
            print(f"  BAD {m}.{a} -> {e}")
        for s_ in missing_scripts:
            print(f"  MISSING SCRIPT {s_}")
        bad = bad or aca_bad or missing_scripts
    else:
        print("\n== ska3-aca checks skipped (not in ska3-aca env) ==")

    return 1 if (bad or noimport) else 0


if __name__ == "__main__":
    sys.exit(main())
