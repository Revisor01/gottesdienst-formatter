# Phase 3: Pipeline - Research

**Researched:** 2026-03-22
**Domain:** CI/CD, pytest unit testing, Docker Registry, automated deployment
**Confidence:** HIGH

## Summary

Phase 3 baut eine vollautomatische Deployment-Pipeline: GitHub Actions baut ein Docker-Image, pusht es in die GitHub Container Registry (ghcr.io), und ein auf dem Produktionsserver laufender Watchtower-Container erkennt das neue Image und deployed es ohne manuellen Eingriff. Parallel dazu werden pytest-Unit-Tests fuer alle Formatierungsfunktionen eingefuehrt, die als CI-Gate vor dem Deployment laufen.

**Wichtige Erkenntnis zum Ist-Zustand:** Der Produktionsserver (185.248.143.234) laeuft noch mit der alten docker-compose.yml — Phase-1-Aenderungen (Umgebungsvariablen statt hardcoded Tokens, neues Org-Schema) sind noch nicht deployed. Phase 3 muss als ersten Schritt das Server-Setup auf den aktuellen Stand bringen und gleichzeitig auf Pull-from-Registry umstellen.

**Portainer-Einschraenkung:** Kein Portainer auf dem App-Server (185.248.143.234). Portainer existiert nur auf server.godsapp.de (213.109.162.132). Watchtower ist die einfachste Alternative fuer automatisches Image-Update auf dem App-Server.

**Primary recommendation:** GitHub Actions → ghcr.io → Watchtower auf App-Server. Kein Portainer auf App-Server erforderlich.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TEST-01 | Unit-Tests fuer alle Formatierungsfunktionen (Datum, Zeit, Gottesdienst-Typ, Pastor-Titel) | pytest mit @pytest.mark.parametrize; formatting.py ist isoliert testbar ohne Flask-Kontext |
| TEST-02 | Test-Fixture mit echtem Boyens-Referenz-Output als Goldstandard | Textdatei als Fixture, Vergleich mit tatsaechlichem Output; Goldstandard-Datei muss vom Nutzer bereitgestellt oder aus bestehendem Output erstellt werden |
| DEPLOY-01 | GitHub Actions Workflow: Build Docker Image und Push zu Container Registry | docker/build-push-action@v5 + docker/login-action fuer ghcr.io; GITHUB_TOKEN reicht fuer Authentication |
| DEPLOY-02 | Automatisches Deployment auf Portainer (kein manueller Server-Build mehr) | Kein Portainer auf App-Server — Watchtower als Ersatz; Watchtower pollt ghcr.io und deployed automatisch |
| DEPLOY-03 | Git Push → Image Build → Portainer Update als vollautomatische Pipeline | GitHub Actions (Build+Push) + Watchtower (Auto-Pull) ergibt vollautomatische Pipeline ohne manuellen SSH |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 8.x (aktuell 8.3.x) | Unit-Testing Framework | Standard in Python-Ecosystem; parametrize, fixtures, conftest out-of-the-box |
| docker/build-push-action | v6 | GitHub Actions: Docker-Build und Push | Offizieller Docker-Action fuer GitHub Actions |
| docker/login-action | v3 | GitHub Actions: Registry-Authentifizierung | Offizieller Login-Action; unterstuetzt ghcr.io nativ |
| docker/metadata-action | v5 | GitHub Actions: Tags und Labels generieren | Automatische tag-Generierung (sha, latest, branch) |
| containrrr/watchtower | latest | Auto-Deploy bei neuem Image auf Registry | Leichtgewichtig; pollt Registry ohne Portainer-Abhaengigkeit |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| actions/checkout | v4 | GitHub Actions: Repository auschecken | Pflicht in jedem Workflow |
| ghcr.io | — | Container Registry | Kostenlos fuer public + private Images im GitHub-Plan |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Watchtower | Portainer Webhook | Portainer nicht auf App-Server vorhanden; Portainer CE Webhook nur fuer Git-basierte Stacks (nicht Registry-basiert); Watchtower ist simpler |
| Watchtower | SSH + docker pull im Actions-Workflow | Wuerde funktionieren, aber Watchtower entkoppelt Build von Deploy; keine SSH-Keys in GitHub Secrets noetig |
| ghcr.io | Docker Hub | ghcr.io ist im GitHub-Oekosystem integriert; GITHUB_TOKEN reicht fuer Auth ohne extra Credentials |

