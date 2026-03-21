# Phase 2: Formatierung - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Der generierte Fließtext muss 1:1 der Boyens-Vorgabe entsprechen — ohne redaktionelle Nacharbeit übernehmbar. Alle Formatierungsregeln leiten sich aus dem offiziellen Boyens-Referenzdokument (E-Mail Chefredakteur Johannes Simonsen) ab.

</domain>

<decisions>
## Implementation Decisions

### Gottesdienst-Typ-Abkürzungen
- **D-01:** Standard-Gottesdienst → "Gd."
- **D-02:** Abendmahl → "Gd. m. A."
- **D-03:** Taufe → "Gd. m. T."
- **D-04:** Abendmahl + Taufe → "Abendmahlgd. m. T."
- **D-05:** Familiengottesdienst → "Familiengd."
- **D-06:** Konfirmation → "Konfirmation" (ausgeschrieben, mit Nummer: "1. Konfirmation")
- **D-07:** Popularmusik → "Gd. m. Popularmusik"
- **D-08:** Konfirmandenprüfung → "Gd. m. Konfirmandenprüfung"
- **D-09:** Kinderkirche → "Kinderkirche" (ausgeschrieben)
- **D-10:** Sonderformate wie "Unterwegs" Brotzeit → Titel direkt übernehmen mit Anführungszeichen
- **D-11:** Gemeinschaft → "Gd. der Gemeinschaft"
- **D-12:** Zusatzinfos wie "anschl. Kirchcafé", "anschl. Kirchenkaffee" → nach dem Typ anhängen, kommagetrennt

### Pastor-Titel-Formatierung
- **D-13:** Pastor → "P. Nachname"
- **D-14:** Pastorin → "Pn. Nachname"
- **D-15:** Diakon → "Diakon Nachname" (ausgeschrieben, NICHT "D.")
- **D-16:** Prädikantin → "Prädikantin Nachname" (ausgeschrieben)
- **D-17:** R. → "R. Nachname" (Referent/in — Abkürzung beibehalten)
- **D-18:** Mehrere Pastoren → kommagetrennt: "Pn. Christ, Pn. Hoffmann, P. Soost"
- **D-19:** Team-Bezeichnungen → "Pn. Sievers & Team" (& Team beibehalten)
- **D-20:** "jeweils" bei mehreren Zeiten mit selben Pastoren → "jeweils Pn. Luthe"

### Datums- und Zeitformate
- **D-21:** Wochentag, Tag. Monat → "Sonnabend, 5. April" (NICHT "Samstag")
- **D-22:** Doppelpunkt nach dem Datum bei der Überschrift ist optional (Boyens-Referenz hat beides: mit und ohne)
- **D-23:** Uhrzeiten: "9.30 Uhr" (mit Punkt), "17 Uhr" (ohne Minuten bei vollen Stunden)
- **D-24:** Kein führendes Null beim Tag: "5. April" nicht "05. April"

### Standort-Formatierung
- **D-25:** Orte mit einer Kirche → nur Ortsname: "Albersdorf:"
- **D-26:** Orte mit mehreren Kirchen → "Ort, Kirchenname:" z.B. "Heide, St.-Jürgen:" oder "Brunsbüttel, Jakobuskirche:"
- **D-27:** Multi-Church-Städte: Heide (St.-Jürgen, Auferstehungskirche), Brunsbüttel (Jakobuskirche, Apsis im Gemeindezentrum)
- **D-28:** Büsum → Sonderregel gemäß CLAUDE.md: In Übersicht "Urlauberseelsorge", in Output "Büsum"
- **D-29:** Alphabetische Sortierung der Orte innerhalb eines Datums

