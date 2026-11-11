# Calling: Paris — saved tournament results analysis

1,418 observed named players; 1,392 with a known hero; 26 named players with source hero `N/A`. 5,181 result rows: 5,174 Swiss (rounds 1–15) and 7 elimination (rounds 16–18).

**Champion: Matt Muus (Teklovossen). Runner-up: Cody Gebert (Jarl).**

## Reading the results

- Participation counts distinct exact player names seen anywhere in the saved pages. This is an observed field, not a registration list. No conflicting heroes or duplicate player names within a round were found; exact names are not verified unique player IDs.
- Day 2 means an appearance in round 10. The 128 observed round-10 players provide an observed Day 2 cohort; qualification rules are not inferred.
- Swiss win rate = W / (W + L + D). Draws count as games without a win; a double loss is one loss for each player. Mirrors are included in the basic Swiss rate.
- Day 1 covers rounds 1–9; Day 2 covers Swiss rounds 10–15. Rounds 16–18 are eliminations and are excluded from both daily rates. Each daily rate uses only games from that day. No games means an unavailable rate, not 0%. Day 2 reflects the players who advanced, not the full original field. Daily records and non-mirror rates are shown alongside the rates.
- Confidence for overall and daily basic hero rates uses a reproducible 95% percentile bootstrap interval from 2,000 resamples of whole players. Each resampled player retains all their games in that period, and the pooled W / games ratio is recomputed. Both contributing game and player counts are shown. An interval is withheld with fewer than two players, an unknown hero, no games, or no between-player variation in the resampled ratio. Few-player intervals remain unstable; they are descriptive and conditional on this tournament cohort, not guarantees about future hero strength or comparisons between days. The CSV’s non-mirror Wilson intervals are a separate game-based approximation. Reference for percentile bootstrap construction: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html (the implementation here uses only the Python standard library).
- In player tables, Hero Swiss win rate is the pooled Swiss rate of every observed player using that hero, including the current player. It uses the same denominator and exclusions as the player rate; unknown heroes show no hero rate.
- Non-mirror win rate additionally excludes mirror matches and every match with an unknown hero. It uses Swiss rounds only, avoiding extra weight from the elimination bracket. CSV includes approximate 95% Wilson intervals; repeated games from the same player are correlated, so these intervals are descriptive, not a player-adjusted model.
- Six rows (rounds 2, 4, 6, 7, 13 and 14) record wins against the literal placeholder “Player 2” / `N/A`. These are not counted as real opponents or played matches. They remain in raw matches and in each player’s recorded Swiss wins, with a separate placeholder-wins count in players.csv. The source does not label them as byes; other unlisted byes cannot be recovered.
- The 26 named `N/A` players appear only in round 1, each with a loss. Their reason for missing hero data is not supplied. Their results are preserved in basic player/hero totals; non-mirror and matchup metrics exclude those rows. This can inflate basic rates for their opponents.
- Participation shares include the 26 unknowns in the denominator. To compare only known heroes, divide a hero’s player count by 1392.
- Player tables are sorted by recorded Swiss wins, then losses, draws and name. This is not official standings: tie-breakers, byes absent from coverage, and final Swiss ranks are unavailable. Elimination finish is taken directly from rounds 16–18.
- The source warns that coverage results are provisional relative to GEM. All figures describe these saved snapshots, not a fresh live scrape. No event date is inferred from file timestamps.

## Main findings

