# Route Maps in StreamField

## Overview

Content editors can add interactive route maps to any page using a StreamField block. Routes are calculated using open source routing services and displayed on OpenStreetMap.

## Use Cases

| Content Type | Example |
|--------------|---------|
| Event | Meeting point → destination route |
| News Article | Ride report with GPS track |
| Tour Guide | Multi-day itinerary |
| Club Info | How to reach us |

---

## RouteBlock (StreamField)

### Block Fields

| Field | Type | Description |
|-------|------|-------------|
| Title | Text | Route name (e.g., "Percorso Giro delle Langhe") |
| Description | Text | Optional route description |
| Waypoints | Repeater | List of route points |
| Route Type | Choice | Car, Motorcycle, Bicycle, Walking |
| Show Elevation | Boolean | Display elevation profile |
| Map Height | Choice | Small (300px), Medium (400px), Large (500px) |

### Waypoint Fields

| Field | Type | Description |
|-------|------|-------------|
| Name | Text | Point label (e.g., "Start", "Coffee Stop") |
| Address | Text | Address for geocoding |
| Coordinates | Text | Lat, Long (auto-filled from address) |
| Icon | Choice | Start, End, Waypoint, POI, Food, Fuel |

### Waypoint Input Methods

| Method | Description |
|--------|-------------|
| Address Search | Type address, Nominatim geocodes it |
| Coordinates | Paste lat/long directly |
| Map Click | Click on preview map to set point |
| GPX Import | Upload GPX file to extract waypoints |

---

## Routing Services

### OSRM (Primary)

| Feature | Description |
|---------|-------------|
| Service | Open Source Routing Machine |
| API | `router.project-osrm.org` (demo) or self-hosted |
| Profiles | car, bike, foot |
| Output | GeoJSON geometry + distance/duration |
| Cost | Free (open source) |

### OpenRouteService (Alternative)

| Feature | Description |
|---------|-------------|
| Service | openrouteservice.org |
| API | Free tier: 2000 req/day |
| Profiles | driving-car, cycling-regular, foot-walking |
| Extra | Elevation data, avoid areas, isochrones |
| Cost | Free tier available |

### GraphHopper (Alternative)

| Feature | Description |
|---------|-------------|
| Service | graphhopper.com |
| API | Free tier: 500 req/day |
| Profiles | Multiple vehicle types |
| Extra | Route optimization |

---

## Map Display

### Map Provider

| Component | Technology |
|-----------|------------|
| Base Map | OpenStreetMap tiles |
| Library | Leaflet.js |
| Geocoding | Nominatim |
| Routing | OSRM / OpenRouteService |

### Visual Elements

| Element | Description |
|---------|-------------|
| Route Line | Colored polyline on map |
| Markers | Icons at each waypoint |
| Popups | Waypoint name on click |
| Start/End | Distinct icons (green flag/checkered flag) |

### Route Info Panel

| Display | Source |
|---------|--------|
| Total Distance | Calculated from route |
| Estimated Time | Based on profile speed |
| Waypoint List | Clickable, centers map |
| Elevation Chart | If enabled, shows profile |

---

## GPX Support

### Import

| Feature | Description |
|---------|-------------|
| Upload | Accept .gpx files |
| Parse | Extract track points |
| Simplify | Reduce points for performance |
| Preview | Show on map before saving |

### Export

| Feature | Description |
|---------|-------------|
| Download | GPX file of displayed route |
| Format | Standard GPX 1.1 |
| Includes | Waypoints + track |

---

## Multiple Routes

A page can have multiple RouteBlocks:

| Example | Routes |
|---------|--------|
| Multi-day tour | Day 1, Day 2, Day 3 routes |
| Event options | Short route, Long route |
| Alternative paths | Main road, Scenic route |

Each route displays on its own map or combined on one map (toggle option).

---

## Admin Configuration

### Site Settings → Maps

| Setting | Type | Description |
|---------|------|-------------|
| Routing Service | Dropdown | OSRM, OpenRouteService, GraphHopper |
| API Key | Text | For services requiring auth |
| Default Profile | Dropdown | Car, Motorcycle, Bicycle, Walking |
| Cache Routes | Boolean | Store calculated routes |
| Max Waypoints | Number | Limit per route (default: 25) |

### Route Colors

| Setting | Description |
|---------|-------------|
| Primary Route | Main route color |
| Alternative | Alternative route color |
| Completed | Passed waypoints color |

---

## Performance

| Optimization | Description |
|--------------|-------------|
| Route Caching | Store geometry after first calculation |
| Lazy Loading | Load map only when visible |
| Point Simplification | Reduce GPX points for display |
| Tile Caching | Browser caches map tiles |

---

## Elevation Profile

When enabled, shows:

| Element | Description |
|---------|-------------|
| Chart | Line graph below map |
| X-axis | Distance (km) |
| Y-axis | Elevation (m) |
| Hover | Shows elevation at point |
| Sync | Highlights position on map |

Elevation data from:
- OpenRouteService (included in API)
- Open-Elevation (open source alternative)

---

## Mobile Experience

| Feature | Description |
|---------|-------------|
| Responsive | Map adjusts to screen |
| Touch | Pinch zoom, swipe pan |
| Full Screen | Expand map button |
| Navigation | "Open in Maps" link |

### External Navigation Links

| Provider | URL Format |
|----------|------------|
| OpenStreetMap | `openstreetmap.org/directions` |
| OsmAnd | `osmand.net/go` |
| Google Maps | `maps.google.com/dir` (optional) |

---

## Schema.org

RouteBlock generates TouristTrip or Place schema:

| Property | Source |
|----------|--------|
| @type | "TouristTrip" or "Route" |
| name | Route title |
| description | Route description |
| touristType | Route type |
| itinerary | Waypoints as ItemList |

---

## Example Usage

### Event with Route

1. Create EventDetailPage
2. Add RouteBlock to body StreamField
3. Set waypoints: Meeting Point → Destination
4. Choose "Motorcycle" profile
5. Enable elevation profile
6. Save and publish

### Multi-Stop Tour

1. Create ContentPage for tour
2. Add multiple RouteBlocks (Day 1, Day 2...)
3. Import GPX from GPS device
4. Add descriptions and photos between routes

---

## Related Documentation

| Doc | Topic |
|-----|-------|
| [13-NEWS-EVENTS.md](13-NEWS-EVENTS.md) | Event pages |
| [20-STREAMFIELD-BLOCKS.md](20-STREAMFIELD-BLOCKS.md) | All blocks |
| [86-FAVORITE-EVENTS.md](86-FAVORITE-EVENTS.md) | Event favorites with map |
