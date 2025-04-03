import { Injectable } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';


@Injectable({
    providedIn: 'root'
  })
  export class VerDiariaService {
    public etapasAprovador: number[] = [];
    
    private viagemIdSource = new BehaviorSubject<number | null>(null);
    private fluxoViagemSource = new BehaviorSubject<string | null>(null);
    private etapaSolicitacaoSource = new BehaviorSubject<string | null>(null);
    private situacaoSolicitacaoSource = new BehaviorSubject<string | null>(null);
    private dataInicioSource = new BehaviorSubject<Date | null>(null);
    private dataFimSource = new BehaviorSubject<Date | null>(null);
    private telaAprovadorSource = new BehaviorSubject<boolean | null>(null);
    private telaChefeImediatoSource = new BehaviorSubject<boolean | null>(null);
    private excedenteSource = new BehaviorSubject<boolean | null>(null);
    private possuiExcedenteSource = new BehaviorSubject<boolean | null>(null);
    private finalidadeAcompanhamentoSource = new BehaviorSubject<boolean | null>(null);
    private refreshSubject = new Subject<void>();

    viagemId$ = this.viagemIdSource.asObservable();
    fluxoViagem$ = this.fluxoViagemSource.asObservable();
    situacaoSolicitacao$ = this.situacaoSolicitacaoSource.asObservable();
    etapaSolicitacao$ = this.etapaSolicitacaoSource.asObservable();
    dataInicio$ = this.dataInicioSource.asObservable();
    dataFim$ = this.dataFimSource.asObservable();
    telaAprovador$ = this.telaAprovadorSource.asObservable();
    telaChefeImediato$ = this.telaChefeImediatoSource.asObservable();
    excedente$ = this.excedenteSource.asObservable();
    possuiExcedente$ = this.excedenteSource.asObservable();
    finalidadeAcompanhamento$ = this.excedenteSource.asObservable();
    public refresh$ = this.refreshSubject.asObservable();
  
    constructor() {}
  
    get viagemId(): number | null {
      return this.viagemIdSource.value;
    }
  
    set viagemId(id: number | null) {
      this.viagemIdSource.next(id);
    }

    get fluxoViagem(): string | null {
      return this.fluxoViagemSource.value;
    }
  
    set fluxoViagem(fluxo: string | null) {
      this.fluxoViagemSource.next(fluxo);
    }

    get situacaoSolicitacao(): string | null {
      return this.situacaoSolicitacaoSource.value;
    }

    set situacaoSolicitacao(situacao: string | null) {
        this.situacaoSolicitacaoSource.next(situacao);
    }

    get etapaSolicitacao(): string | null {
        return this.etapaSolicitacaoSource.value;
    }

    set etapaSolicitacao(etapa: string | null) {
        this.etapaSolicitacaoSource.next(etapa);
    }
    
    get dataInicio(): Date | null {
      return this.dataInicioSource.value;
    }

    set dataInicio(data: Date | null) {
        this.dataInicioSource.next(data);
    }

    get dataFim(): Date | null {
        return this.dataFimSource.value;
    }

    set dataFim(data: Date | null) {
        this.dataFimSource.next(data);
    }

    get telaAprovador(): boolean | null {
        return this.telaAprovadorSource.value;
    }

    set telaAprovador(value: boolean | null) {
        this.telaAprovadorSource.next(value);
    }

    get telaChefeImediato(): boolean | null {
      return this.telaChefeImediatoSource.value;
    }

    set telaChefeImediato(value: boolean | null) {
      this.telaChefeImediatoSource.next(value);
    }

    get excedente(): boolean | null {
      return this.excedenteSource.value;
    }

    set excedente(value: boolean | null) {
        this.excedenteSource.next(value);
    }

    get possuiExcedente(): boolean | null {
      return this.possuiExcedenteSource.value;
    }

    set possuiExcedente(value: boolean | null) {
        this.possuiExcedenteSource.next(value);
    }

    get finalidadeAcompanhamento(): boolean | null {
      return this.finalidadeAcompanhamentoSource.value;
    }

    set finalidadeAcompanhamento(value: boolean | null) {
        this.finalidadeAcompanhamentoSource.next(value);
    }

    refreshResumoBeneficiarios() {
      this.refreshSubject.next();
    }

    clearServiceData() {
      this.viagemIdSource.next(null);
      this.fluxoViagemSource.next(null);
      this.situacaoSolicitacaoSource.next(null);
      this.etapaSolicitacaoSource.next(null);
      this.dataInicioSource.next(null);
      this.dataFimSource.next(null);
      this.telaAprovadorSource.next(null);
      this.telaChefeImediatoSource.next(null);
      this.excedenteSource.next(null);
      this.possuiExcedenteSource.next(null);
      this.finalidadeAcompanhamentoSource.next(null);
    }
  
}