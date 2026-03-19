import { AfterViewInit, Component } from '@angular/core';
import mapboxgl from 'mapbox-gl';
import { MapService } from './services/map.service';
import { Landfill, LandfillStatus } from './models/landfill.model';
import {FeatureCollection, Feature ,Point} from 'geojson';
import {NgClass, NgForOf, NgIf, NgStyle} from '@angular/common';
import {catchError, count, of} from 'rxjs';
import {FormsModule} from '@angular/forms';

@Component({
  selector: 'app-map',
  standalone: true,
  templateUrl: './map.component.html',
  styleUrls: ['./map.component.css'],
  providers: [MapService],
  imports: [
    NgClass,
    NgForOf,
    FormsModule,
    NgStyle,
    NgIf
  ]
})
export class MapComponent implements AfterViewInit {
  private map!: mapboxgl.Map;

  sanitarnaVisible = true;
  nesanitarnaVisible = true;
  divljaVisible = true;
  private allLandfills: Array<{ lat: number; lng: number; type: string; naziv?: string; props?: any }> = [];
  private selectedMarker: mapboxgl.Marker | null = null;
  private IMPACT_RADIUS_METERS = 2000;
  years: number[] = [];
  selectedYear: string = '';
  heatVisible = false;
  controlsVisible = false;



  constructor(private mapService: MapService) {
  //  (mapboxgl as any).accessToken = this.mapboxAccessToken;
    const currentYear = new Date().getFullYear();
    this.years = Array.from({ length: 50 }, (_, i) => currentYear - i);
  }

  ngAfterViewInit(): void {
    this.initMap();
  }

  private initMap(): void {
    this.map = new mapboxgl.Map({
      container: 'map',
      style: 'mapbox://styles/mapbox/satellite-streets-v11',
      center: [20.4569, 44.8176],
      zoom: 7,
    });

    this.map.addControl(new mapboxgl.NavigationControl());


    this.map.on('load', () => {
      this.loadLandfills();
      this.loadLandfillsFromCSV()
    });

    this.map.on('click', (e: any) => {
      const features = this.map.queryRenderedFeatures(e.point, {
        layers: ['sanitarne-points','nesanitarne-points','divlje-unclustered','backend-divlje-unclustered', 'divlje-clusters', 'divlje-cluster-count']
      });

      if (features && features.length > 0) {
        return;
      }

      const lng = e.lngLat.lng;
      const lat = e.lngLat.lat;
      this.analyzeLocation(lat, lng);
    });
  }

