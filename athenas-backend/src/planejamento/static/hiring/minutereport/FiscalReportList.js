Ext._define('planning.hiring.minutereport.FiscalReportList', {
    extend: 'toolkit.widget.TabPanel',


    getFormPanel: function () {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                // frame: true,
                labelWidth: 100,
                autoHeight: true,
                width: 500,
                items: [
                    this.getFiscaisField(),
                    this.getSituacao(),
                    this.getTipoFiscal(),
                    this.getTipoDocumento()
                ]
            });

        return this._formPanel;
    },

    getFiscaisField: function () {
        if (!this._fiscaisField) {
            this._fiscaisField = new Ext.form.ComboBox({
                fieldLabel: 'Fiscais',
                hiddenName: 'fiscais',
                width: 350,
                store: [
                    [1, 'TODOS'],
                    [2, 'ATIVOS'],
                    [3, 'INATIVOS'],
                ],
                allowBlank: false,
                triggerAction: 'all',
                mode: 'local'
            });
        }
        return this._fiscaisField;
    },

    getSituacao: function () {
        if (!this._situacaoField) {
            this._situacaoField = new Ext.form.ComboBox({
                fieldLabel: 'Situação do Contrato e da Ata',
                hiddenName: 'situacao',
                width: 350,
                store: [
                    [1, 'TODOS'],
                    [2, 'ATIVOS'],
                    [3, 'INATIVOS'],
                ],
                allowBlank: false,
                triggerAction: 'all',
                mode: 'local'
            });
        }
        return this._situacaoField;
    },

    getTipoFiscal: function () {
        if (!this._tipoFiscalField) {
            this._tipoFiscalField = new Ext.form.ComboBox({
                fieldLabel: 'Tipo do Fiscal',
                hiddenName: 'tipo_fiscal',
                width: 350,
                store: [
                    [1, 'TODOS'],
                    [2, 'TITULAR'],
                    [3, 'SUBSTITUTO'],
                ],
                allowBlank: false,
                triggerAction: 'all',
                mode: 'local'
            });
        }
        return this._tipoFiscalField;
    },

    getTipoDocumento: function () {
        if (!this._tipoDocumento) {
            this._tipoDocumento = new Ext.form.ComboBox({
                fieldLabel: 'Tipo de Documento',
                hiddenName: 'tipo_documento',
                width: 350,
                store: [
                    [1, 'TODOS'],
                    [2, 'SOMENTE ATAS'],
                    [3, 'SOMENTE CONTRATOS'],
                ],
                allowBlank: false,
                triggerAction: 'all',
                mode: 'local'
            });
        }
        return this._tipoDocumento;
    },


    getMain: function () {
        if (!this._panel)
            this._panel = Ext._create('Ext.Panel', {
                layout: 'border',
                region: 'center',
                height: 650,
                split: true,
                autoEl: { tag: 'center' },
                items: [
                    {
                        region: 'center',
                        border: false,
                        items:[
                            {
                                xtype: 'fieldset',
                                title: 'Férias a Usufruir no Mês',
                                width: 650,
                                style: 'margin: 5px',
                                align: 'left',
                                items: [
                                    this.getFormPanel(),
                                    {
                                        xtype: 'button',
                                        iconCls: 'icon-siatu icon-siatu-move-down',
                                        style: 'margin-top: 10px',
                                        text: 'Gerar Relatório',
                                        width: 100,
                                        height: 25,
                                        scope: this,
                                        handler: this.generate,
                                    }
                                ]
                            },

                        ]
                    }
                ]
            });

        return this._panel;
    },


    generate: function () {
        supervisor_status = this.getFiscaisField().getValue();
        status = this.getSituacao().getValue();
        supervisor_kind = this.getTipoFiscal().getValue();
        tipo = this.getTipoDocumento().getValue();
        
        if(supervisor_status == '' || status == '' || supervisor_kind == '' || tipo == ''){
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Todos os campos são obrigatórios.'
            });
            return;
        }

        engine.mq.Report.request({
            report: '/to/mpe/planejamento/minute_contrato_list_by_supervisor_by_quantity',
            waitMessage: 'Gerando relatório...',
            params: Ext.apply(
                {
                    outfile: 'listagem_de_fiscais',
                    report_name: 'Listagem de Fiscais',
                    supervisor_status: supervisor_status,
                    status: status,
                    supervisor_kind: supervisor_kind,
                    tipo: tipo,
                }
            ),
        });
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Relatório -> Fiscais de Atas e Contratos',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items:[
                    this.getMain(),
                ],
            }
        );

        planning.hiring.minutereport.FiscalReportList.superclass.constructor.call(this, cfg);
    }
});