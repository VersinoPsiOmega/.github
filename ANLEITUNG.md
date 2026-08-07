# GitHub-Org-Landingpage für VersinoPsiOmega

Die „Landingpage" einer GitHub-Organisation ist das **Profil-README**: die Datei
`profile/README.md` in einem öffentlichen Repo namens `.github`. Ihr Inhalt
erscheint oben auf https://github.com/VersinoPsiOmega.

## Was hier liegt

```
profile/README.md            die Landingpage
profile/assets/hero-*.svg    animierter Hero (dark + light), generiert
profile/assets/cortex-*.webp Cortex-Visual (aus semvec-design-system)
scripts/generate_hero.py     erzeugt die beiden Hero-SVGs
scripts/preview.py           baut build/preview.html zur lokalen Kontrolle
```

Hero neu erzeugen und ansehen:

```bash
python3 scripts/generate_hero.py
python3 scripts/preview.py     # -> build/preview.html im Browser öffnen
```

## Der Hero

Ein Konzept: **Konvergenz.** 46 Faserpfade in drei Tiefenebenen strömen von
links herein und laufen in einem Ember-Kern zusammen — dem Zustandsvektor. Nach
rechts verlässt ihn eine gleichmäßig getaktete Linie: konstanter Output, egal
was hineinging. Hinter der Typografie löst eine Lichtung die Fasern auf, damit
der Text ruhig sitzt.

Drei Entscheidungen, die es aus der Vorlagen-Ecke holen:

- **Die Wortmarke ist Vektor-Geometrie, keine Schrift.** Der ANSI-Shadow-Banner
  wird zellweise geparst: `█` wird ein Rechteck, die Box-Zeichen werden
  Schattenkanten. Damit sieht der Retro-Banner auf jedem Rechner identisch aus,
  statt von der Monospace-Schrift des Betrachters abzuhängen.
- **Der Endzustand ist der Default.** Keine Animation nutzt `animation-delay`
  mit unsichtbarem Startzustand; gestaffelt wird über unterschiedliche
  *Dauern*. Läuft die Animation nicht (Screenshot-Bots, Social-Media-Previews,
  gedrosselte Clients), zeigt die Seite trotzdem das fertige Bild statt einer
  leeren Fläche. `prefers-reduced-motion` friert alles auf denselben Zustand ein.
- **Zwei Themes.** `<picture>` mit `prefers-color-scheme` liefert die dunkle
  oder helle Fassung passend zur GitHub-Einstellung des Betrachters.

Beim Ändern zu beachten: Ein `linearGradient` in `objectBoundingBox`-Einheiten
verschwindet auf einer exakt horizontalen Linie (Bounding-Box-Höhe 0). Die
Exit-Linie nutzt deshalb `gradientUnits="userSpaceOnUse"`.

## Schritt 1 — Veröffentlichen

Das Repo `VersinoPsiOmega/.github` existiert bereits und ist als `origin`
eingerichtet. Der Branch dieses Worktrees enthält die fertige Seite:

```bash
git push origin HEAD:main
```

Danach ist die Seite sofort live. Prüfen: https://github.com/VersinoPsiOmega

> Falls die Bilder nicht erscheinen: GitHub cached über den camo-Proxy. Ein
> harter Reload oder ein paar Minuten Wartezeit lösen das.

## Schritt 2 (optional) — Marketing-Spot einbetten

Es gibt zwei fertige Videos:

| Datei | Größe |
|---|---|
| `/mnt/c/dev/Semvec_Marketing/08_assets/semvec-spot/out/semvec-spot.mp4` | 16 MB |
| `/mnt/c/dev/coding/semvec_webseite/Semvec_&_Semvec_Cortex.mp4` | 15 MB |

GitHub rendert Videos im README **nur**, wenn sie per Drag & Drop im
Web-Editor hochgeladen werden — dabei entsteht eine
`github.com/user-attachments/…`-URL mit Player. Ein im Repo committetes `.mp4`
bekommt keinen Player. Deshalb sind die Videos hier bewusst nicht eingecheckt.

So geht es:

1. `profile/README.md` auf github.com im Editor öffnen
2. Video an die gewünschte Stelle ziehen (Empfehlung: unter „Multi-agent memory
   that does not drift", anstelle des Standbilds)
3. Commit

Überlegung dazu: Der Hero bewegt sich bereits. Ein zweites bewegtes Element
konkurriert um dieselbe Aufmerksamkeit. Wenn der Spot rein soll, ist er stärker
*statt* des Cortex-Standbilds als zusätzlich dazu.

## Schritt 3 (optional) — Org-Seite abrunden

- **Pinned Repositories:** beide öffentlichen Repos anpinnen.
- **Org-Beschreibung** (Settings → Profile), Vorschlag:
  `Constant-cost semantic memory for LLM agents · pip install semvec`
- Website-Feld ist bereits gesetzt (semvec.io) ✓

## Redaktionelle Grundlage

Die Seite folgt den Voice-Regeln aus `Semvec_Marketing/02_brand/`:

- Jede Zahl steht **mit ihrer Messbedingung** (LOCOMO-Konfiguration, Modell,
  T = 0, Cat-5-Caveat).
- Die Benchmark-Zahlen stammen aus dem aktuellen Produkt-README
  (`semvec_rust_refactor/README.md`, Stand 0.6.x): F1 0.495, Rang 2/8, ~12 pp
  über mem0 unter deren Judge-Prompt, 17× Wall-Clock, ~93 % weniger
  Input-Tokens. Die älteren Zahlen aus den Messaging-Pillars (LOCOMO-J 0.597
  vs. 0.669) wurden bewusst **nicht** verwendet, damit die Seite dem aktuellen
  README nicht widerspricht.
- „Patent applications pending", nie „patented". Org-Name immer
  „Versino PsiOmega GmbH". Keine Kundennamen. Keine Links auf private Repos.
- Zahlen statt Adjektive; keine Hype-Sprache.
- Offen ausgewiesen, was nicht gemessen wurde: gegen Letta und LangChain Memory
  gibt es keine Head-to-Head-Zahlen, und das steht auch so da.