  private loadLandfillsFromCSV(): void {
    const loadCsvDivlje = true;
    this.mapService.getAllLandfillsFromCSV().subscribe((items) => {
      const sanitarneFeatures: Feature<Point, { type: string; count: number }>[] = [];
      const nesanitarneFeatures: Feature<Point, { type: string; count: number }>[] = [];
      const divljeFeatures: Feature<Point, { type: string; count: number }>[] = [];

      items.forEach(i => {
        const t = (i.type || '').toString().trim();
        const roundedWaste = i.avgTotalWaste !== undefined ? Math.round(i.avgTotalWaste) : undefined;
        const feat: Feature<Point, { type: string; count: number; avgTotalWaste?: number; naziv?: string }> = {
          type: 'Feature',
          properties: { type: t, count: i.count, avgTotalWaste: roundedWaste, naziv: i.naziv },
          geometry: { type: 'Point', coordinates: [i.lng, i.lat] }
        };
        this.allLandfills.push({ lat: i.lat, lng: i.lng, type: t, naziv: i.naziv, props: { count: i.count, avgTotalWaste: roundedWaste } });

        if (t.includes('Sanitarna')) sanitarneFeatures.push(feat);
        else if (t.includes('Nesanitarna')) nesanitarneFeatures.push(feat);
        else if (t.includes('Divlja')) divljeFeatures.push(feat);
      });

      const safeRemove = (id: string) => {
        if (this.map.getLayer(id)) this.map.removeLayer(id);
        if (this.map.getSource(id)) this.map.removeSource(id);
      };

      safeRemove('sanitarne-points');
      this.map.addSource('landfills-sanitarne', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: sanitarneFeatures
        } as GeoJSON.FeatureCollection
      } as any);

      this.map.addLayer({
        id: 'sanitarne-points',
        type: 'circle',
        source: 'landfills-sanitarne',
        paint: {
          'circle-radius': 6,
          'circle-color': 'blue'
        }
      });

      safeRemove('nesanitarne-points');
      this.map.addSource('landfills-nesanitarne', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: nesanitarneFeatures
        } as GeoJSON.FeatureCollection
      } as any);

      this.map.addLayer({
        id: 'nesanitarne-points',
        type: 'circle',
        source: 'landfills-nesanitarne',
        paint: {
          'circle-radius': 6,
          'circle-color': 'orange'
        }
      });

      if (loadCsvDivlje) {
        ['divlje-clusters', 'divlje-cluster-count', 'divlje-unclustered'].forEach(id => {
          if (this.map.getLayer(id)) this.map.removeLayer(id);
        });
        if (this.map.getSource('landfills-divlje')) this.map.removeSource('landfills-divlje');

        this.map.addSource('landfills-divlje', {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: divljeFeatures
          } as GeoJSON.FeatureCollection,
          cluster: true,
          clusterMaxZoom: 13,
          clusterRadius: 40
        } as any);

        this.map.addLayer({
          id: 'divlje-clusters',
          type: 'circle',
          source: 'landfills-divlje',
          filter: ['has', 'point_count'],
          paint: {
            'circle-radius': 22,
            'circle-color': 'red'
          }
        });

        this.map.addLayer({
          id: 'divlje-cluster-count',
          type: 'symbol',
          source: 'landfills-divlje',
          filter: ['has', 'point_count'],
          layout: {
            'text-field': '{point_count_abbreviated}',
            'text-size': 12
          }
        });

        this.map.addLayer({
          id: 'divlje-unclustered',
          type: 'circle',
          source: 'landfills-divlje',
          filter: ['!', ['has', 'point_count']],
          paint: {
            'circle-radius': 6,
            'circle-color': 'red'
          }
        });

        this.map.on('click', 'divlje-clusters', (e: any) => {
          const features = this.map.queryRenderedFeatures(e.point, {layers: ['divlje-clusters']});
          if (!features.length) return;

          const clusterId = features[0].properties?.['cluster_id'];
          if (clusterId === undefined) return;

          const geom = features[0].geometry as Point;
          const coordsArr = geom.coordinates;
          if (coordsArr.length < 2) return;

          const coords: [number, number] = [coordsArr[0], coordsArr[1]];

          const src = this.map.getSource('landfills-divlje') as any;
          src.getClusterExpansionZoom(clusterId, (err: any, zoom: number) => {
            if (err) return;
            this.map.easeTo({center: coords, zoom});
          });
        });
      }
      const showPopup = (coords: number[], props: any) => {
        new mapboxgl.Popup()
          .setLngLat(coords as [number, number])
          .setHTML(`
          <b>${props.type} - ${props.naziv}</b><br>
          Prosečna količina otpada: ${props.avgTotalWaste ?? 'N/A'} t<br>
          Godina nastanka: ${2025 - props.count}
        `)
          .addTo(this.map);
      };

      this.map.on('click', 'divlje-unclustered', (e: any) => {
        const f = e.features[0];
        const coords = (f.geometry.coordinates as number[]).slice();
        showPopup(coords, f.properties);
      });

      this.map.on('click', 'sanitarne-points', (e: any) => {
        const f = e.features[0];
        const coords = (f.geometry.coordinates as number[]).slice();
        showPopup(coords, f.properties);
      });

      this.map.on('click', 'nesanitarne-points', (e: any) => {
        const f = e.features[0];
        const coords = (f.geometry.coordinates as number[]).slice();
        showPopup(coords, f.properties);
      });

      ['divlje-clusters', 'divlje-unclustered', 'sanitarne-points', 'nesanitarne-points'].forEach(layer => {
        this.map.on('mouseenter', layer, () => this.map.getCanvas().style.cursor = 'pointer');
        this.map.on('mouseleave', layer, () => this.map.getCanvas().style.cursor = '');
      });

      this.setVisibilityForType('sanitarna', this.sanitarnaVisible);
      this.setVisibilityForType('nesanitarna', this.nesanitarnaVisible);
      this.setVisibilityForType('divlja', this.divljaVisible);

      const allFeatures = [
        ...sanitarneFeatures,
        ...nesanitarneFeatures,
        ...divljeFeatures,
      ];

      this.map.addSource('landfills-heat-src', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: allFeatures
        } as GeoJSON.FeatureCollection
      });

      this.map.addLayer({
        id: 'landfills-heat',
        type: 'heatmap',
        source: 'landfills-heat-src',
        layout: {
          visibility: 'none'
        },
        paint: {
          'heatmap-radius': 30,
          'heatmap-intensity': 1,
          'heatmap-opacity': 0.6,
          'heatmap-weight': 1
        }
      });
    });
  }


  toggleHeat() {
    this.heatVisible = !this.heatVisible;
    this.map.setLayoutProperty('landfills-heat', 'visibility', this.heatVisible ? 'visible' : 'none');
  }

  toggleControls() {
    this.controlsVisible = !this.controlsVisible;
  }

  scrollToMap() {
    const mapSection = document.getElementById('mapSection');
    if (mapSection) {
      mapSection.scrollIntoView({ behavior: 'smooth' });
    }
  }

  private loadLandfills(): void {
    this.mapService.getAllLandfills().pipe(
      catchError(err => {
        console.warn('Backend not reachable, loading dummy data', err);

        const dummy: Landfill[] = [{
          id: 1,
          landfillId: 'DUMMY-1',
          status: LandfillStatus.Divlja,
          location: { lat: 44.819, lng: 20.458 },
          areaM2: 5000,
          volumeM3: 2000,
          wasteMassTons: 50,
          startYear: 2015,
          methaneTonsPerYear: 12,
          co2eqTonsPerYear: 20,
          createdAt: new Date().toISOString()
        }];

        return of(dummy);
      })
    ).subscribe(landfills => {
      this.renderDivljeLandfills(landfills);
    });
  }

  private renderDivljeLandfills(landfills: Landfill[]): void {
    const divljeFeatures: Feature<Point, any>[] = [];

    landfills
      .filter(lf => lf.status === LandfillStatus.Divlja)
      .forEach(lf => {
        const feat: Feature<Point, any> = {
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [lf.location.lng, lf.location.lat] },
          properties: {
            ...lf,
            location: lf.location
          }
        };
        divljeFeatures.push(feat);
        this.allLandfills.push({ lat: lf.location.lat, lng: lf.location.lng, type: 'Divlja deponija', naziv: lf.landfillId ?? undefined, props: lf });
      });

    ['backend-divlje-clusters', 'backend-divlje-cluster-count', 'backend-divlje-unclustered'].forEach(id => {
      if (this.map.getLayer(id)) this.map.removeLayer(id);
    });
    if (this.map.getSource('backend-divlje')) this.map.removeSource('backend-divlje');

    this.map.addSource('backend-divlje', {
      type: 'geojson',
      data: {
        type: 'FeatureCollection',
        features: divljeFeatures
      } as GeoJSON.FeatureCollection,
      cluster: true,
      clusterMaxZoom: 13,
      clusterRadius: 40
    } as any);

    this.map.addLayer({
      id: 'backend-divlje-clusters',
      type: 'circle',
      source: 'backend-divlje',
      filter: ['has', 'point_count'],
      paint: {
        'circle-radius': 22,
        'circle-color': 'red'
      }
    });

    this.map.addLayer({
      id: 'backend-divlje-cluster-count',
      type: 'symbol',
      source: 'backend-divlje',
      filter: ['has', 'point_count'],
      layout: {
        'text-field': '{point_count_abbreviated}',
        'text-size': 12
      }
    });

    this.map.addLayer({
      id: 'backend-divlje-unclustered',
      type: 'circle',
      source: 'backend-divlje',
      filter: ['!', ['has', 'point_count']],
      paint: {
        'circle-radius': 6,
        'circle-color': 'red'
      }
    });

    const showPopup = (coords: number[], props: Landfill) => {
      new mapboxgl.Popup()
        .setLngLat(coords as [number, number])
        .setHTML(`
      <b>${LandfillStatus[props.status]}</b><br>
      Lokacija: ${coords[1].toFixed(5)}, ${coords[0].toFixed(5)}<br>
      Površina: ${props.areaM2 ?? 'N/A'} m²<br>
      Prosečna količina otpada: ${props.wasteMassTons ?? 'N/A'} m³<br>
      Godišnja emisija metana: ${props.methaneTonsPerYear ?? 'N/A'} t<br>
      Godišnja emisija CO₂: ${props.co2eqTonsPerYear ?? 'N/A'} t
    `)
        .addTo(this.map);
    };

    this.map.on('click', 'backend-divlje-unclustered', (e: any) => {
      const f = e.features[0];
      const coords = (f.geometry.coordinates as number[]).slice();
      showPopup(coords, f.properties);
    });

    ['backend-divlje-clusters', 'backend-divlje-unclustered'].forEach(layer => {
      this.map.on('mouseenter', layer, () => this.map.getCanvas().style.cursor = 'pointer');
      this.map.on('mouseleave', layer, () => this.map.getCanvas().style.cursor = '');
    });
  }


  useMyLocation(): void {
    if (!navigator.geolocation) {
      console.warn('Geolocation is not supported by this browser.');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;

        this.map.flyTo({ center: [lng, lat], zoom: 12 });

        this.analyzeLocation(lat, lng);

      },
      (error) => {
        console.warn('Unable to retrieve location', error);
      },
      {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0,
      }
    );
  }



  onDateChange(): void {
    if (!this.selectedYear) return;
console.log('selected yaer is ' + this.selectedYear)
    if (this.map.getLayer('satellite-tiled')) {
      this.map.removeLayer('satellite-tiled');
      this.map.removeSource('satellite-tiled');
    }

  }


