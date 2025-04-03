import { Component, Input } from '@angular/core';
import { CdkDragDrop, moveItemInArray } from '@angular/cdk/drag-drop';

import { MpmtListagem2Coluna, MpmtListagem2Linha } from 'components/mpmt-listagem2/mpmt-listagem2.interface';
import { MpmtListagem2Component } from 'components/mpmt-listagem2/mpmt-listagem2.component';
import { BehaviorSubject, Subject, take, takeUntil } from 'rxjs';
import moment from 'moment';
import { MpmtListagemReordenavelService } from './mpmt-listagem-reordenavel.service';

@Component({
    selector: 'mpmt-listagem-reordenavel',
    templateUrl: './mpmt-listagem-reordenavel.component.html',
    standalone: false
})
export class MpmtListagemReordenavelComponent extends MpmtListagem2Component {
    @Input('service') service: MpmtListagemReordenavelService;

    dragAtivo = false;
    localData: MpmtListagem2Linha[] = [];
    backupData: MpmtListagem2Linha[];
    private destroy$ = new Subject<void>();

    ngOnInit() {
        super.ngOnInit();
        this.service.listagem$.pipe(takeUntil(this.destroy$)).subscribe(dados => {
            this.localData = dados;
        });
    }

    ngOnDestroy() {
        this.destroy$.next();
        this.destroy$.complete();
    }

    atualizarListagem() {
        this.service.paginacao.page = this.paginator.pageIndex + 1;
        this.service.paginacao.per_page = this.paginator.pageSize;
        this.service.recarregarListagem();
    }

    ativarDragMode() {
        this.dragAtivo = !this.dragAtivo;
        if (this.dragAtivo) {
            this.backupData = [...this.localData];
            this.renumerarOrdem();
            this.service.total$.pipe(
                take(1)
            ).subscribe(total => {
                this.paginator.pageSize = total;
                this.paginator.pageIndex = 0;
                this.atualizarListagem();
            });
        } else {
            this.paginator.pageSize = 10;
            this.atualizarListagem();
        }
    }

    renumerarOrdem() {
        this.localData.forEach((item, index) => {
            item.ordem = index + 1;
        });
        this.localData = [...this.localData];
    }
    
    drop(event: CdkDragDrop<any[]>) {
        const previousIndex = event.previousIndex;
        const currentIndex = event.currentIndex;
    
        if (previousIndex !== currentIndex) {
            moveItemInArray(this.localData, previousIndex, currentIndex);
            this.localData = [...this.localData];
            this.renumerarOrdem();
        }
    }

    cancelarEdicao() {
        this.dragAtivo = false;
        this.localData = this.backupData;
        this.backupData = [];
        this.service.recarregarListagem();
    }

    salvarOrdem() {
        this.service.atualizarOrdem(this.localData)
        .then(() => {
            this.dragAtivo = false;
            this.service.recarregarListagem();
        })
        .catch(error => {
            console.error("Erro ao salvar a ordem:", error);
        });
    }


    @Input('coluna') coluna: MpmtListagem2Coluna;
    @Input('linha') linha: MpmtListagem2Linha;

    private valorSubject = new BehaviorSubject<
        string | number | boolean | Date
    >(undefined);
    public valor$ = this.valorSubject.asObservable();

    ngOnChanges() {
        if (!this.coluna) return;
        if (!this.linha) return;

        this.valorSubject.next(this.contruirValor(this.coluna, this.linha));
    }

    contruirValor(coluna: MpmtListagem2Coluna, linha: MpmtListagem2Linha) {
        if (!coluna) return;
        if (!linha) return;
        const valor = this.linha[this.coluna.codigo];
        if (!this.coluna.transformarValor) return valor;
        return this.coluna.transformarValor(valor);
    }

    formatarData = (data) => moment(data).format('DD/MM/YYYY');
    formatarDataHora = (data) => moment(data).format('DD/MM/YYYY HH:MM');
    formatarBooleano = (valor: boolean) => valor ? 'Sim' : 'Não';
}