### Zeilen-Struktur
- **D-30:** Format: "Ort: Uhrzeit, Typ, Pastor" — alles in einer Zeile
- **D-31:** Mehrere Termine am gleichen Ort → Semikolon-getrennt in einer Zeile: "11 Uhr, Gd. m. A., anschl. Kirchcafé; 15.30 Uhr, Kinderkirche, jeweils Pn. Luthe"
- **D-32:** Keine Tabellen, keine Einladungen, keine zusätzlichen Erläuterungen — nur Termine im Fließtext
- **D-33:** Termine nach Datum gruppiert, NICHT nach Orten

### Claude's Discretion
- Reihenfolge der Typ-Erkennung in format_service_type() (optimale Matching-Logik)
- Fallback-Verhalten bei unbekannten Typen oder fehlenden Daten
- Wie "Sonderformate" (z.B. Brotzeit-Events) aus ChurchDesk-Titeln erkannt werden

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Formatierungslogik (aktueller Stand)
- `web/formatting.py` — Zentrale Formatierungsfunktionen (nach Phase 1 konsolidiert). MUSS gegen diese Entscheidungen geprüft und angepasst werden.
- `web/churchdesk_api.py` — extract_boyens_location(), EventAnalyzer, Multi-Church-Logic, LOCATION_MAPPINGS

### Boyens-Referenzformat
- Die offizielle Boyens-Vorgabe ist in den Decisions oben vollständig erfasst (aus E-Mail Chefredakteur Johannes Simonsen)

### Projektregeln
- `CLAUDE.md` — Büsum-Sonderregel: Übersicht → "Urlauberseelsorge", Output → "Büsum"

</canonical_refs>

<code_context>
## Existing Code Insights

### Zu fixende Lücken in web/formatting.py
- format_service_type(): Fehlt "Gd. m. Popularmusik", "Gd. m. Konfirmandenprüfung", "Abendmahlgd. m. T.", "Gd. der Gemeinschaft"
- format_pastor(): "Diakon" wird zu "D." statt "Diakon" (ausgeschrieben), "Prädikantin" wird zu "Prädikant" (ohne -in)
- format_pastor(): Trenner ist "&" statt "," (Boyens: "Pn. Christ, Pn. Hoffmann, P. Soost")
- format_pastor(): "jeweils"-Logik fehlt für Multi-Termin-Zeilen

### Zu fixende Lücken in web/churchdesk_api.py
- convert_churchdesk_events_to_boyens(): Prüfen ob Semikolon-Zusammenfassung für Multi-Termine am gleichen Ort funktioniert
- extract_boyens_location(): Multi-Church-Erkennung gegen Boyens-Referenz validieren
- Zusatzinfos ("anschl. Kirchcafé") aus Event-Daten extrahieren

### Bestehende Patterns
- format_service_type() nutzt if/elif-Kette mit lower()-Check — erweitern, nicht umbauen
- extract_boyens_location() hat LOCATION_MAPPINGS Dict — gut erweiterbar
- MULTI_CHURCH_CITIES Liste in churchdesk_api.py

### Integration Points
- web/app.py process_excel_file() — nutzt formatting.py Funktionen
- web/app.py convert_churchdesk_events_to_boyens() — Output-Generierung
- web/churchdesk_api.py format_event_for_boyens() — Event-Transformation

</code_context>

<specifics>
## Specific Ideas

- Boyens-Referenz zeigt: "Hennstedt: 11 Uhr, Gd. m. A., anschl. Kirchcafé; 18.30 Uhr; 15.30 Uhr, Kinderkirche, jeweils Pn. Luthe" — mehrere Zeiten mit selben Pastoren auf einer Zeile
- "Heide, Auferstehungskirche: 17 Uhr, „Unterwegs" Brotzeit: Die Wohnzimmerkirche in Heide (Süd), Pn. Sievers & Team" — Sonderformate mit Anführungszeichen direkt übernehmen
- "R. Sierk" als Titel — vermutlich "Referent" — einfach als "R." beibehalten

</specifics>

<deferred>
## Deferred Ideas

None — Discussion stayed within phase scope

</deferred>

---

*Phase: 02-formatierung*
*Context gathered: 2026-03-22*