- Most played: Fang, Dracai of Blades (159, 11.2%), followed by Levia, Shadowborn Abomination (156) and Jarl Vetreiði (132).
- Best non-mirror Swiss rates among heroes with at least 30 observed players: Dorinthea Ironsong 58.2% (180-124-5); Ira, Scarlet Revenger 53.0% (325-286-2); Fang, Dracai of Blades 53.0% (591-518-7); Aurora, Legacy of Tempest 52.3% (415-374-4); Arakni, 5L!p3d 7hRu 7h3 cR4X 52.0% (185-170-1).
- Top 8 hero composition: Jarl Vetreiði: 3, Aurora, Legacy of Tempest: 2, Teklovossen, Esteemed Magnate: 1, Gravy Bones, Shipwrecked Looter: 1, Arakni, 5L!p3d 7hRu 7h3 cR4X: 1.
- Jarl converted 3 of 132 players to Top 8 (2.3%); Aurora converted 2 of 120 (1.7%). Fang and Levia had the two largest cohorts but neither reached Top 8.
- Dorinthea also had the highest observed Day 2 conversion among cohorts of at least 30 players: 8 of 37 (21.6%), against a field baseline of 128 / 1,418 (9.0%). None reached Top 8.
- Teklovossen won the event but posted a 44.3% non-mirror Swiss rate across 18 players. Matt Muus was its only observed Day 2 player. The champion’s result therefore differs sharply from the hero’s aggregate performance.
- Among well-represented matchups, Aurora went 81–54 against Fang (60.0%) but 23–57–2 against Jarl (28.1%). Fang went 61–32 against Ira (65.6%). Pairing mix can change a hero’s aggregate result substantially.
- These are tournament outcomes, not causal measures of hero strength: player skill, pairings and survivor selection affect the rates. Small cohorts and sparse matchups are particularly uncertain.

## Elimination results

| Player | Hero | Finish | Swiss W-L-D | Player Swiss win rate | Hero Swiss win rate | Hero Day 1 win rate | Hero Day 2 win rate | All rounds W-L-D |
|---|---|---|---|---|---|---|---|---|
| Matt Muus | Teklovossen, Esteemed Magnate | Champion | 13-1-1 | 86.7% | 44.4% | 42.2% | 83.3% | 16-1-1 |
| Cody Gebert | Jarl Vetreiði | Runner-up | 13-2-0 | 86.7% | 51.6% | 50.9% | 59.3% | 15-3-0 |
| Madeline Southwood | Jarl Vetreiði | Top 4 | 12-3-0 | 80.0% | 51.6% | 50.9% | 59.3% | 13-4-0 |
| Nicolas Lazarides | Aurora, Legacy of Tempest | Top 4 | 14-1-0 | 93.3% | 52.4% | 52.2% | 54.2% | 15-2-0 |
| Alexander Teague | Aurora, Legacy of Tempest | Top 8 | 12-3-0 | 80.0% | 52.4% | 52.2% | 54.2% | 12-4-0 |
| Jimmy Niro Demers | Gravy Bones, Shipwrecked Looter | Top 8 | 14-1-0 | 93.3% | 48.4% | 49.1% | 39.1% | 14-2-0 |
| Konrad Niva | Arakni, 5L!p3d 7hRu 7h3 cR4X | Top 8 | 12-3-0 | 80.0% | 51.9% | 51.6% | 54.3% | 12-4-0 |
| Michael Jaszczur | Jarl Vetreiði | Top 8 | 12-3-0 | 80.0% | 51.6% | 50.9% | 59.3% | 12-4-0 |

## Hero participation and performance

