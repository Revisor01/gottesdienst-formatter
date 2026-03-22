#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zentrale Formatierungsfunktionen fuer Boyens-Medien-Output.
Einzige Quelle der Wahrheit — alle Codepfade importieren von hier.
"""
import re

# Modul-globale Liste der Custom-Typ-Zuordnungen (aus DB geladen).
# Jedes Element: {'keyword': str, 'output_label': str, 'priority': int}
_custom_mappings = []

# Modul-globaler Pastor-Cache (aus DB geladen).
# Jedes Element: {'first_name': str|None, 'last_name': str, 'title': str}
_pastor_cache = []


def load_custom_mappings(app):
    """Laedt Custom-Typ-Zuordnungen aus der DB und speichert sie im Modul-Cache."""
    global _custom_mappings
    try:
        with app.app_context():
            from models import ServiceTypeMapping
            mappings = (ServiceTypeMapping.query
                        .filter_by(is_active=True)
                        .order_by(ServiceTypeMapping.priority.desc())
                        .all())
            _custom_mappings = [
                {'keyword': m.keyword.lower(), 'output_label': m.output_label}
                for m in mappings
            ]
    except Exception:
        # Tabelle existiert noch nicht (Tests, erste Migration)
        _custom_mappings = []


def reload_custom_mappings(app):
    """Alias fuer load_custom_mappings — expliziter Name fuer post-CRUD-Aufrufe."""
    load_custom_mappings(app)


def load_pastors(app):
    """Laedt Pastor-Eintraege aus der DB und speichert sie im Modul-Cache."""
    global _pastor_cache
    try:
        with app.app_context():
            from models import Pastor
            pastors = Pastor.query.filter_by(is_active=True).all()
            _pastor_cache = [
                {
                    'first_name': p.first_name.strip() if p.first_name else None,
                    'last_name': p.last_name.strip(),
                    'title': p.title.strip(),
                }
                for p in pastors
            ]
    except Exception:
        # Tabelle existiert noch nicht (Tests, erste Migration)
        _pastor_cache = []


def reload_pastors(app):
    """Alias fuer load_pastors — expliziter Name fuer post-CRUD-Aufrufe."""
    load_pastors(app)


def format_date(date_obj):
    """Formatiert Datum im gewuenschten Format"""
    if date_obj is None:
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
    if date_obj is None:
        return ""

    hour = date_obj.hour
    minute = date_obj.minute

    if minute == 0:
        return "{} Uhr".format(hour)
    else:
        return "{}.{:02d} Uhr".format(hour, minute)


def _match_service_type(titel):
    """Interne Hilfsfunktion: Ordnet Titel einem formatierten Typ zu (ohne Doppelpunkt-Split)."""
    titel_lower = titel.lower()

    # Custom-Zuordnungen zuerst pruefen (hoehere Prioritaet als Built-ins)
    for mapping in _custom_mappings:
        if mapping['keyword'] in titel_lower:
            return mapping['output_label']

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
    # Pruefe auf 'tauf' (deckt "Taufe", "Taufgottesdienst" ab)
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
    elif 'kinderkirche' in titel_lower or 'kindergottesdienst' in titel_lower:
        return 'Kinderkirche'
    elif 'familiengottesdienst' in titel_lower or 'familiengd' in titel_lower:
        return 'Familiengd.'
    elif 'andacht' in titel_lower:
        return 'Andacht'
    else:
        return 'Gd.'


def format_service_type(titel):
    """Formatiert den Gottesdiensttyp — strikt nach Boyens, nur Typ-Abkürzung, keine Untertitel."""
    if not titel:
        return "Gd."

    # Bei Doppelpunkt: nur den Teil vor dem Doppelpunkt für Typ-Matching nutzen
    if ':' in titel:
        titel = titel.split(':', 1)[0].strip()

    return _match_service_type(titel)


def _extract_surname(name_str):
    """Extrahiert den Nachnamen — behält Dr./Prof. als Teil des Nachnamens."""
    parts = name_str.split()
    if len(parts) <= 1:
        return name_str
    # Wenn vorletztes Wort akademisch ist: "Dr. Stein" → "Dr. Stein"
    if len(parts) == 2 and parts[0].lower().rstrip('.') in {'dr', 'prof'}:
        return name_str
    # Sonst: letztes Wort (ggf. mit Dr. davor)
    if len(parts) > 2 and parts[-2].lower().rstrip('.') in {'dr', 'prof'}:
        return '{} {}'.format(parts[-2], parts[-1])
    return parts[-1]


def _is_noise_contributor(text):
    """Erkennt Nicht-Personen-Beiträge die rausgefiltert werden sollen."""
    text_lower = text.lower().strip()
    # Komplette Noise-Einträge (kein Personenname)
    noise_patterns = [
        'dem team', 'vielen ', 'anschließend', 'anschl.', 'mitbringfrühstück',
        'kirchenmäuse'
    ]
    return any(p in text_lower for p in noise_patterns)


def _lookup_pastor(text):
    """
    Sucht im Pastor-Cache ob ein bekannter Nachname im Text vorkommt.

    Gibt das formatierte 'Titel Nachname' zurueck oder None wenn kein Match.
    Disambiguierung: Wenn Vorname auch im Text → exakter Match.
    Wenn mehrere gleiche Nachnamen: Vorname-Match bevorzugen, sonst erster Eintrag.
    """
    text_lower = text.lower()
    matches = []
    for p in _pastor_cache:
        last = p['last_name'].lower()
        if last in text_lower:
            matches.append(p)

    if not matches:
        return None

    if len(matches) == 1:
        p = matches[0]
        return '{} {}'.format(p['title'], p['last_name'])

    # Mehrere Treffer (gleicher Nachname, verschiedene Titel) → Vorname zur Disambiguierung
    for p in matches:
        if p['first_name'] and p['first_name'].lower() in text_lower:
            return '{} {}'.format(p['title'], p['last_name'])

    # Kein Vorname-Match → ersten nehmen
    p = matches[0]
    return '{} {}'.format(p['title'], p['last_name'])


def _regex_fallback_pastor(contrib):
    """
    Fallback fuer Pastoren die NICHT in der DB stehen.
    Regex-basiertes Prefix-Parsing: Pastor → P., Pastorin → Pn., etc.
    Nur Nachname ausgeben (Vorname entfernen).
    """
    # Bekannte Prefixe und ihre Boyens-Abkuerzungen
    prefix_map = [
        ('Diakonin ',      'Diakonin'),
        ('Diakon ',        'Diakon'),
        ('Pastores ',      'Ps.'),
        ('Pastorin ',      'Pn.'),
        ('Pastor ',        'P.'),
        ('Pfarrer ',       'P.'),
        ('Pn. ',           'Pn.'),
        ('P. ',            'P.'),
        ('Prädikantin ',   'Prä.'),
        ('Prädikant ',     'Prä.'),
        ('R. ',            'R.'),
    ]

    for prefix, title in prefix_map:
        if contrib.startswith(prefix):
            rest = contrib[len(prefix):].strip()
            surname = _extract_surname(rest)
            return '{} {}'.format(title, surname)

    # Kein bekannter Prefix — durchreichen
    return contrib


def format_pastor(contributor: str) -> str:
    """
    Formatiert Mitwirkende nach Boyens-Standard.

    Strategie:
    1. DB-Lookup: Nachname im Pastor-Cache? → exakter Match mit Titel
    2. Regex-Fallback: Prefix-Parsing fuer unbekannte Pastoren
    3. Durchreichen: Gruppen (Kantorei, WGT-Team, Frauenhilfe, etc.)
    """
    if not contributor:
        return ""

    name = str(contributor).strip()

    # Weltgebetstagsteam normalisieren — ausschreiben
    wgt_patterns = ['weltgebetstagsteam', 'weltsgebetstagsteam', 'weltgebetstagssteam',
                    'wgt-team', 'wgt team', 'weltgebetstagskomitee']
    name_lower = name.lower()
    if any(p in name_lower for p in wgt_patterns):
        return 'Weltgebetstagsteam'

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

    if not split_done and ', ' in name:
        contributors = [c.strip() for c in name.split(', ')]

    formatted_contributors = []

    for contrib in contributors:
        if not contrib:
            continue

        # Noise-Beitraege rausfiltern
        if _is_noise_contributor(contrib):
            continue

        contrib_lower = contrib.lower()

        # Spezialfaelle
        if 'kirchspiel-pastor:innen' in contrib_lower:
            formatted_contributors.append('Kirchspiel-Pastor:innen')
            continue
        if 'konfirmand:innen' in contrib_lower:
            formatted_contributors.append('Konfirmand:innen')
            continue

        # WGT normalisieren (auch als Teil eines Splits)
        if any(p in contrib_lower for p in wgt_patterns):
            formatted_contributors.append('Weltgebetstagsteam')
            continue

        # Noise-Teile aus dem String entfernen
        for noise_part in ['Prädikantin in Ausbildung ', 'Prädikant in Ausbildung ',
                           ' Prädikantin in Ausbildung', ' Prädikant in Ausbildung',
                           ' in Ausbildung']:
            contrib = contrib.replace(noise_part, ' ').strip()
        for suffix in [' anschließend', ' anschl.']:
            idx = contrib.lower().find(suffix.lower())
            if idx > 0:
                contrib = contrib[:idx].strip()

        # 1. DB-Lookup: Nachname im Pastor-Cache?
        result = _lookup_pastor(contrib)
        if result is not None:
            formatted_contributors.append(result)
        else:
            # 2. Regex-Fallback: Prefix-Parsing
            formatted_contributors.append(_regex_fallback_pastor(contrib))

    # Deduplizierung
    seen = []
    for fc in formatted_contributors:
        if fc not in seen:
            seen.append(fc)
    formatted_contributors = seen

    # D-18: Komma als Trenner
    result = ', '.join(formatted_contributors)

    # D-19: "& Team" wieder anhaengen
    if has_team:
        result += ' & Team'

    return result
