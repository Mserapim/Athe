import { Component, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiAuthCurrentUserService } from 'api/auth/api-auth-current-user.service';
import { apiFolhaPontoIgnorarBatida } from 'api/folha-ponto/api-folha-ponto-ignorar-batida.service';
import {
    ApiRhPvfClockingLastBeatsItem,
    apiRhPvfClockingLastBeats,
} from 'api/rh/api-rh-pvf-clocking-last-beats.service';
import { apiRhPvfClockingRegister } from 'api/rh/api-rh-pvf-clocking-registers.service';
import { VdfFolhaPontoMarcacaoEditarComponent } from '../vdf-folha-ponto/vdf-folha-ponto-marcacao-editar/vdf-folha-ponto-marcacao-editar.component';
import { MatDialog } from '@angular/material/dialog';
import { apiFolhaPontoMarcacoes, ApiFolhaPontoMarcacoesItem } from 'api/folha-ponto/api-folha-ponto-marcacoes.service';

@Component({
    selector: 'app-clocking',
    templateUrl: './clocking.component.html',
    standalone: false
})
export class ClockingComponent implements OnInit {
    lastBeats: ApiFolhaPontoMarcacoesItem;
    time: string = new Date().toLocaleTimeString('pt-BR', {
        timeZone: 'America/Cuiaba',
    });
    messageSuccess: string = '';
    messageFail: string = '';
    showAfastamentoMensagem: boolean = false;
    permitirPonto: boolean = false;
    afastamento: string = '';
    public isLoading = false;

    constructor(public dialog: MatDialog) { }

    ngOnInit() {
        this.checkAfastamento();
        setInterval(() => {
            this.time = new Date().toLocaleTimeString('pt-BR', {
                timeZone: 'America/Cuiaba',
            });
        }, 1000);
        this.loadLastBeat();
    }

    ngAfterViewInit() {}

    async checkAfastamento() {
        try {
            const currentUser = await apiAuthCurrentUserService({});
            this.afastamento = currentUser.afastamento_ativo;
            const temAfastamento = !!this.afastamento;
            this.showAfastamentoMensagem = temAfastamento;
            if (!temAfastamento) {
                this.permitirPonto = true;
            }
        } catch (error) {
            console.error('Erro ao verificar afastamento:', error);
        }
    }

    handleRespostaUsuario(allow: boolean) {
        if (allow) {
            this.showAfastamentoMensagem = false;
            this.permitirPonto = true;
        }
        if (!allow) {
            this.showAfastamentoMensagem = false;
        }
    }

    async loadLastBeat() {

        try {
            const hoje = new Date().toLocaleString('en-CA', { timeZone: 'America/Cuiaba' }).split(',')[0]
            const filtros = {
                inicio: hoje,
                fim: hoje,
            };
            const { data } = await apiFolhaPontoMarcacoes(filtros);
            this.lastBeats = data.results[0];
        } catch (e) {
            console.error(e?.response?.data?.message);
        }
        
    }

    async register() {
        this.isLoading = true;
        this.messageSuccess = '';
        this.messageFail = '';
        try {
            const {} = await apiRhPvfClockingRegister({});
            this.loadLastBeat();
            this.messageSuccess = 'Ponto registrado com sucesso';
        } catch (e) {
            console.log('ENTROU', e);
            this.messageFail = e?.response?.data?.message;
        } finally {
            this.isLoading = false;
        }
    }

    get canRegisterInput() {
        if (!this.lastBeats || !this.lastBeats.marcacoes) return true;
        const marcacoesValidas = this.lastBeats.marcacoes.filter(m => m.marcacao_valida);
        return marcacoesValidas.length === 0 || marcacoesValidas.length % 2 === 0;
    }
    

    get canRegisterOutput() {
        return !this.canRegisterInput;
    }

    protected async ignorarBatida($event, marcacao: any) {
        const checked = $event.checked;
        const marcacao_id = marcacao.pk;

        try {
            this.messageSuccess = '';
            const { resposta } = await apiFolhaPontoIgnorarBatida({
                marcacao_id,
            });
            this.messageSuccess = resposta;
            this.loadLastBeat();
        } catch (e: any) {
            console.log(e);
            const detalheErro =
                e?.response?.data?.resposta ||
                'Ocorreu um erro inesperado ao salvar o valor.';
            const texto = `${detalheErro}`;
            alert(texto);
        }
    }

    public editarBatidas(): void {
        const dialogRef = this.dialog.open(VdfFolhaPontoMarcacaoEditarComponent, {
            width: '600px',
            data: {
                marcacao: this.lastBeats,
            }
        });

        dialogRef.afterClosed().subscribe((result) => {
            this.loadLastBeat();
        });
    }
}
