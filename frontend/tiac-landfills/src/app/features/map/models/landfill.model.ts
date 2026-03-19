export enum LandfillStatus {
  Divlja = 1,
  JavnaNesanitarna = 2,
  Sanitarna = 3
}

export interface Landfill {
  id: number;
  landfillId: string;
  status: LandfillStatus;
  location: {
    lat: number;
    lng: number;
  };
  areaM2?: number;
  volumeM3?: number;
  wasteMassTons?: number;
  startYear?: number;
  methaneTonsPerYear?: number;
  co2eqTonsPerYear?: number;
  createdAt: string;
}
