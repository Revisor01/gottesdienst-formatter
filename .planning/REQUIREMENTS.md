# Requirements: Gottesdienst-Formatter

**Defined:** 2026-03-21
**Core Value:** Output muss 1:1 der Boyens-Fließtext-Vorgabe entsprechen

## v1 Requirements

### Formatierung

- [x] **FMT-01**: Output folgt exakt der Boyens-Fließtext-Struktur (Datum-Überschrift, dann Orte alphabetisch, keine Tabellen)
- [x] **FMT-02**: Zeitformat korrekt: "9.30 Uhr" (mit Punkt), "17 Uhr" (ohne Minuten bei vollen Stunden)
- [x] **FMT-03**: Datumsformat korrekt: "Sonnabend, 5. April" (Sonnabend statt Samstag, kein führendes Null)
- [x] **FMT-04**: Gottesdienst-Typ-Abkürzungen vollständig: Gd., Gd. m. A., Gd. m. T., Familiengd., Konfirmation, Abendmahlgd. m. T., Gd. m. Popularmusik, Gd. m. Konfirmandenprüfung
- [x] **FMT-05**: Pastor-Titel vollständig: P., Pn., Diakon, Prädikantin, R. (nicht nur P./Pn.)
- [x] **FMT-06**: Bei Orten mit mehreren Kirchen den Kirchennamen angeben (z.B. "Heide, St.-Jürgen" vs. "Heide, Auferstehungskirche")
- [x] **FMT-07**: Mehrere Termine am gleichen Ort in einer Zeile möglich (z.B. "11 Uhr, Gd. m. A., anschl. Kirchcafé; 15.30 Uhr, Kinderkirche")
- [x] **FMT-08**: Zusatzinfos wie "anschl. Kirchcafé", "anschl. Kirchenkaffee" korrekt übernommen
- [x] **FMT-09**: Mehrere Pastoren pro Gottesdienst korrekt formatiert (z.B. "Pn. Christ, Pn. Hoffmann, P. Soost")

### Code-Qualität

- [x] **CODE-01**: Formatierungslogik in einem zentralen Modul (nicht 3x dupliziert über app.py, churchdesk_api.py, standalone-Script)
- [x] **CODE-02**: Pastor-Formatierung: eine konsolidierte Implementierung statt drei verschiedener
- [x] **CODE-03**: Klare Schichtentrennung: API-Client / Formatierung / Web-Interface als separate Module
- [x] **CODE-04**: Neue ChurchDesk-Organisation hinzufügen erfordert nur Konfiguration, keinen Code-Change

### Sicherheit

- [x] **SEC-01**: Alle API-Tokens aus Quellcode entfernt, nur via Environment Variables geladen
- [x] **SEC-02**: Flask Secret Key via Environment Variable, nicht hardcoded

### Testing

- [x] **TEST-01**: Unit-Tests für alle Formatierungsfunktionen (Datum, Zeit, Gottesdienst-Typ, Pastor-Titel)
- [x] **TEST-02**: Test-Fixture mit echtem Boyens-Referenz-Output als Goldstandard

### Deployment

- [ ] **DEPLOY-01**: GitHub Actions Workflow: Build Docker Image und Push zu Container Registry
- [ ] **DEPLOY-02**: Automatisches Deployment auf Portainer (kein manueller Server-Build mehr)
- [ ] **DEPLOY-03**: Git Push → Image Build → Portainer Update als vollautomatische Pipeline

## v2 Requirements

### Erweiterung

- **EXT-01**: Weitere Kirchengemeinden mit eigenen ChurchDesk-Instanzen einfach hinzufügbar
- **EXT-02**: Automatischer monatlicher Export/Versand an Boyens

### Monitoring

- **MON-01**: Logging für API-Fehler und fehlgeschlagene Formatierungen
- **MON-02**: Health-Check-Endpoint für Uptime-Monitoring

## Out of Scope

| Feature | Reason |
|---------|--------|
| Andere Konfessionen (Kath., Freikirchlich, Neuapostolisch) | Kirchenkreis liefert nur ev.-luth. Daten |
| Mobile App | Web-Interface genügt |
| Automatischer E-Mail-Versand | Manuelle Übermittlung reicht für v1 |
| Mehrsprachigkeit | Nur Deutsch relevant |
| Print-Layout/PDF-Export | Boyens will Fließtext, kein Layout |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FMT-01 | Phase 2 | Complete |
| FMT-02 | Phase 2 | Complete |
| FMT-03 | Phase 2 | Complete |
| FMT-04 | Phase 2 | Complete |
| FMT-05 | Phase 2 | Complete |
| FMT-06 | Phase 2 | Complete |
| FMT-07 | Phase 2 | Complete |
| FMT-08 | Phase 2 | Complete |
| FMT-09 | Phase 2 | Complete |
| CODE-01 | Phase 1 | Complete |
| CODE-02 | Phase 1 | Complete |
| CODE-03 | Phase 1 | Complete |
| CODE-04 | Phase 1 | Complete |
| SEC-01 | Phase 1 | Complete |
| SEC-02 | Phase 1 | Complete |
| TEST-01 | Phase 3 | Complete |
| TEST-02 | Phase 3 | Complete |
| DEPLOY-01 | Phase 3 | Pending |
| DEPLOY-02 | Phase 3 | Pending |
| DEPLOY-03 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0

---
*Requirements defined: 2026-03-21*
*Last updated: 2026-03-21 after roadmap creation*
