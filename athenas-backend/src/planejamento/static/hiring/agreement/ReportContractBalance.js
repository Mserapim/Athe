Ext._define('planning.hiring.agreement.ReportContractBalance', {
    extend: 'Ext.Window',

    title: 'Levantamento de Saldo de Contratos',

    width: 435,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 100,
                autoHeight: true,
                items:[
                {
                    xtype: 'button',
                    iconCls: 'icon-siatu icon-siatu-move-down',
                    style: 'margin-top: 10px',
                    text: 'Gerar Relatório',
                    width: 100,
                    height: 25,
                    scope: this,
                    menu: {
                        scope: this,
                        items: [
                            {
                                text: 'Arquivo PDF ',
                                type: 'PDF',
                                iconCls: 'icon-ged icon-ged-application-pdf',
                                scope: this,
                                handler: function (item) {
                                    this.generate(item.type);
                                }
                            },
                            {
                                text: 'Arquivo ODT',
                                type: 'ODT',
                                iconCls: 'icon-ged icon-ged-application-msword',
                                scope: this,
                                handler: function (item) {
                                    this.generate(item.type);
                                }
                            },
                            {
                                text: 'Arquivo XLS',
                                type: 'XLS',
                                iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                scope: this,
                                handler: function (item) {
                                    this.generate(item.type);
                                }
                            },
                        ]
                    },
                }
                ]
            });

        return this._formPanel;
    },

    generate: function(type) {

        engine.mq.Report.request({
            report: '/to/mpe/planejamento/contrato/saldo_contrato',
            el: this.getEl(),
            waitMessage: 'Gerando relatório...',
            params: Ext.apply(
                {
                    outfile: 'Saldo_Contratos',
                    report_name: 'Levantamento de Saldo de Contratos',
                }
            ),
        }, type);

    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                modal: true,
                resizable: false,
                border: false
            }
        );

        Ext.apply(
            cfg,
            {
                items: [
                    this.getFormPanel(),
                ]
            }
        );
        planning.hiring.agreement.ReportContractBalance.superclass.constructor.call(this, cfg);
    }
});