**Installation (lokal fuer Tests):**
```bash
pip install pytest
# In requirements.txt des Test-Runners (oder web/requirements-dev.txt)
```

**Version verification (durchgefuehrt 2026-03-22):**
```bash
pip index versions pytest  # aktuell: 8.3.5
```

## Architecture Patterns

### Recommended Project Structure
```
.github/
└── workflows/
    └── ci-cd.yml           # Build, Test, Push, (optional: notify)
web/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Gemeinsame Fixtures (z.B. Referenz-Output)
│   ├── test_formatting.py   # Unit-Tests fuer formatting.py
│   └── fixtures/
│       └── boyens_reference.txt  # Goldstandard-Output fuer TEST-02
├── formatting.py            # Zu testende Funktionen (bereits vorhanden)
├── requirements.txt         # Runtime-Deps (kein pytest hier)
└── requirements-dev.txt     # pytest + ggf. weitere Test-Deps
docker-compose.yml           # Auf Server: image: ghcr.io/... statt build: .
```

### Pattern 1: pytest mit @pytest.mark.parametrize fuer Formatierungsfunktionen
**Was:** Eine Testfunktion, viele Input/Output-Paare — jedes Paar wird als separater Testfall ausgefuehrt.
**Wann einsetzen:** Alle Formatierungsfunktionen (format_date, format_time, format_service_type, format_pastor) — jede hat mehrere bekannte Input/Output-Paare aus der Boyens-Vorgabe.
**Beispiel:**
```python
# web/tests/test_formatting.py
import pytest
from datetime import datetime
from formatting import format_date, format_time, format_service_type, format_pastor

@pytest.mark.parametrize("date_obj, expected", [
    (datetime(2025, 4, 5, 0, 0), "Sonnabend, 5. April"),
    (datetime(2025, 4, 6, 0, 0), "Sonntag, 6. April"),
    (datetime(2025, 12, 25, 0, 0), "Donnerstag, 25. Dezember"),
    (datetime(2025, 5, 3, 0, 0), "Sonnabend, 3. Mai"),
])
def test_format_date(date_obj, expected):
    assert format_date(date_obj) == expected

@pytest.mark.parametrize("hour, minute, expected", [
    (9, 30, "9.30 Uhr"),
    (17, 0, "17 Uhr"),
    (10, 0, "10 Uhr"),
    (15, 30, "15.30 Uhr"),
])
def test_format_time(hour, minute, expected):
    dt = datetime(2025, 1, 1, hour, minute)
    assert format_time(dt) == expected

@pytest.mark.parametrize("titel, expected", [
    ("Gottesdienst", "Gd."),
    ("Abendmahlsgottesdienst", "Gd. m. A."),
    ("Taufgottesdienst", "Gd. m. T."),
    ("Gottesdienst mit Abendmahl und Taufe", "Abendmahlgd. m. T."),
    ("Konfirmation", "Konfirmation"),
    ("Konfirmandenprüfung", "Gd. m. Konfirmandenprüfung"),
    ("Familiengottesdienst", "Familiengd."),
    ("Gottesdienst mit Popularmusik", "Gd. m. Popularmusik"),
])
def test_format_service_type(titel, expected):
    assert format_service_type(titel) == expected

@pytest.mark.parametrize("contributor, expected", [
    ("Pastor Müller", "P. Müller"),
    ("Pastorin Schmidt", "Pn. Schmidt"),
    ("Diakon Weber", "Diakon Weber"),
    ("Pastor Müller & Pastorin Schmidt", "P. Müller, Pn. Schmidt"),
    ("", ""),
])
def test_format_pastor(contributor, expected):
    assert format_pastor(contributor) == expected
```

### Pattern 2: GitHub Actions Workflow (Build → Test → Push)
**Was:** Bei Push auf main: Tests laufen, bei Erfolg Image bauen und in ghcr.io pushen.
**Wann einsetzen:** Hauptbranch-Pipeline.
**Beispiel:**
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install test dependencies
        run: pip install -r web/requirements-dev.txt
      - name: Run tests
        run: pytest web/tests/ -v

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=raw,value=latest
            type=sha
      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: ./web
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

### Pattern 3: Watchtower fuer Auto-Deploy
**Was:** Watchtower-Container laeuft auf dem App-Server, pollt ghcr.io auf neue Images und startet den Applikations-Container neu wenn ein neues Image verfuegbar ist.
**Wann einsetzen:** Auf dem App-Server anstelle von Portainer Webhook (kein Portainer vorhanden).