| Hero | Players | Field share | Day 2 | Day 2 conversion | Top 8 | Swiss W-L-D | Swiss win rate | Non-mirror win rate | Day 1 W-L-D | Day 1 win rate | Day 1 non-mirror win rate | Day 2 W-L-D | Day 2 win rate | Day 2 non-mirror win rate | Swiss 95% CI | Swiss games | Swiss contributing players | Day 1 95% CI | Day 1 games | Day 1 contributing players | Day 2 95% CI | Day 2 games | Day 2 contributing players |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fang, Dracai of Blades | 159 | 11.2% | 18 | 11.3% | 0 | 663-587-7 | 52.7% | 53.0% | 615-532-6 | 53.3% | 53.6% | 48-55-1 | 46.1% | 45.8% | 50.2%–55.2% | 1257 | 159 | 50.6%–55.8% | 1153 | 159 | 36.0%–55.7% | 104 | 18 |
| Levia, Shadowborn Abomination | 156 | 11.0% | 15 | 9.6% | 0 | 554-559-2 | 49.7% | 49.5% | 507-522-2 | 49.2% | 49.0% | 47-37-0 | 56.0% | 56.8% | 46.5%–52.8% | 1115 | 156 | 46.0%–52.1% | 1031 | 156 | 44.3%–66.3% | 84 | 15 |
| Jarl Vetreiði | 132 | 9.3% | 14 | 10.6% | 3 | 508-461-16 | 51.6% | 51.8% | 460-430-14 | 50.9% | 51.0% | 48-31-2 | 59.3% | 60.3% | 48.2%–54.7% | 985 | 132 | 47.6%–54.2% | 904 | 132 | 52.0%–66.7% | 81 | 14 |
| Aurora, Legacy of Tempest | 120 | 8.5% | 8 | 6.7% | 2 | 446-402-4 | 52.4% | 52.3% | 420-380-4 | 52.2% | 52.2% | 26-22-0 | 54.2% | 54.5% | 49.3%–55.3% | 852 | 120 | 49.1%–55.3% | 804 | 120 | 39.6%–70.8% | 48 | 8 |
| Ser Boltyn, Breaker of Dawn | 94 | 6.6% | 9 | 9.6% | 0 | 370-343-1 | 51.8% | 51.9% | 347-319-1 | 52.0% | 52.1% | 23-24-0 | 48.9% | 48.8% | 49.0%–54.8% | 714 | 94 | 48.7%–55.0% | 667 | 94 | 34.1%–62.0% | 47 | 9 |
| Gravy Bones, Shipwrecked Looter | 88 | 6.2% | 9 | 10.2% | 1 | 308-320-8 | 48.4% | 48.1% | 290-293-7 | 49.1% | 48.9% | 18-27-1 | 39.1% | 38.1% | 44.0%–52.4% | 636 | 88 | 44.5%–53.5% | 590 | 88 | 21.9%–55.6% | 46 | 9 |
| Ira, Scarlet Revenger | 84 | 5.9% | 9 | 10.7% | 0 | 343-302-2 | 53.0% | 53.0% | 323-274-2 | 53.9% | 54.0% | 20-28-0 | 41.7% | 41.7% | 49.8%–56.1% | 647 | 84 | 50.1%–57.4% | 599 | 84 | 30.2%–51.0% | 48 | 9 |
| Oscilio, Forked Continuum | 57 | 4.0% | 9 | 15.8% | 0 | 239-229-1 | 51.0% | 51.0% | 215-199-1 | 51.8% | 51.9% | 24-30-0 | 44.4% | 44.0% | 45.9%–55.5% | 469 | 57 | 46.5%–57.2% | 415 | 57 | 31.5%–57.4% | 54 | 9 |
| Arakni, 5L!p3d 7hRu 7h3 cR4X | 49 | 3.5% | 6 | 12.2% | 1 | 193-178-1 | 51.9% | 52.0% | 174-162-1 | 51.6% | 51.7% | 19-16-0 | 54.3% | 54.3% | 47.0%–56.6% | 372 | 49 | 46.6%–56.4% | 337 | 49 | 38.9%–69.4% | 35 | 6 |
| Puffin, Hightail | 43 | 3.0% | 2 | 4.7% | 0 | 138-166-4 | 44.8% | 44.5% | 133-159-4 | 44.9% | 44.6% | 5-7-0 | 41.7% | 41.7% | 39.2%–50.0% | 308 | 43 | 39.3%–50.7% | 296 | 43 | 33.3%–50.0% | 12 | 2 |
| Dorinthea Ironsong | 37 | 2.6% | 8 | 21.6% | 0 | 184-128-5 | 58.0% | 58.2% | 167-103-4 | 61.0% | 61.1% | 17-25-1 | 39.5% | 38.5% | 53.8%–61.5% | 317 | 37 | 55.6%–65.9% | 274 | 37 | 27.5%–50.0% | 43 | 8 |
| Olympia, Prized Fighter | 33 | 2.3% | 3 | 9.1% | 0 | 101-137-2 | 42.1% | 41.7% | 93-127-2 | 41.9% | 41.5% | 8-10-0 | 44.4% | 44.4% | 33.8%–49.0% | 240 | 33 | 33.8%–49.5% | 222 | 33 | 16.7%–66.7% | 18 | 3 |
| Marlynn, Treasure Hunter | 31 | 2.2% | 0 | 0.0% | 0 | 89-121-4 | 41.6% | 41.4% | 89-121-4 | 41.6% | 41.4% | 0-0-0 | — | — | 35.2%–47.3% | 214 | 31 | 35.5%–47.6% | 214 | 31 | Not estimable | 0 | 0 |
| Vynnset, Iron Maiden | 28 | 2.0% | 0 | 0.0% | 0 | 81-116-2 | 40.7% | 40.5% | 81-116-2 | 40.7% | 40.5% | 0-0-0 | — | — | 35.3%–45.8% | 199 | 28 | 35.0%–45.6% | 199 | 28 | Not estimable | 0 | 0 |
| Hala, Bladesaint of the Vow | 27 | 1.9% | 1 | 3.7% | 0 | 73-100-4 | 41.2% | 40.9% | 73-96-4 | 42.2% | 41.9% | 0-4-0 | 0.0% | 0.0% | 34.5%–47.5% | 177 | 27 | 34.2%–49.7% | 173 | 27 | Not estimable | 4 | 1 |
| Riptide, Lurker of the Deep | 27 | 1.9% | 1 | 3.7% | 0 | 84-96-1 | 46.4% | 45.9% | 80-94-1 | 45.7% | 45.2% | 4-2-0 | 66.7% | 66.7% | 38.1%–53.4% | 181 | 27 | 38.2%–52.1% | 175 | 27 | Not estimable | 6 | 1 |
| Tuffnut, Bumbling Hulkster | 27 | 1.9% | 2 | 7.4% | 0 | 73-107-1 | 40.3% | 40.1% | 70-98-1 | 41.4% | 41.3% | 3-9-0 | 25.0% | 20.0% | 33.1%–46.6% | 181 | 27 | 32.9%–49.2% | 169 | 27 | 16.7%–33.3% | 12 | 2 |
| Zyggy Starlight | 27 | 1.9% | 0 | 0.0% | 0 | 75-108-0 | 41.0% | 40.1% | 75-108-0 | 41.0% | 40.1% | 0-0-0 | — | — | 35.4%–46.2% | 183 | 27 | 35.1%–46.1% | 183 | 27 | Not estimable | 0 | 0 |
| N/A | 26 | 1.8% | 0 | 0.0% | 0 | 0-26-0 | 0.0% | — | 0-26-0 | 0.0% | — | 0-0-0 | — | — | Not estimable | 26 | 26 | Not estimable | 26 | 26 | Not estimable | 0 | 0 |
| Arakni, Huntsman | 25 | 1.8% | 2 | 8.0% | 0 | 103-86-4 | 53.4% | 53.4% | 96-81-4 | 53.0% | 53.1% | 7-5-0 | 58.3% | 58.3% | 46.3%–59.1% | 193 | 25 | 46.7%–59.0% | 181 | 25 | 50.0%–66.7% | 12 | 2 |
| Rhinar, Reckless Rampage | 24 | 1.7% | 5 | 20.8% | 0 | 119-98-1 | 54.6% | 54.2% | 105-82-1 | 55.9% | 55.4% | 14-16-0 | 46.7% | 46.4% | 48.3%–59.8% | 218 | 24 | 48.2%–62.5% | 188 | 24 | 36.7%–56.7% | 30 | 5 |
| Viserai, the Forsaken | 24 | 1.7% | 0 | 0.0% | 0 | 66-91-2 | 41.5% | 40.9% | 66-91-2 | 41.5% | 40.9% | 0-0-0 | — | — | 35.5%–47.0% | 159 | 24 | 35.8%–46.9% | 159 | 24 | Not estimable | 0 | 0 |
| Betsy, Skin in the Game | 18 | 1.3% | 3 | 16.7% | 0 | 86-63-2 | 57.0% | 56.8% | 73-58-2 | 54.9% | 54.5% | 13-5-0 | 72.2% | 75.0% | 46.4%–65.2% | 151 | 18 | 44.7%–63.5% | 133 | 18 | 66.7%–83.3% | 18 | 3 |
| Katsu, the Wanderer | 18 | 1.3% | 1 | 5.6% | 0 | 49-65-0 | 43.0% | 42.5% | 47-61-0 | 43.5% | 43.0% | 2-4-0 | 33.3% | 33.3% | 35.4%–50.0% | 114 | 18 | 35.0%–52.9% | 108 | 18 | Not estimable | 6 | 1 |
| Teklovossen, Esteemed Magnate | 18 | 1.3% | 1 | 5.6% | 1 | 48-58-2 | 44.4% | 44.3% | 43-58-1 | 42.2% | 42.0% | 5-0-1 | 83.3% | 83.3% | 30.9%–57.0% | 108 | 18 | 31.1%–53.3% | 102 | 18 | Not estimable | 6 | 1 |
| Valda, Seismic Impact | 13 | 0.9% | 0 | 0.0% | 0 | 31-53-2 | 36.0% | 36.0% | 31-53-2 | 36.0% | 36.0% | 0-0-0 | — | — | 26.2%–45.6% | 86 | 13 | 26.8%–46.0% | 86 | 13 | Not estimable | 0 | 0 |
| Kayo, Underhanded Cheat | 9 | 0.6% | 1 | 11.1% | 0 | 39-33-1 | 53.4% | 53.4% | 35-31-1 | 52.2% | 52.2% | 4-2-0 | 66.7% | 66.7% | 40.0%–63.6% | 73 | 9 | 40.4%–63.2% | 67 | 9 | Not estimable | 6 | 1 |
| Lyath Goldmane, Vile Savant | 9 | 0.6% | 1 | 11.1% | 0 | 39-35-1 | 52.0% | 52.0% | 34-34-1 | 49.3% | 49.3% | 5-1-0 | 83.3% | 83.3% | 37.7%–65.5% | 75 | 9 | 37.7%–61.7% | 69 | 9 | Not estimable | 6 | 1 |
| Malice, Domina of the Dead | 8 | 0.6% | 0 | 0.0% | 0 | 11-34-0 | 24.4% | 24.4% | 11-34-0 | 24.4% | 24.4% | 0-0-0 | — | — | 7.3%–44.2% | 45 | 8 | 7.5%–43.8% | 45 | 8 | Not estimable | 0 | 0 |
| Maxx 'The Hype' Nitro | 2 | 0.1% | 0 | 0.0% | 0 | 1-6-0 | 14.3% | 14.3% | 1-6-0 | 14.3% | 14.3% | 0-0-0 | — | — | 0.0%–25.0% | 7 | 2 | 0.0%–25.0% | 7 | 2 | Not estimable | 0 | 0 |
| Pleiades, Superstar | 2 | 0.1% | 0 | 0.0% | 0 | 1-9-0 | 10.0% | 10.0% | 1-9-0 | 10.0% | 10.0% | 0-0-0 | — | — | 0.0%–14.3% | 10 | 2 | 0.0%–14.3% | 10 | 2 | Not estimable | 0 | 0 |
| Uzuri, Switchblade | 2 | 0.1% | 0 | 0.0% | 0 | 7-8-0 | 46.7% | 46.7% | 7-8-0 | 46.7% | 46.7% | 0-0-0 | — | — | 44.4%–50.0% | 15 | 2 | 44.4%–50.0% | 15 | 2 | Not estimable | 0 | 0 |
| Bravo, Showstopper | 1 | 0.1% | 0 | 0.0% | 0 | 3-6-0 | 33.3% | 33.3% | 3-6-0 | 33.3% | 33.3% | 0-0-0 | — | — | Not estimable | 9 | 1 | Not estimable | 9 | 1 | Not estimable | 0 | 0 |

