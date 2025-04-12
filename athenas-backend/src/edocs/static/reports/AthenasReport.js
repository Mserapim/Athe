/**
 *
 **/

Ext._define('edocs.reports.AthenasReport', {
    extend: 'toolkit.widget.TabPanel',

    _buildReport: function(paycheck){

        var protocolo = this.getProtocoloField().getValue();
        var chancela = this.getChancelaField().getValue();
        var criacao_inicio = Ext.util.Format.date(this.getDataCriacaoInicio().getValue(), 'Y-m-d');
        var criacao_final = Ext.util.Format.date(this.getDataCriacaoFim().getValue(), 'Y-m-d');
        var interessado = this.getInteressado().getValue().toString();
        var assunto = this.getAssuntoField().getValue();
        var resumo = this.getResumoField().getValue().toString();
        var remetente = this.getRemetente().getValue().toString();
        var envio_inicio = Ext.util.Format.date(this.getDataEnvioInicio().getValue(), 'Y-m-d');
        var envio_final = Ext.util.Format.date(this.getDataEnvioFim().getValue(), 'Y-m-d');
        var destinatario = this.getDestinatario().getValue().toString();
        var recebimento_inicio = Ext.util.Format.date(this.getDataRecebimentoInicio().getValue(), 'Y-m-d');
        var recebimento_final = Ext.util.Format.date(this.getDataRecebimentoFim().getValue(), 'Y-m-d');
        var orgao_remetente = this.getOrgaoRemetente().getValue().toString();
        var orgao_destino = this.getOrgaoDestino().getValue().toString();

        engine.mq.Report.request({
            report: '/to/mpe/protocolo/athenas/protocolo',
            waitMessage: 'Gerando relatório...',
            params: {
                outfile: 'relatorio_edoc_athenas',
                report_name: 'Relatório EDOC - Athenas',
                protocolo: protocolo != "" ? protocolo : null,
                chancela: chancela != "" ? chancela : null,
                criacao_inicio: criacao_inicio != "" ? criacao_inicio : null,
                criacao_final: criacao_final != "" ? criacao_final : null,
                interessado: interessado != "" ? interessado : null,
                assunto: assunto != "" ? assunto : null,
                resumo: resumo != "" ? resumo : null,
                remetente: remetente != "" ? remetente : null,
                envio_inicio: envio_inicio != "" ? envio_inicio : null,
                envio_final: envio_final != "" ? envio_final : null,
                destinatario: destinatario != "" ? destinatario : null,
                recebimento_inicio: recebimento_inicio != "" ? recebimento_inicio : null,
                recebimento_final: recebimento_final != "" ? recebimento_final : null,
                orgao_remetente: orgao_remetente != "" ? orgao_remetente : null,
                orgao_destino: orgao_destino != "" ? orgao_destino : null
            }

        });
    },

    getInteressado: function(){
        if(!this._especialidade)
            this._especialidade = Ext._create('core.fields.AutocompleteField', {
                name: 'interessado',
                rest: 'rh.pessoa.Restful',
                fieldLabel: 'Interessado',
                width: 350
            });

        return this._especialidade;
    },

    getRemetente: function(){
        if(!this._especialidade)
            this._especialidade = Ext._create('core.fields.AutocompleteField', {
                name: 'remetente',
                rest: 'rh.pessoa.Restful',
                fieldLabel: 'Remetente',
                width: 350
            });

        return this._especialidade;
    },

    getDestinatario: function(){
        if(!this._especialidade)
            this._especialidade = Ext._create('core.fields.AutocompleteField', {
                name: 'destinatario',
                rest: 'rh.pessoa.Restful',
                fieldLabel: 'Destinatario',
                width: 350
            });

        return this._especialidade;
    },

    getOrgaoDestino: function(){
        if(!this._orgaodestino)
            this._orgaodestino = Ext._create('core.fields.AutocompleteField', {
                name: 'orgao_destino',
                rest: 'rh.generalorgan.Restful',
                fieldLabel: 'Orgão Destino',
                width: 350
            });

        return this._orgaodestino;
    },

    getOrgaoRemetente: function(){
        if(!this._orgaoremetente)
            this._orgaoremetente = Ext._create('core.fields.AutocompleteField', {
                name: 'orgao_remetente',
                rest: 'rh.generalorgan.Restful',
                fieldLabel: 'Orgão Remetente',
                width: 350
            });

        return this._orgaoremetente;
    },

    getDataCriacaoInicio: function() {
        if (!this._datacriacaoinicio)
            this._datacriacaoinicio = Ext._create('Ext.form.DateField', {
                name: 'data_criacao_inicio',
                fieldLabel: "Data Criação Início",
                hidden: false,
                width: 350,
            });
        return this._datacriacaoinicio;
    },

    getDataCriacaoFim: function() {
        if (!this._datacriacaofim)
            this._datacriacaofim = Ext._create('Ext.form.DateField', {
                name: 'data_criacao_fim',
                fieldLabel: "Data Criação Fim",
                hidden: false,
                width: 350,
            });
        return this._datacriacaofim;
    },

    getDataEnvioInicio: function() {
        if (!this._dataenvioinicio)
            this._dataenvioinicio = Ext._create('Ext.form.DateField', {
                name: 'data_envio_inicio',
                fieldLabel: "Data Envio Início",
                hidden: false,
                width: 350,
            });
        return this._dataenvioinicio;
    },

    getDataEnvioFim: function() {
        if (!this._dataenviofim)
            this._dataenviofim = Ext._create('Ext.form.DateField', {
                name: 'data_envio_fim',
                fieldLabel: "Data Envio Fim",
                hidden: false,
                width: 350,
            });
        return this._dataenviofim;
    },

    getDataRecebimentoInicio: function() {
        if (!this._datarecebimentoinicio)
            this._datarecebimentoinicio = Ext._create('Ext.form.DateField', {
                name: 'data_recebimento_inicio',
                fieldLabel: "Data Recebimento Início",
                hidden: false,
                width: 350,
            });
        return this._datarecebimentoinicio;
    },

    getDataRecebimentoFim: function() {
        if (!this._datarecebimentofim)
            this._datarecebimentofim = Ext._create('Ext.form.DateField', {
                name: 'data_recebimento_fim',
                fieldLabel: "Data Recebimento Fim",
                hidden: false,
                width: 350,
            });
        return this._datarecebimentofim;
    },

    getProtocoloField: function(){
        if(!this._protocolofield)
            this._protocolofield = Ext._create('Ext.form.TextField', {
                name: 'protocolo',
                fieldLabel: 'Protocolo',
                width: 350
            });

        return this._protocolofield;
    },

    getChancelaField: function(){
        if(!this._chancelafield)
            this._chancelafield = Ext._create('Ext.form.TextField', {
                name: 'chancela',
                fieldLabel: 'Chancela',
                width: 350
            });

        return this._chancelafield;
    },

    getAssuntoField: function(){
        if(!this._assuntofield)
            this._assuntofield = Ext._create('Ext.form.TextField', {
                name: 'assunto',
                fieldLabel: 'Assunto',
                width: 350
            });

        return this._assuntofield;
    },

    getResumoField: function(){
        if(!this._resumofield)
            this._resumofield = Ext._create('Ext.form.TextField', {
                name: 'resumo',
                fieldLabel: 'Resumo',
                width: 350
            });

        return this._resumofield;
    },

    getMain: function(){
        if(!this._panel)
        this._panel = new Ext.Panel({
            layout: 'border',
            region: 'center',
            height: 650,
            split: true,
            autoEl: {tag: 'center'},
            items: [
            {
                // title: 'Informações do Contra-Cheque',
                region: 'center',
                border: false,
                autoScroll: true,
                items: [
                {
                    xtype: 'fieldset',
                    title: 'EDOCS -> Athenas',
                    name: 'fieldServidor',
                    width: 650,
                    style: 'margin: 5px',
                    align: 'center',
                    items:[
                        this.getProtocoloField(),
                        this.getChancelaField(),
                        this.getDataCriacaoInicio(),
                        this.getDataCriacaoFim(),
                        this.getInteressado(),
                        this.getAssuntoField(),
                        this.getResumoField(),
                        this.getOrgaoRemetente(),
                        this.getDataEnvioInicio(),
                        this.getDataEnvioFim(),
                        this.getDestinatario(),
                        this.getDataRecebimentoInicio(),
                        this.getDataRecebimentoFim(),
                        this.getOrgaoRemetente(),
                        this.getOrgaoDestino(),
                    {
                        xtype: 'button',
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        style: 'margin-top: 10px',
                        text: 'Gerar Relatório',
                        width: 100,
                        height: 25,
                        scope: this,
                        handler: this._buildReport,
                    },
                    ]
                },
                ]
            }
            ]
        });

        return this._panel;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Relatório -> Athenas'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items:[ 
                    this.getMain(),
                ]
            }
        );

        // this.getCurrentPayroll();

        edocs.reports.AthenasReport.superclass.constructor.call(this, cfg);
    }
});