**docker-compose.yml auf dem Server (nach Migration):**
```yaml
version: '3.8'

services:
  gottesdienst-formatter:
    image: ghcr.io/OWNER/REPO:latest
    container_name: gottesdienst-formatter
    ports:
      - "5001:5000"
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=false
      - SECRET_KEY=${SECRET_KEY}
      - CHURCHDESK_ORG_IDS=${CHURCHDESK_ORG_IDS}
      # ... weitere Org-Vars

  watchtower:
    image: containrrr/watchtower
    container_name: watchtower-gd
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_POLL_INTERVAL=300        # Alle 5 Minuten pruefen
      - WATCHTOWER_CLEANUP=true             # Alte Images loeschen
      - WATCHTOWER_INCLUDE_STOPPED=false
    restart: unless-stopped
```

**Wichtig fuer private ghcr.io Images:** Watchtower benoetigt Docker-Login-Credentials fuer private Registries. Entweder:
1. Image auf `public` stellen (einfacher, kein Secret noetig) — empfohlen fuer dieses Projekt
2. Oder `.docker/config.json` mit Credentials in den Watchtower-Container mounten

### Anti-Patterns to Avoid
- **`build: .` in Produktions-Compose:** Baut bei jedem `docker compose up` aus Quellcode — kein automatisches Update moeglich, haengt vom lokalen State ab
- **Hardcoded API-Tokens in docker-compose.yml:** Bereits als Problem identifiziert (State.md) — die Server-Version muss gleichzeitig mit der Pipeline-Migration bereinigt werden
- **pytest direkt in requirements.txt:** Test-Dependencies gehoeren in `requirements-dev.txt`, nicht in das Produktions-Image
- **Tests ohne conftest.py:** Gemeinsame Fixtures muessen in conftest.py, sonst Duplizierung zwischen Testdateien

## Don't Hand-Roll

| Problem | Nicht Selbst Bauen | Stattdessen | Warum |
|---------|-------------------|-------------|-------|
| Docker Registry Login in Actions | Eigenes Login-Skript | docker/login-action@v3 | Credential-Handling, Token-Rotation, Multi-Registry |
| Image-Tag-Generierung | Manuelle SHA-Extraktion | docker/metadata-action@v5 | Konventionen (sha, latest, branch) automatisch |
| Container-Update bei neuem Image | Eigenes Poll-Skript | Watchtower | Signal-Handling, Cleanup, Restart-Policy beibehalten |
| Test-Discovery und -Ausfuehrung | Eigenes Test-Runner-Skript | pytest | Parametrize, Fixtures, Exit-Codes fuer CI |

## Runtime State Inventory

> Dieser Abschnitt ist relevant, weil Phase 3 eine Migration des Deployment-Setups auf dem Produktionsserver beinhaltet.

| Kategorie | Gefundenes | Erforderliche Aktion |
|-----------|-----------|----------------------|
| Gespeicherte Daten | `./uploads/` Volume auf Server (`/opt/gottesdienst-formatter/web/uploads/`) | Beibehalten beim Umstieg auf `image:`-basierte Compose; Volume-Pfad unveraendert |
| Live-Service-Konfiguration | Server-seitige docker-compose.yml hat **alten Stand** (hardcoded Token, falsches Env-Var-Schema) | Muss manuell durch neue Version ersetzt werden; einmalig manueller Schritt erforderlich |
| OS-registrierter State | Keine systemd-Units, keine Cron-Jobs fuer den Container gefunden | Keine Aktion |
| Secrets/Env-Vars | `.env`-Datei auf Server: unbekannt, ob vorhanden; docker-compose nutzt Fallback-Werte mit altem Token | `.env` auf Server mit neuem Schema anlegen (CHURCHDESK_ORG_IDS etc.) vor erstem Auto-Deploy |
| Build-Artefakte | `web-gottesdienst-formatter` Local-Image auf Server (gebaut aus Quellcode) | Wird durch ghcr.io-Image ersetzt; altes Image nach Migration loeschen |

**Kritisch:** Die Umstellung von `build: .` auf `image: ghcr.io/...` erfordert einen einmaligen manuellen Server-Schritt (neue docker-compose.yml einspielen, .env aktualisieren, `docker compose up -d`). Danach uebernimmt Watchtower alle folgenden Updates automatisch.

## Common Pitfalls