## Most-supported non-mirror matchups

Swiss only; each pairing is shown once. Opposite-direction rates need not sum to 100% because draws and double losses exist.

| Hero | Opponent | Matches | W-L-D | Win rate |
|---|---|---|---|---|
| Aurora, Legacy of Tempest | Fang, Dracai of Blades | 135 | 81-54-0 | 60.0% |
| Fang, Dracai of Blades | Jarl Vetreiði | 132 | 64-67-1 | 48.5% |
| Fang, Dracai of Blades | Levia, Shadowborn Abomination | 129 | 67-61-1 | 51.9% |
| Jarl Vetreiði | Levia, Shadowborn Abomination | 108 | 55-53-0 | 50.9% |
| Fang, Dracai of Blades | Ira, Scarlet Revenger | 93 | 61-32-0 | 65.6% |
| Aurora, Legacy of Tempest | Levia, Shadowborn Abomination | 86 | 48-38-0 | 55.8% |
| Fang, Dracai of Blades | Ser Boltyn, Breaker of Dawn | 83 | 50-33-0 | 60.2% |
| Aurora, Legacy of Tempest | Jarl Vetreiði | 82 | 23-57-2 | 28.1% |
| Levia, Shadowborn Abomination | Ser Boltyn, Breaker of Dawn | 81 | 24-57-0 | 29.6% |
| Fang, Dracai of Blades | Gravy Bones, Shipwrecked Looter | 78 | 48-30-0 | 61.5% |
| Ira, Scarlet Revenger | Jarl Vetreiði | 70 | 44-26-0 | 62.9% |
| Gravy Bones, Shipwrecked Looter | Levia, Shadowborn Abomination | 64 | 27-37-0 | 42.2% |
| Gravy Bones, Shipwrecked Looter | Jarl Vetreiði | 63 | 31-31-1 | 49.2% |
| Ira, Scarlet Revenger | Levia, Shadowborn Abomination | 63 | 32-31-0 | 50.8% |
| Aurora, Legacy of Tempest | Ser Boltyn, Breaker of Dawn | 62 | 37-25-0 | 59.7% |
| Fang, Dracai of Blades | Oscilio, Forked Continuum | 59 | 16-43-0 | 27.1% |
| Levia, Shadowborn Abomination | Oscilio, Forked Continuum | 58 | 28-30-0 | 48.3% |
| Aurora, Legacy of Tempest | Ira, Scarlet Revenger | 57 | 25-32-0 | 43.9% |
| Jarl Vetreiði | Ser Boltyn, Breaker of Dawn | 54 | 36-18-0 | 66.7% |
| Aurora, Legacy of Tempest | Gravy Bones, Shipwrecked Looter | 51 | 27-24-0 | 52.9% |

