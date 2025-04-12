Ext._define('rh.ferias.reports.HolidayStock', {
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
                    this.getType(),
                    this.getYearField(),
                ]
            });

        return this._formPanel;
    },

    getType: function () {
        if (!this._typeField) {
            this._typeField = new Ext.form.ComboBox({
                fieldLabel: 'Tipo de Servidor',
                hiddenName: 'type',
                width: 350,
                store: [
                    ['S', 'SERVIDOR'],
                    ['M', 'MEMBRO'],
                ],
                triggerAction: 'all',
                mode: 'local'
            });
        }
        return this._typeField;
    },

    getYearField: function () {
        if (!this._yearField)
            this._yearField = Ext._create('Ext.form.TextField', {
                name: 'year',
                fieldLabel: 'Ano Final do Período',
                width: 350
            });

        return this._yearField;
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
                        items: [
                            {
                                xtype: 'fieldset',
                                title: 'Estoque de Férias',
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
            report: '/to/mpe/rh/ferias/holiday_stock',
            waitMessage: 'Gerando relatório...',
            params: Ext.apply(
                {
                    outfile: 'estoque_de_ferias_' + this.getType().getValue() + '_' + this.getYearField().getValue(),
                    report_name: 'Estoque de Férias',
                    employee_type: this.getType().getValue(),
                    year: this.getYearField().getValue(),
                }
            ),
        }, type);
    },

    constructor: function (cfg) {
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
                items: [
                    this.getMain(),
                ],
            }
        );

        rh.ferias.reports.HolidayStock.superclass.constructor.call(this, cfg);
    }
});
