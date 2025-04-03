import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { environment } from "environments/environment";
import { Observable } from "rxjs";

@Injectable({
    providedIn: 'root'
  })
  export class VersaoAppService {
  
    constructor(private http: HttpClient) { }
  
    consultarVersaoApp(): Observable<any> {
      let url_info_version = environment.api_endpoint + 'actuator/info';
  
      return this.http.get(url_info_version);
    }
  }