// FILTER DEPONIJA
  toggleType(type: 'sanitarna' | 'nesanitarna' | 'divlja') {
    if (type === 'sanitarna') {
      this.sanitarnaVisible = !this.sanitarnaVisible;
      this.setVisibilityForType('sanitarna', this.sanitarnaVisible);
    } else if (type === 'nesanitarna') {
      this.nesanitarnaVisible = !this.nesanitarnaVisible;
      this.setVisibilityForType('nesanitarna', this.nesanitarnaVisible);
    } else {
      this.divljaVisible = !this.divljaVisible;
      this.setVisibilityForType('divlja', this.divljaVisible);
    }
  }

  private setVisibilityForType(type: 'sanitarna' | 'nesanitarna' | 'divlja', visible: boolean) {
    const vis = visible ? 'visible' : 'none';

    if (type === 'sanitarna') {
      if (this.map.getLayer('sanitarne-points')) this.map.setLayoutProperty('sanitarne-points', 'visibility', vis);
    } else if (type === 'nesanitarna') {
      if (this.map.getLayer('nesanitarne-points')) this.map.setLayoutProperty('nesanitarne-points', 'visibility', vis);
    } else {
      ['divlje-clusters', 'divlje-cluster-count', 'divlje-unclustered',
        'backend-divlje-clusters', 'backend-divlje-cluster-count', 'backend-divlje-unclustered']
        .forEach(id => {
          if (this.map.getLayer(id)) this.map.setLayoutProperty(id, 'visibility', vis);
        });
    }
  }




