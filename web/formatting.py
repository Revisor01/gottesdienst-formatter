#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zentrale Formatierungsfunktionen fuer Boyens-Medien-Output.
Einzige Quelle der Wahrheit — alle Codepfade importieren von hier.
"""
import re
import pandas as pd


def format_date(date_obj):
    """Formatiert Datum im gewuenschten Format"""
    if pd.isna(date_obj):
        return ""

    weekday_map = {
        0: 'Montag', 1: 'Dienstag', 2: 'Mittwoch', 3: 'Donnerstag',
        4: 'Freitag', 5: 'Sonnabend', 6: 'Sonntag'
    }

    weekday = weekday_map.get(date_obj.weekday(), 'Unbekannt')
    day = date_obj.day

    month_map = {
        1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April',
        5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August',
        9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
    }
    month = month_map.get(date_obj.month, 'Unbekannt')

    return "{}, {}. {}".format(weekday, day, month)


def format_time(date_obj):
    """Extrahiert und formatiert Uhrzeit aus datetime"""
    if pd.isna(date_obj):
        return ""

    hour = date_obj.hour
    minute = date_obj.minute

    if minute == 0:
        return "{} Uhr".format(hour)
    else:
        return "{}.{:02d} Uhr".format(hour, minute)


def format_service_type(titel):
    """Formatiert den Gottesdiensttyp"""
    if pd.isna(titel):
        return "Gd."

    titel_lower = titel.lower()

    # D-10: Sonderformate mit Anfuehrungszeichen direkt uebernehmen
    if '„' in titel or '"' in titel or '»' in titel:
        return titel

    if 'tauffest' in titel_lower:
        return 'Tauffest'
    elif 'diamantene konfirmation' in titel_lower:
        return 'Diamantene Konfirmation'
    elif 'goldene konfirmation' in titel_lower:
        return 'Goldene Konfirmation'
    elif 'silberne konfirmation' in titel_lower:
        return 'Silberne Konfirmation'
    # D-08: Konfirmandenprüfung — VOR generischem Konfirmation-Check
    elif 'konfirmandenprüfung' in titel_lower or 'konfirmandenpruefung' in titel_lower:
        return 'Gd. m. Konfirmandenprüfung'
    # D-06: Nummerierte Konfirmation (z.B. "1. Konfirmation")
    elif re.search(r'(\d+)\.\s*konfirmation', titel_lower):
        match = re.search(r'(\d+)\.\s*konfirmation', titel_lower)
        return '{}. Konfirmation'.format(match.group(1))
    elif 'konfirmation' in titel_lower:
        return 'Konfirmation'
    # D-04: Abendmahl + Taufe kombiniert — VOR den einzelnen Checks
    # Pruefe auf 'tauf' (deckt "Taufe", "Taufgottesdienst", "Taufgottesdienst" ab)
    elif 'abendmahl' in titel_lower and 'tauf' in titel_lower:
        return 'Abendmahlgd. m. T.'
    elif 'abendmahl' in titel_lower:
        return 'Gd. m. A.'
    elif 'tauf' in titel_lower:
        return 'Gd. m. T.'
    # D-07: Popularmusik
    elif 'popularmusik' in titel_lower:
        return 'Gd. m. Popularmusik'
    # D-11: Gemeinschaft
    elif 'gemeinschaft' in titel_lower:
        return 'Gd. der Gemeinschaft'
    elif 'abendsegen' in titel_lower:
        return 'Abendsegen'
    elif 'kinderkirche' in titel_lower or 'kinder' in titel_lower:
        return 'Kinderkirche'
    elif 'familie' in titel_lower:
        return 'Familiengd.'
    elif 'andacht' in titel_lower:
        return 'Andacht'
    else:
        return 'Gd.'


def format_pastor(contributor: str) -> str:
    """
    Format pastor name according to Boyens Media standards:
    - Diakonin → Diakonin (ausgeschrieben)
    - Diakon → Diakon (ausgeschrieben)
    - Pastorin → Pn.
    - Pastor → P.
    - Prädikantin → Prädikantin (ausgeschrieben)
    - Prädikant → Prädikant (ausgeschrieben)
    - R. → R. (Referent, Abkuerzung beibehalten)
    - Multiple pastors: combine with comma (D-18)
    - & Team: beibehalten (D-19)
    - Special cases: Kirchspiel-Pastor:innen, Konfirmand:innen etc.
    """
    if not contributor:
        return ""

    name = str(contributor).strip()

    # D-19: "& Team" vor dem Splitten merken und spaeter anhaengen
    has_team = name.endswith('& Team') or name.endswith('&amp; Team')
    if has_team:
        name = name.replace('&amp; Team', '').replace('& Team', '').strip()

    # Splitten: erst auf & und und, dann Komma als Fallback
    contributors = [name]
    primary_delimiters = [' & ', ' und ', ' + ', ' / ']
    split_done = False
    for delimiter in primary_delimiters:
        if delimiter in name:
            contributors = [c.strip() for c in name.split(delimiter)]
            split_done = True
            break

    # Komma als Fallback-Delimiter (wenn kein & oder und gefunden)
    if not split_done and ', ' in name:
        contributors = [c.strip() for c in name.split(', ')]

    formatted_contributors = []

    for contrib in contributors:
        # Handle special cases for individual contributors
        contrib_lower = contrib.lower()
        if 'kirchspiel-pastor:innen' in contrib_lower:
            formatted_contributors.append('Kirchspiel-Pastor:innen')
            continue
        if 'konfirmand:innen' in contrib_lower:
            formatted_contributors.append('Konfirmand:innen')
            continue

        # Remove existing prefixes
        prefixes = ['Pastores ', 'Pastor ', 'Pastorin ', 'Pfarrer ', 'P. ', 'Pn. ', 'Ps. ',
                    'Diakon ', 'Diakonin ', 'D. ', 'Dn. ', 'Prädikantin ', 'Prädikant ',
                    'R. ']
        clean_name = contrib
        for prefix in prefixes:
            if clean_name.startswith(prefix):
                clean_name = clean_name[len(prefix):].strip()
                break

        # Determine new prefix based on original text - be more specific in detection
        if 'diakonin' in contrib_lower:
            # D-15: Diakonin ausgeschrieben
            formatted_contributors.append("Diakonin {}".format(clean_name))
        elif 'diakon' in contrib_lower:
            # D-15: Diakon ausgeschrieben (nicht D.)
            formatted_contributors.append("Diakon {}".format(clean_name))
        elif 'pastores' in contrib_lower:
            formatted_contributors.append("Ps. {}".format(clean_name))
        elif 'pastorin' in contrib_lower:
            formatted_contributors.append("Pn. {}".format(clean_name))
        elif 'pastor' in contrib_lower or 'pfarrer' in contrib_lower:
            formatted_contributors.append("P. {}".format(clean_name))
        elif 'pn.' in contrib_lower:
            formatted_contributors.append("Pn. {}".format(clean_name))
        elif 'p.' in contrib_lower:
            formatted_contributors.append("P. {}".format(clean_name))
        # D-16: Prädikantin vor Prädikant (weil "prädikant" in "prädikantin" enthalten)
        elif 'prädikantin' in contrib_lower:
            formatted_contributors.append("Prädikantin {}".format(clean_name))
        elif 'prädikant' in contrib_lower:
            formatted_contributors.append("Prädikant {}".format(clean_name))
        # D-17: R. als Titel beibehalten
        elif contrib.startswith('R. '):
            formatted_contributors.append("R. {}".format(clean_name))
        else:
            # Keep original if unclear - don't assume Pastor
            formatted_contributors.append(contrib)

    # D-18: Komma als Trenner (nicht &)
    result = ', '.join(formatted_contributors)

    # D-19: "& Team" wieder anhaengen
    if has_team:
        result += ' & Team'

    return result
