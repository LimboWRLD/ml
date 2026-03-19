import { Routes } from '@angular/router';
import {MapComponent} from './features/map/map.component';
import {AwarenessComponent} from './features/awareness/awareness.component';

export const routes: Routes = [
  { path: '', component: MapComponent },
  { path: 'info', component: AwarenessComponent }
];
