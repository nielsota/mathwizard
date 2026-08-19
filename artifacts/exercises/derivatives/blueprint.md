# Blueprint: derivatives

**Type:** expand existing (vertical)
**Date:** 2026-07-19

## Diagnosis

The existing collection (`p1`–`p10`) is a solid **mechanics ladder**: every exercise is
"Bepaal de afgeleide van de volgende functies." across power / product / quotient / chain
rules, trig, exp/log and tangent — difficulty 1→5. That's good coverage of *computing* a
derivative.

The gap versus real exams: exam derivative questions almost never say "differentiate this."
They **apply** the derivative — tangent lines, extrema (`toppen`) via \(f'=0\), monotonicity,
rate of change, and derivatives inside families/proofs, always **exact** and often with
`Bewijs dat…` / `Toon aan…`. None of `p1`–`p10` exercise that.

So this expansion keeps the mechanics rungs as-is and adds an **application ladder**
(`p11`–`p20`) that climbs from single applications toward the exam anchors.

## Competencies

Existing (covered by p1–p10):
- machtsregel, productregel, quotiëntregel, kettingregel
- afgeleiden van goniometrische, exponentiële en logaritmische functies

New (targeted by p11–p20):
- raaklijn opstellen (afgeleide als helling → lijnvergelijking)
- extrema / toppen bepalen via \(f'(x)=0\), exacte x-coördinaten
- monotonie / stijgen–dalen via tekenschema van \(f'\)
- afgeleide als momentane snelheid / veranderingssnelheid in context
- afgeleide binnen een functiefamilie + bewijs (`Bewijs dat…` / `Toon aan…`)

## Exam anchors

| Exam question ID | Competencies exercised | Notes |
|---|---|---|
| VW-1025-a-18-2-o-q5 | raaklijn aan \(f(x)=x^2\) in \(P(p,p^2)\), exact, oppervlakte-bewijs | figure-based; tangent-line + proof |
| VW-1025-a-18-1-o-q4 | toppen van \(f(x)=6\sin x-\cos 2x\) via \(f'=0\), exacte x-coördinaten | trig extrema, kettingregel |
| VW-1025-a-19-1-o-q2 | "Toon aan met behulp van de afgeleide"; \(f(x)=3\cos 2x-\sqrt{2x}\), toppen | ketting + wortel; toppen aantonen |
| VW-1025-a-18-1-o-q2 | afgeleide van \(xe^{ax}\) (product+ketting), top op een lijn, familie, bewijs | families crossover, exp-derivative |
| VW-1025-a-18-1-o-q1 | exacte snelheid (momentane veranderingssnelheid) | rate-of-change flavour (parametric context) |

*(User may paste additional anchors here.)*

## Difficulty ladder

| Rung | Focus | Competencies | Builds toward |
|---|---|---|---|
| 1 | single-skill mechanics | machtsregel | — |
| 2 | mechanics + one application skill | ketting/product; raaklijn opstellen | VW-1025-a-18-2-o-q5 |
| 3 | two skills combined; extrema/monotonie | \(f'=0\), tekenschema | VW-1025-a-18-1-o-q4 |
| 4 | multi-step, exact + short justification, context | trig/exp extrema, snelheid, families | VW-1025-a-19-1-o-q2, VW-1025-a-18-1-o-q2 |
| 5 | exam-style: multiple competencies, exact + bewijs, calc-restricted | raaklijn+oppervlakte / volledig toppenonderzoek | VW-1025-a-18-2-o-q5, VW-1025-a-18-1-o-q4 |

## Planned exercises

| Proposed id | Status | Difficulty | Competency | builds_toward | calculator | Description |
|---|---|---|---|---|---|---|
| p1 | existing | 1 | machtsregel | — | false | Machtsfuncties |
| p2 | existing | 2 | product/quotiënt, gonio | — | false | Goniometrische functies I |
| p3 | existing | 2 | kettingregel, macht | — | false | Kettingregel I |
| p4 | existing | 3 | ketting + gonio | — | false | Goniometrische functies II |
| p5 | existing | 3 | quotiënt + ketting | — | false | Quotiëntregel |
| p6 | existing | 2 | exp/log | — | false | Exponentiële en logaritmische functies |
| p7 | existing | 3 | ketting (gonio/exp/log) | — | false | Kettingregel II |
| p8 | existing | 3 | tangens | — | false | Tangens en cotangens |
| p9 | existing | 4 | gemengd | — | false | Gemengde opgaven I |
| p10 | existing | 5 | gemengd | — | false | Gemengde opgaven II |
| p11 | new | 2 | raaklijn opstellen (polynoom) | VW-1025-a-18-2-o-q5 | false | Raaklijn aan grafiek in gegeven punt; lijnvergelijking |
| p12 | new | 3 | raaklijn exact, snijpunt as | VW-1025-a-18-2-o-q5 | false | Raaklijn aan \(f(x)=x^2\) in \(P(p,p^2)\); snijpunt x-as |
| p13 | new | 3 | extrema via \(f'=0\) | VW-1025-a-18-1-o-q4 | false | Toppen van polynoom/rationale functie bepalen en classificeren |
| p14 | new | 3 | monotonie / tekenschema | VW-1025-a-18-1-o-q4 | false | Stijgen/dalen bepalen via tekenschema van \(f'\) |
| p15 | new | 4 | extrema gonio, exact | VW-1025-a-18-1-o-q4, VW-1025-a-19-1-o-q2 | false | Exacte toppen van een goniometrische functie via \(f'=0\) |
| p16 | new | 4 | afgeleide ketting+wortel, toon aan | VW-1025-a-19-1-o-q2 | false | \(f(x)=3\cos 2x-\sqrt{2x}\)-type; top aantonen met afgeleide |
| p17 | new | 4 | veranderingssnelheid in context | VW-1025-a-18-1-o-q1 | false | Momentane snelheid als afgeleide; exact in context |
| p18 | new | 4 | familie, afgeleide \(xe^{ax}\), bewijs | VW-1025-a-18-1-o-q2 | false | Top van \(f_a\) op een vaste lijn; bewijs |
| p19 | new | 5 | raaklijn + oppervlakte + bewijs | VW-1025-a-18-2-o-q5 | false | Exam-style: raaklijn, snijpunten, oppervlakteverhouding bewijzen |
| p20 | new | 5 | volledig toppenonderzoek, exact + bewijs | VW-1025-a-18-1-o-q4, VW-1025-a-18-1-o-q2 | false | Exam-style: alle toppen exact + eigenschap bewijzen |

**Summary:** 10 existing kept, **10 new** (`p11`–`p20`) added — doubling the topic and
adding the missing tangent-line / extrema / monotonicity / rate-of-change / family-proof
application ladder anchored to 5 exam questions.
