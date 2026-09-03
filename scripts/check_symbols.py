"""Verify every symbol the ska-knowledge router table claims exists."""

import importlib
import sys

CLAIMS = [
    ("chandra_aca.aca_image", "get_aca_images"),
    ("chandra_aca.aca_image", "get_aca_images_cheta"),
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

    return 1 if (bad or noimport) else 0


if __name__ == "__main__":
    sys.exit(main())