// IZRACUNAVANJE RADIUSA OD 2KM
  private toRadius(deg: number) { return deg * Math.PI / 180; }

  private distanceMeters(lat1: number, lon1: number, lat2: number, lon2: number) {
    const R = 6371000; // Earth radius in meters
    const dLat = this.toRadius(lat2 - lat1);
    const dLon = this.toRadius(lon2 - lon1);
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(this.toRadius(lat1)) * Math.cos(this.toRadius(lat2)) *
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }

  private analyzeLocation(lat: number, lng: number) {
    if (!this.allLandfills.length) {
      this.showAnalysisResult('Nema podataka o deponijama za analizu.');
      return;
    }

    let min = Infinity;
    let nearest: any = null;
    this.allLandfills.forEach(lf => {
      const d = this.distanceMeters(lat, lng, lf.lat, lf.lng);
      if (d < min) { min = d; nearest = { ...lf, distance: d }; }
    });

    const meters = Math.round(min);
    if (meters <= this.IMPACT_RADIUS_METERS) {
      const name = nearest.naziv ?? 'Nepoznata deponija';
      const type = nearest.type ?? 'deponija';
      const msg = `PAŽNJA: Vaša lokacija je u radijusu od 2 km od deponije ${name}, koja je klasifikovana kao ${type}. Udaljenost: ${meters} m.`;
      this.showAnalysisResult(msg, lat, lng, nearest);
    } else {
      const msg = 'Vaša lokacija se ne nalazi u neposrednoj blizini mapiranih deponija.';
      this.showAnalysisResult(msg, lat, lng, null, meters);
    }
  }

  private showAnalysisResult(message: string, lat?: number, lng?: number, nearest?: any, distanceMeters?: number) {
    const el = document.getElementById('analysisResult');
    if (el) {
      el.innerHTML = `<strong>Analiza lokacije:</strong><br>${message}`;

      if (nearest && nearest.distance <= this.IMPACT_RADIUS_METERS) {
        el.style.backgroundColor = 'rgba(255, 0, 0, 0.2)';
        el.style.color = 'darkred';
      } else {
        el.style.backgroundColor = 'rgba(0, 128, 0, 0.2)';
        el.style.color = 'darkgreen';
      }
    }
    if (this.selectedMarker !== null) {
      this.selectedMarker.remove();
      this.selectedMarker = null;
    }

    if (lat !== undefined && lng !== undefined) {
      this.selectedMarker = new mapboxgl.Marker({ color: '#006400' })
        .setLngLat([lng, lat])
        .addTo(this.map);

    }

    const infoDiv = document.getElementById('info');
    if (infoDiv) infoDiv.scrollIntoView({ behavior: 'smooth' });
  }




}

