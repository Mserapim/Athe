Ext._define('rh.reports.WorkplaceByLocality', {
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
                    this.getCitiesField()
                ]
            });

        return this._formPanel;
    },

    getCitiesField: function() {
        if (!this._citiesField) {
            this._citiesField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Cidade',
                name: 'id_cidade',
                rest: 'rh.localidade.Restful',
                allowBlank: true,
                width: 320,
                preFilter: [
                    {'property':  'estado__sigla', 'value': 'TO', 'stage': 1}
                ],
                gridConfig: {
                    allowCreate: false,
                    allowRemove: false,
                    allowUpdate: false,
                    columnAction: false,
                    configOrderToolBar: ['search'],
                    hideColumns: ['valor_vale_transporte', 'ibge', 'distancia_capital', 'nome', 'microregiao_unicode', 'sede_termo', 'siafi', 'comarca_unicode', 'cep', 'estado_unicode', 'indicador_municipio', 'descricao', 'sigla']
                },
                enableKeyEvents: true
            });
        }

        return this._citiesField;
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
                                title: 'Relatório de lotação por cidade',
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

        var id_cidade = this.getCitiesField().getValue();

        engine.mq.Report.request({
            report: '/to/mpe/rh/servidor/employee_by_city',
            waitMessage: 'Gerando relatório...',
            params: Ext.apply(
                {
                    id_cidade: id_cidade,
                    outfile: 'Relatorio de lotação por cidade' + new Date().format("d/m/Y"),
                    report_name: 'Relatorio de lotação por cidade',
                }
            ),
        });
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Relatório de lotação por cidade',
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