### Pitfall 1: format_time erwartet datetime-Objekt — pd.NaT vs. None
**Was schieflaeuft:** `format_time` und `format_date` pruefen auf `pd.isna()`. In Tests arbeitet man mit echten `datetime`-Objekten — `pd.isna(datetime(...))` gibt False zurueck. Problem entsteht wenn Tests None oder NaT uebergeben ohne pandas zu importieren.
**Warum:** formatting.py importiert pandas; Tests muessen pandas ebenfalls verfuegbar haben oder NaT-Tests explizit mit `pd.NaT` schreiben.
**Vermeidung:** In requirements-dev.txt pandas und pytest listen. NaT-Tests mit `import pandas as pd; pd.NaT` schreiben.

### Pitfall 2: Watchtower und private ghcr.io-Images
**Was schieflaeuft:** Watchtower kann keine privaten Images von ghcr.io pullen ohne Credentials. Container startet, aber Updates werden nicht gezogen.
**Warum:** ghcr.io benoetigt Authentication auch fuer Pull bei privaten Packages.
**Vermeidung:** Entweder Package auf `public` setzen (GitHub Package Settings → Change visibility) oder Docker-Credentials in Watchtower konfigurieren. Empfehlung: public machen — App ist Open Source und enthaelt keine Secrets.
**Warnsignal:** Watchtower-Logs zeigen `401 Unauthorized` beim Pull.

### Pitfall 3: Alter docker-compose.yml-Stand auf Server blockiert korrekte Env-Vars
**Was schieflaeuft:** Nach Deploy via Watchtower laeuft das neue Image, aber die ENV-Vars auf dem Server entsprechen dem alten Schema (CHURCHDESK_API_TOKEN statt CHURCHDESK_ORG_IDS etc.) — neue Config-Logik bricht.
**Warum:** Watchtower ersetzt nur das Image, nicht die Compose-Datei.
**Vermeidung:** Neue docker-compose.yml und .env muss VOR dem ersten automatischen Deploy auf den Server geschrieben werden. Einmaliger manueller Schritt.

### Pitfall 4: GitHub Package Repository-Verknuepfung fuer ghcr.io
**Was schieflaeuft:** Image wird unter falschem Namen oder im falschen Namespace gepusht; Watchtower zieht falsches/kein Image.
**Warum:** `IMAGE_NAME: ${{ github.repository }}` ergibt `owner/repo` in Kleinbuchstaben — ghcr.io URL muss exakt dem entsprechen was Watchtower konfiguriert hat.
**Vermeidung:** `IMAGE_NAME` lowercase erzwingen via `${{ github.repository_owner }}/${{ github.event.repository.name }}` und `env: LOWERCASE_IMAGE_NAME: ${{ env.IMAGE_NAME }}` mit `tr '[:upper:]' '[:lower:]'`.

### Pitfall 5: pytest findet formatting.py nicht (ImportError)
**Was schieflaeuft:** Tests schlagen mit `ModuleNotFoundError: No module named 'formatting'` fehl.
**Warum:** `web/tests/test_formatting.py` importiert `from formatting import ...` — Python sucht `formatting` im sys.path, aber das web/-Verzeichnis ist nicht automatisch darin.
**Vermeidung:** `conftest.py` im `web/`-Verzeichnis mit `sys.path.insert(0, os.path.dirname(__file__))` oder Tests von `web/` aus starten: `pytest web/tests/` mit `cd web && pytest tests/`. Alternativ: `pyproject.toml` mit `[tool.pytest.ini_options] pythonpath = ["."]` im web/-Verzeichnis.

## Code Examples

### conftest.py mit sys.path-Fix
```python
# web/tests/conftest.py
import os
import sys

# Damit 'from formatting import ...' funktioniert
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
```

### pyproject.toml fuer pytest im web/-Verzeichnis
```toml
# web/pyproject.toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

### Watchtower mit ghcr.io Credentials (falls private)
```yaml
# Nur noetig wenn Image private bleibt
watchtower:
  image: containrrr/watchtower
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
    - /root/.docker/config.json:/config.json:ro
  environment:
    - DOCKER_CONFIG=/config.json
```

### Image lowercase erzwingen in GitHub Actions
```yaml
- name: Set lowercase image name
  run: echo "IMAGE_LC=${IMAGE_NAME,,}" >> $GITHUB_ENV
  env:
    IMAGE_NAME: ${{ github.repository }}
