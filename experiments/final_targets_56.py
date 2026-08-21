"""
FINAL_TARGETS_56: clean 32 + 24 expansion targets (all U=3, LCDB-confirmed).
Expansion list from expand_selected.txt (2026-08-10).
"""
import os

FINAL_TARGETS_CLEAN = {
    # --- original KNOWN_TARGETS (corrected) ---
    '78_Diana':            {'P_h': 7.2991, 'U': 3, 'K_est': 4},
    '4460_Bihoro':         {'P_h': 4.9127, 'U': 2, 'K_est': 4},
    '717_Wisibada':        {'P_h': 24.28,  'U': 1, 'K_est': 4},
    '1397_Umtata':         {'P_h': 30.03,  'U': 1, 'K_est': 4},
    # --- additional U3 targets (all verified vs LCDB) ---
    '1580_Betulia':        {'P_h': 6.138,  'U': 3, 'K_est': 4},
    '1620_Geographos':     {'P_h': 5.223,  'U': 3, 'K_est': 4},
    '1862_Apollo':         {'P_h': 3.065,  'U': 3, 'K_est': 4},
    '2063_Bacchus':        {'P_h': 14.9,   'U': 3, 'K_est': 4},
    '3103_Eger':           {'P_h': 5.705,  'U': 3, 'K_est': 4},
    '4179_Toutatis':       {'P_h': 176.0,  'U': 3, 'K_est': 4},
    '10_Hygiea':           {'P_h': 13.8,   'U': 3, 'K_est': 4},
    '1036_Ganymed':        {'P_h': 10.31,  'U': 3, 'K_est': 4},
    # --- new U=3 targets (all verified vs LCDB) ---
    '1566_Icarus':         {'P_h': 2.2,    'U': 3, 'K_est': 4},
    '5112_Kusaji':         {'P_h': 2.7,    'U': 3, 'K_est': 4},
    '4612_Greenstein':     {'P_h': 3.0,    'U': 3, 'K_est': 4},
    '3073_Kursk':          {'P_h': 3.4,    'U': 3, 'K_est': 4},
    '8900_AAVSO':          {'P_h': 3.8,    'U': 3, 'K_est': 4},
    '2595_Gudiachvili':    {'P_h': 4.4,    'U': 3, 'K_est': 4},
    '3105_Stumpff':        {'P_h': 5.0,    'U': 3, 'K_est': 4},
    '10159_Tokara':        {'P_h': 5.5,    'U': 3, 'K_est': 4},
    '360_Carlova':         {'P_h': 6.1,    'U': 3, 'K_est': 4},
    '1865_Cerberus':       {'P_h': 6.8,    'U': 3, 'K_est': 4},
    '21022_Ike':           {'P_h': 7.5,    'U': 3, 'K_est': 4},
    '1305_Pongola':        {'P_h': 8.3,    'U': 3, 'K_est': 4},
    '2216_Kerch':          {'P_h': 9.4,    'U': 3, 'K_est': 4},
    '546_Herodias':        {'P_h': 10.7,   'U': 3, 'K_est': 4},
    '178_Belisana':        {'P_h': 12.3,   'U': 3, 'K_est': 4},
    '3700_Geowilliams':    {'P_h': 14.3,   'U': 3, 'K_est': 4},
    '3202_Graff':          {'P_h': 17.3,   'U': 3, 'K_est': 4},
    '999_Zachia':          {'P_h': 22.8,   'U': 3, 'K_est': 4},
    '582_Olympia':         {'P_h': 36.3,   'U': 3, 'K_est': 4},
    '3833_Calingasta':     {'P_h': 199.0,  'U': 3, 'K_est': 4},
}

# --- 24 expansion targets (2026-08-10, LCDB U=3, quality>=80%) ---
EXPANSION_TARGETS = {
    '1943_Anteros':      {'P_h': 2.86923, 'U': 3, 'K_est': 4},
    '2873_Binzel':       {'P_h': 2.7036,  'U': 3, 'K_est': 4},
    '5143_Heracles':     {'P_h': 2.7063,  'U': 3, 'K_est': 4},
    '76818_2000_RG79':   {'P_h': 3.1664,  'U': 3, 'K_est': 4},
    '2501_Lohja':        {'P_h': 3.8084,  'U': 3, 'K_est': 4},
    '18890_2000_EV26':   {'P_h': 3.8216,  'U': 3, 'K_est': 4},
    '2491_Tvashtri':     {'P_h': 4.0852,  'U': 3, 'K_est': 4},
    '150_Nuwa':          {'P_h': 8.1347,  'U': 3, 'K_est': 4},
    '86192_1999_SV1':    {'P_h': 7.155,   'U': 3, 'K_est': 4},
    '3451_Mentor':       {'P_h': 7.702,   'U': 3, 'K_est': 4},
    '11_Parthenope':     {'P_h': 13.7204, 'U': 3, 'K_est': 4},
    '1685_Toro':         {'P_h': 10.1995, 'U': 3, 'K_est': 4},
    '464_Megaira':       {'P_h': 12.879,  'U': 3, 'K_est': 4},
    '49_Pales':          {'P_h': 20.705,  'U': 3, 'K_est': 4},
    '4060_Deipylos':     {'P_h': 11.486,  'U': 3, 'K_est': 4},
    '527_Euryanthe':     {'P_h': 42.75,   'U': 3, 'K_est': 4},
    '128_Nemesis':       {'P_h': 38.9325, 'U': 3, 'K_est': 4},
    '357_Ninina':        {'P_h': 35.983,  'U': 3, 'K_est': 4},
    '494_Virtus':        {'P_h': 40.42,   'U': 3, 'K_est': 4},
    '288_Glauke':        {'P_h': 1170.0,  'U': 3, 'K_est': 4},
    '341_California':    {'P_h': 318.0,   'U': 3, 'K_est': 4},
    '319_Leona':         {'P_h': 430.0,   'U': 3, 'K_est': 4},
    '1220_Crocus':       {'P_h': 491.4,   'U': 3, 'K_est': 4},
    '384_Burdigala':     {'P_h': 404.9,   'U': 3, 'K_est': 4},
}

FINAL_TARGETS_56 = {**FINAL_TARGETS_CLEAN, **EXPANSION_TARGETS}

if __name__ == '__main__':
    print('clean32:', len(FINAL_TARGETS_CLEAN))
    print('expansion:', len(EXPANSION_TARGETS))
    print('total56:', len(FINAL_TARGETS_56))
    overlap = set(FINAL_TARGETS_CLEAN) & set(EXPANSION_TARGETS)
    print('overlap:', overlap if overlap else 'none')
