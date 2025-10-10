# International High-Speed Rail Operators

This document summarizes the research conducted to identify international high-speed rail operators available through the Navitia SNCF API.

## Research Date
October 10, 2025

## Objective
Investigate whether TGV Lyria, Frecciarossa, and Eurostar trains are available in the Navitia API, and identify which routes they serve.

---

## Findings Summary

### ✅ TGV Lyria (France-Switzerland)
**Status**: **FOUND**
- **Commercial Mode**: `TGV Lyria`
- **Physical Mode**: `Train grande vitesse` (High-speed train)
- **Network**: `TGV Lyria`
- **Total Trains Found**: 203 trains across international routes

**Sample Train**: Train 9761

**Confirmed Routes**:
- Paris Gare de Lyon → Geneva (Genève)
- Paris Gare de Lyon → Lausanne
- Paris Gare de Lyon → Zurich (Zürich)
- Paris Gare de Lyon → Basel (Bâle)
- Lyon Part-Dieu → Geneva
- Lyon Part-Dieu → Lausanne
- Lyon Part-Dieu → Zurich
- Lyon Part-Dieu → Basel

**Station IDs in Navitia**:
- Geneva: `stop_area:SNCF:85010082`
- Lausanne: `stop_area:SNCF:85011205`
- Zurich: `stop_area:SNCF:85030007`
- Basel: `stop_area:SNCF:85000109` or `stop_area:SNCF:87473108`

---

### ❌ Frecciarossa (France-Italy)
**Status**: **NOT FOUND**
- Searched Paris → Milan, Lyon → Milan, Paris → Turin routes
- No Frecciarossa trains found in Navitia SNCF coverage
- Possible reasons:
  - Service may not have launched yet as of API data date
  - Coverage limited to French domestic and select international routes
  - Trenitalia services may appear under different branding in France

---

### ✅ Eurostar (France-UK)
**Status**: **FOUND**
- **Commercial Mode**: `Eurostar`
- **Physical Mode**: `Train grande vitesse` (High-speed train)
- **Network**: `Eurostar`

**Sample Train**: Train 9007

**Confirmed Routes**:
- Paris Gare du Nord → London St Pancras

**Station IDs in Navitia**:
- Paris Gare du Nord: `stop_area:SNCF:87271007`
- London St Pancras: `stop_area:SNCF:70154005`

---

## All Providers Discovered Across International Routes

During the comprehensive search of international routes (Paris/Lyon to Swiss and Italian cities), we discovered the following operators:

1. **REGIONAURA** - 694 trains (Regional service in Auvergne-Rhône-Alpes)
2. **TGV INOUI** - 355 trains (Standard SNCF high-speed service)
3. **TGV Lyria** - 203 trains (France-Switzerland high-speed)
4. **LEX** - 72 trains (Léman Express, Geneva-area regional)
5. **RER** - 57 trains (Parisian suburban rail)
6. **BreizhGo** - 37 trains (Brittany regional service)
7. **OUIGO** - 24 trains (Low-cost SNCF high-speed)
8. **TRANSILIEN** - 22 trains (Paris suburban rail)
9. **FLUO** - 17 trains (Grand Est regional service)
10. **MOBIGO** - 15 trains (Burgundy-Franche-Comté regional)
11. **OUIGO Train Classique** - 9 trains (Low-cost conventional trains)
12. **Aléop** - 3 trains (Loire Valley regional)
13. **DB SNCF** - 1 train (Germany-France high-speed)
14. **Intercités de nuit** - 1 train (Overnight intercity service)

---

## Implementation in TGV Times Dashboard

### Provider Filter Updated
The dashboard now includes the following high-speed providers in the filter dropdown:

1. **All** (Default - shows all high-speed trains)
2. **TGV INOUI** - Standard SNCF service
3. **OUIGO** - Low-cost SNCF option
4. **TGV Lyria** - France-Switzerland service ✨ NEW
5. **Eurostar** - France-UK service ✨ NEW
6. **DB SNCF** - Germany-France service
7. **Trenitalia** - Italian high-speed trains (not yet found in API)
8. **Renfe** - Spanish high-speed trains (not yet found in API)

### New Stations Added
The following international stations have been added to `stations.json`:

**France:**
- Paris Gare de l'Est (to Metz)
- Metz
- Paris Gare du Nord (to London)

**International:**
- London St Pancras (UK) 🇬🇧

Each station now includes a `country` field (`FR` for France, `GB` for UK).

### Feature Enhancements

1. **French Stations Only for Departure**: The departure station dropdown now only shows French stations, preventing users from selecting international stations as origin points.

2. **Sort Options**: Added the ability to sort results by:
   - Departure Time (default)
   - Arrival Time

---

## Technical Notes

### Station ID Patterns
- **French stations (SNCF)**: `stop_area:SNCF:XXXXXXXX`
- **Swiss stations (in Navitia)**: `stop_area:SNCF:XXXXXXXX` (mapped to SNCF coverage)
- **UK stations**: `stop_area:SNCF:XXXXXXXX` (Eurostar terminals in SNCF coverage)

### API Coverage Limitations
The Navitia SNCF API appears to have limited coverage for:
- Italian destinations (Milan, Turin)
- Spanish destinations
- German destinations (some DB ICE routes may be included via DB SNCF partnership)

### Physical Mode Detection
The filter uses `physical_mode` to identify high-speed trains:
- French: `"Train grande vitesse"`
- English: `"high speed"`

This approach automatically includes any high-speed operator without needing to explicitly list brand names.

---

## Search Methodology

### Scripts Used
1. **`search_international_operators.py`**: Main search script that tested 28 route combinations between Paris/Lyon and Swiss/Italian cities
2. **`check_eurostar.py`**: Specific script to verify Eurostar availability
3. **`get_station_ids.py`**: Utility to find Navitia station IDs for international cities

### Routes Tested
- Paris Gare de Lyon ↔ Geneva, Lausanne, Zurich, Basel, Milan, Turin
- Lyon Part-Dieu ↔ Geneva, Lausanne, Zurich, Basel, Milan, Turin
- Paris Gare du Nord → London St Pancras

---

## Future Considerations

1. **Frecciarossa Monitoring**: Keep checking for Frecciarossa availability as the Paris-Milan service may be added to Navitia coverage in the future.

2. **Additional Swiss Routes**: Consider adding more Swiss cities like Bern, Lucerne, or Brig which may also be served by TGV Lyria.

3. **Belgian Routes**: Investigate Thalys/Eurostar routes to Brussels, which may be available in the API.

4. **German Routes**: Check for TGV/ICE services to German cities like Frankfurt, Stuttgart, or Munich via DB SNCF partnership.

5. **Spanish Routes**: Monitor for Renfe-SNCF cooperation routes (Barcelona-Paris, Madrid-Paris).

---

## Conclusion

The Navitia SNCF API successfully provides data for:
- ✅ TGV Lyria (Switzerland)
- ✅ Eurostar (United Kingdom)
- ❌ Frecciarossa (Italy) - Not yet available

The TGV Times dashboard has been updated to support these international operators with proper filtering, station management, and country-based restrictions.
