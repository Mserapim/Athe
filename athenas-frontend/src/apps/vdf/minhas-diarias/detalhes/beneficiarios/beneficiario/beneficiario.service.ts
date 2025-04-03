import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class BeneficiarioService {
  private beneficiarioId = new BehaviorSubject<number | null>(null);
  beneficiarioIdAtual = this.beneficiarioId.asObservable();

  constructor() {}

  atualizarBeneficiarioId(id: number) {
    this.beneficiarioId.next(id);
  }

  limparBeneficiarioId() {
    this.beneficiarioId.next(null);
  }
}