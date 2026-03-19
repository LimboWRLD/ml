import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {forkJoin, map, Observable} from 'rxjs';
import {Landfill} from '../models/landfill.model';
import * as Papa from 'papaparse';

interface CsvRow {
  latitude: string;
  longitude: string;
  'prosecna ukupna kolicina otpada'?: string;
  'naziv'?: string;
}

@Injectable({
  providedIn: 'root'
})
export class MapService {
  private apiUrl = 'http://localhost:8080/api/landfill';

  constructor(private http: HttpClient) {}

  getAllLandfills(): Observable<Landfill[]> {
    return this.http.get<Landfill[]>(this.apiUrl);
  }


  private loadCsv(path: string): Observable<CsvRow[]> {
    return this.http.get(`assets/${path}`, { responseType: 'text' }).pipe(
      map(text => Papa.parse(text, { header: true }).data as CsvRow[])
    );
  }

  getAllLandfillsFromCSV(): Observable<
    { lat: number; lng: number; type: string; count: number; avgTotalWaste?: number; naziv?: string }[]
  > {
    return forkJoin([
      this.loadCsv('sanitarne-deponije-utf.csv').pipe(
        map(rows => this.groupByLatLng(rows, 'Sanitarna deponija'))
      ),
      this.loadCsv('nesanitarne-deponije-utf.csv').pipe(
        map(rows => this.groupByLatLng(rows, 'Nesanitarna deponija'))
      ),
      this.loadCsv('divlje-deponije-utf.csv').pipe(
        map(rows => this.groupByLatLng(rows, 'Divlja deponija'))
      ),
    ]).pipe(
      map(([san, nesan, div]) => [...san, ...nesan, ...div])
    );
  }

  private groupByLatLng(rows: CsvRow[], type: string) {
    const grouped = new Map<string, { lat:number; lng:number; type:string; count:number; avgTotalWaste?: number; naziv: string }>();

    rows.forEach(r => {
      const lat = +r.latitude;
      const lng = +r.longitude;
      if (isNaN(lat) || isNaN(lng)) return;

      const key = `${lat},${lng}`;
      const avgTotalWaste = r['prosecna ukupna kolicina otpada'] ? +r['prosecna ukupna kolicina otpada'] : undefined;
      const naziv = r.naziv || '';
      if (!grouped.has(key)) {
        grouped.set(key, { lat, lng, type, count: 0, avgTotalWaste, naziv });
      }

      grouped.get(key)!.count++;
    });
    return Array.from(grouped.values());
  }

}