```

## State of the Art

| Alter Ansatz | Aktueller Ansatz | Seit Wann | Auswirkung |
|--------------|------------------|-----------|------------|
| `docker compose build` auf Server | Image aus Registry ziehen | ~2022 | Kein Quellcode auf Produktionsserver noetig |
| Manueller `docker pull` nach Build | Watchtower / Portainer Webhook | ~2021 | Deployment ohne SSH-Zugriff |
| Docker Hub als Default-Registry | ghcr.io fuer GitHub-Projekte | 2020 (GA) | Kein separates Account-Management; GITHUB_TOKEN reicht |
| `actions/checkout@v2` | `actions/checkout@v4` | 2023 | Performance, Node 20 |

**Deprecated/outdated:**
- `docker-compose` (V1, Python): Ersetzt durch `docker compose` (V2, Go Plugin) — Server hat bereits V2 (`Docker Compose version v5.0.2`)
- `version: '3.8'` in docker-compose.yml: Wird ignoriert in Compose V2, schadet aber nicht

## Open Questions

1. **Goldstandard-Fixture fuer TEST-02**
   - Was wir wissen: Es gibt echten Boyens-Output aus dem Produktionsbetrieb (z.B. `gottesdienste_formatiert.txt` im Projektroot)
   - Was unklar ist: Ob dieser Output 1:1 der Vorgabe entspricht (Phase-2-Ziel war das herzustellen) — und ob der Test einen festen Zeitraum oder dynamische Daten testet
   - Empfehlung: Fixture als statischen Input-Output-Testfall definieren (feste Excel-Daten → erwarteter Fließtext); kein Live-API-Aufruf in Tests

2. **Watchtower Poll-Intervall vs. Deployment-Latenz**
   - Was wir wissen: Standard-Intervall ist 24h; 300 Sekunden (5min) ist konfigurierbar
   - Was unklar ist: Wie schnell soll nach einem Push deployed sein?
   - Empfehlung: 300 Sekunden (5 Minuten) fuer Produktionsbetrieb; reicht fuer die Nutzungsfrequenz des Projekts

3. **Einmaliger manueller Server-Schritt**
   - Was wir wissen: Server-seitige docker-compose.yml muss von `build: .` auf `image: ghcr.io/...` umgestellt werden; .env muss aktualisiert werden
   - Was unklar ist: Ob alle ENV-Vars (CHURCHDESK_ORG_*) auf dem Server bereits vorhanden sind oder neu gesetzt werden muessen
   - Empfehlung: Als expliziten Task in PLAN.md aufnehmen — einmaliger SSH-Zugriff, danach nie wieder noetig

## Sources

### Primary (HIGH confidence)
- [GitHub Docs: Publishing Docker images](https://docs.github.com/en/actions/publishing-packages/publishing-docker-images) — vollstaendiger Workflow, GITHUB_TOKEN Auth, Permissions
- [Portainer Docs: Stack Webhooks](https://docs.portainer.io/user/docker/stacks/webhooks) — Webhook nur BE; CE braucht API oder Alternative
- [Portainer Blog: Pull Latest Image in CE](https://www.portainer.io/blog/pull-latest-image-feature-in-ce) — Feature ab v2.15.1 auch in CE
- Server-SSH-Pruefung (2026-03-22) — kein Portainer auf 185.248.143.234 bestaetigt; docker-compose.yml-Stand verifiziert

### Secondary (MEDIUM confidence)
- [containrrr/watchtower GitHub](https://github.com/containrrr/watchtower) — offizielles Repo, Konfigurationsoptionen
- [JuliusFreudenberger/portainer-stack-git-redeploy-action](https://github.com/JuliusFreudenberger/portainer-stack-git-redeploy-action) — CE-kompatibler Portainer-API-Action (Fallback falls Watchtower nicht gewuenscht)
- [GitHub GHCR Dokumentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry) — Pricing, Visibility, Auth

### Tertiary (LOW confidence)
- WebSearch-Ergebnis zu Watchtower + GitHub Actions Pattern — mehrere Blog-Posts bestaetigen das Pattern; nicht offiziell dokumentiert aber weitverbreitet

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — offiziell dokumentiert, auf Server verifiziert
- Architecture: HIGH — Watchtower + ghcr.io + pytest ist bewiesenes Pattern; Portainer-Einschraenkung durch SSH-Check verifiziert
- Pitfalls: MEDIUM — basierend auf Dokumentation und bekannten Eigenheiten; pytest-Import-Pitfall ist spezifisch fuer diese Projektstruktur

**Research date:** 2026-03-22
**Valid until:** 2026-09-22 (stabiles Oekosystem; Actions-Versionen koennen sich aendern)
