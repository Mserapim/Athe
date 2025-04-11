Ext._define('rh.ferias.reports.UnmarkedScales', {
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
                    this.getAcquisitionPeriod(),
                ]
            });

        return this._formPanel;
    },

    getAcquisitionPeriod: function(){
        if(!this._periodoaquisitivo)
            this._periodoaquisitivo = Ext._create('core.fields.AutocompleteField', {
                name: 'periodoaquisitivo',
                rest: 'rh.ferias.pas.AcquisitionPeriodRestful',
                fieldLabel: 'Período Aquisitivo',
                width: 350,
                preFilter: [
                    {'property': 'data_publicacao', 'value': null, 'stage': 1000},
                    {'property': 'periodo_anterior', 'value': false, 'stage': 1001},
                ],
            });

        return this._periodoaquisitivo;
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
                                title: 'Acompanhamento de Escala de Férias',
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
                            },

                        ]
                    }
                ]
            });

        return this._panel;
    },


    generate: function (type) {

        engine.mq.Report.request({
            report: '/to/mpe/rh/ferias/escala_nao_marcada',
            waitMessage: 'Gerando relatório...',
            params: Ext.apply(
                {
                    outfile: 'escala_de_ferias_nao_marcadas',
                    report_name: 'Acompanhamento de Escala de Férias',
                    periodo: this.getAcquisitionPeriod().getValue(),
                }
            ),
        }, type);
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Relatório -> Acompanhamento de Escala de Férias',
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

        rh.ferias.reports.UnmarkedScales.superclass.constructor.call(this, cfg);
    }
});