## Player results

All players and round-by-round opponents are in [players.csv](players.csv) and [player-results.csv](player-results.csv). Open [report.html](report.html) for searchable player and matchup tables. The first 40 players in the descriptive Swiss ordering are below.

| Player | Hero | Finish | Swiss W-L-D | Player Swiss win rate | Hero Swiss win rate | Hero Day 1 win rate | Hero Day 2 win rate | All rounds W-L-D |
|---|---|---|---|---|---|---|---|---|
| Jimmy Niro Demers | Gravy Bones, Shipwrecked Looter | Top 8 | 14-1-0 | 93.3% | 48.4% | 49.1% | 39.1% | 14-2-0 |
| Nicolas Lazarides | Aurora, Legacy of Tempest | Top 4 | 14-1-0 | 93.3% | 52.4% | 52.2% | 54.2% | 15-2-0 |
| Matt Muus | Teklovossen, Esteemed Magnate | Champion | 13-1-1 | 86.7% | 44.4% | 42.2% | 83.3% | 16-1-1 |
| Cody Gebert | Jarl Vetreiði | Runner-up | 13-2-0 | 86.7% | 51.6% | 50.9% | 59.3% | 15-3-0 |
| Alexander Teague | Aurora, Legacy of Tempest | Top 8 | 12-3-0 | 80.0% | 52.4% | 52.2% | 54.2% | 12-4-0 |
| Andrei Sebastian Suciu | Fang, Dracai of Blades |  | 12-3-0 | 80.0% | 52.7% | 53.3% | 46.1% | 12-3-0 |
| Benjamin Westmore | Levia, Shadowborn Abomination |  | 12-3-0 | 80.0% | 49.7% | 49.2% | 56.0% | 12-3-0 |
| David Gómez | Oscilio, Forked Continuum |  | 12-3-0 | 80.0% | 51.0% | 51.8% | 44.4% | 12-3-0 |
| David Pantoja Sánchez | Lyath Goldmane, Vile Savant |  | 12-3-0 | 80.0% | 52.0% | 49.3% | 83.3% | 12-3-0 |
| Emma Hollingsworth | Levia, Shadowborn Abomination |  | 12-3-0 | 80.0% | 49.7% | 49.2% | 56.0% | 12-3-0 |
| Gints Dreimanis | Levia, Shadowborn Abomination |  | 12-3-0 | 80.0% | 49.7% | 49.2% | 56.0% | 12-3-0 |
| Konrad Niva | Arakni, 5L!p3d 7hRu 7h3 cR4X | Top 8 | 12-3-0 | 80.0% | 51.9% | 51.6% | 54.3% | 12-4-0 |
| Madeline Southwood | Jarl Vetreiði | Top 4 | 12-3-0 | 80.0% | 51.6% | 50.9% | 59.3% | 13-4-0 |
| Matthew Dilks | Fang, Dracai of Blades |  | 12-3-0 | 80.0% | 52.7% | 53.3% | 46.1% | 12-3-0 |
| Michael Jaszczur | Jarl Vetreiði | Top 8 | 12-3-0 | 80.0% | 51.6% | 50.9% | 59.3% | 12-4-0 |
| Patrycjusz Janas | Betsy, Skin in the Game |  | 12-3-0 | 80.0% | 57.0% | 54.9% | 72.2% | 12-3-0 |
| Rik Godschalk | Ser Boltyn, Breaker of Dawn |  | 12-3-0 | 80.0% | 51.8% | 52.0% | 48.9% | 12-3-0 |
| Shahmir Samee | Levia, Shadowborn Abomination |  | 12-3-0 | 80.0% | 49.7% | 49.2% | 56.0% | 12-3-0 |
| Takahito Natsume | Ira, Scarlet Revenger |  | 12-3-0 | 80.0% | 53.0% | 53.9% | 41.7% | 12-3-0 |
| Andreas Ritzakis | Jarl Vetreiði |  | 11-3-1 | 73.3% | 51.6% | 50.9% | 59.3% | 11-3-1 |
| Florian Koksch | Jarl Vetreiði |  | 11-3-1 | 73.3% | 51.6% | 50.9% | 59.3% | 11-3-1 |
| Xavier laperrouze | Gravy Bones, Shipwrecked Looter |  | 11-3-1 | 73.3% | 48.4% | 49.1% | 39.1% | 11-3-1 |
| Aleksejs Titovs | Levia, Shadowborn Abomination |  | 11-4-0 | 73.3% | 49.7% | 49.2% | 56.0% | 11-4-0 |
| Bangliang Liu | Levia, Shadowborn Abomination |  | 11-4-0 | 73.3% | 49.7% | 49.2% | 56.0% | 11-4-0 |
| Bun Ar | Betsy, Skin in the Game |  | 11-4-0 | 73.3% | 57.0% | 54.9% | 72.2% | 11-4-0 |
| Callum Young | Fang, Dracai of Blades |  | 11-4-0 | 73.3% | 52.7% | 53.3% | 46.1% | 11-4-0 |
| Cedric SCHAACK | Ser Boltyn, Breaker of Dawn |  | 11-4-0 | 73.3% | 51.8% | 52.0% | 48.9% | 11-4-0 |
| Dave Margetson | Oscilio, Forked Continuum |  | 11-4-0 | 73.3% | 51.0% | 51.8% | 44.4% | 11-4-0 |
| Elie Champel | Dorinthea Ironsong |  | 11-4-0 | 73.3% | 58.0% | 61.0% | 39.5% | 11-4-0 |
| Enes Findik | Arakni, 5L!p3d 7hRu 7h3 cR4X |  | 11-4-0 | 73.3% | 51.9% | 51.6% | 54.3% | 11-4-0 |
| Enki Dupaquier | Fang, Dracai of Blades |  | 11-4-0 | 73.3% | 52.7% | 53.3% | 46.1% | 11-4-0 |
| Eugene C | Rhinar, Reckless Rampage |  | 11-4-0 | 73.3% | 54.6% | 55.9% | 46.7% | 11-4-0 |
| Jimmy Nguyen | Jarl Vetreiði |  | 11-4-0 | 73.3% | 51.6% | 50.9% | 59.3% | 11-4-0 |
| Juha-Matti Pihlajamäki | Fang, Dracai of Blades |  | 11-4-0 | 73.3% | 52.7% | 53.3% | 46.1% | 11-4-0 |
| Kilian Schellekens | Levia, Shadowborn Abomination |  | 11-4-0 | 73.3% | 49.7% | 49.2% | 56.0% | 11-4-0 |
| Lucas Macorano | Gravy Bones, Shipwrecked Looter |  | 11-4-0 | 73.3% | 48.4% | 49.1% | 39.1% | 11-4-0 |
| Ludovic Zgajner | Kayo, Underhanded Cheat |  | 11-4-0 | 73.3% | 53.4% | 52.2% | 66.7% | 11-4-0 |
| Lukasz Bigos | Levia, Shadowborn Abomination |  | 11-4-0 | 73.3% | 49.7% | 49.2% | 56.0% | 11-4-0 |
| Manuel González Martínez | Olympia, Prized Fighter |  | 11-4-0 | 73.3% | 42.1% | 41.9% | 44.4% | 11-4-0 |
| Marco Marcelli | Jarl Vetreiði |  | 11-4-0 | 73.3% | 51.6% | 50.9% | 59.3% | 11-4-0 |

## Round coverage

| Round | Phase | Rows | Named players | Draws | Double losses | Unknown hero rows | Placeholder rows |
|---|---|---|---|---|---|---|---|
| 1 | Swiss | 709 | 1418 | 3 | 0 | 26 | 0 |
| 2 | Swiss | 694 | 1387 | 3 | 0 | 1 | 1 |
| 3 | Swiss | 683 | 1366 | 5 | 0 | 0 | 0 |
| 4 | Swiss | 650 | 1299 | 4 | 0 | 1 | 1 |
| 5 | Swiss | 590 | 1180 | 4 | 0 | 0 | 0 |
| 6 | Swiss | 506 | 1011 | 4 | 0 | 1 | 1 |
| 7 | Swiss | 399 | 797 | 3 | 0 | 1 | 1 |
| 8 | Swiss | 317 | 634 | 5 | 0 | 0 | 0 |
| 9 | Swiss | 261 | 522 | 6 | 3 | 0 | 0 |
| 10 | Swiss | 64 | 128 | 1 | 0 | 0 | 0 |
| 11 | Swiss | 64 | 128 | 0 | 0 | 0 | 0 |
| 12 | Swiss | 63 | 126 | 1 | 0 | 0 | 0 |
| 13 | Swiss | 61 | 121 | 0 | 0 | 1 | 1 |
| 14 | Swiss | 58 | 115 | 0 | 0 | 1 | 1 |
| 15 | Swiss | 55 | 110 | 1 | 0 | 0 | 0 |
| 16 | Elimination | 4 | 8 | 0 | 0 | 0 | 0 |
| 17 | Elimination | 2 | 4 | 0 | 0 | 0 | 0 |
| 18 | Elimination | 1 | 2 | 0 | 0 | 0 | 0 |

## Reproduce and audit

Run `python -B tools/stats/analyze_saved_results.py --matches public/data/calling-paris/matches.csv --output public/data/calling-paris` from the repository root to rebuild from the included normalized data. If the original pages are available in Scraping/, omit --matches to extract them again. The script uses only the Python standard library. `audit.json` lists source filenames and SHA-256 hashes, unknown players, placeholder rows and late first appearances. `matches.csv` preserves source results and filenames; `player-results.csv` expands each named player’s individual result.
