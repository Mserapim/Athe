Ext._define('rh.ferias.reports.HolidaysEnjoyMonth', {
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
                    this.getYearField(),
                    this.getMonthField(),
                    this.getType(),
                ]
            });

        return this._formPanel;
    },

    getType: function () {
        if (!this._typeField) {
            this._typeField = new Ext.form.ComboBox({
                fieldLabel: 'Tipo',
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

    getYearField: function(){
        if(!this._yearField)
            this._yearField = Ext._create('Ext.form.TextField', {
                name: 'year',
                fieldLabel: 'Ano',
                width: 350
            });

        return this._yearField;
    },

    getMonthField: function () {
        if (!this._monthField) {
            this._monthField = new Ext.form.ComboBox({
                fieldLabel: 'Mês',
                hiddenName: 'mes',
                width: 350,
                store: [
                    [1, 'JANEIRO'],
                    [2, 'FEVEREIRO'],
                    [3, 'MARÇO'],
                    [4, 'ABRIL'],
                    [5, 'MAIO'],
                    [6, 'JUNHO'],
                    [7, 'JULHO'],
                    [8, 'AGOSTO'],
                    [9, 'SETEMBRO'],
                    [10, 'OUTUBRO'],
                    [11, 'NOVEMBRO'],
                    [12, 'DEZEMBRO'],
                ],
                triggerAction: 'all',
                mode: 'local'
            });
        }
        return this._monthField;
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
                                        // handler: this.generate,
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
            report: '/to/mpe/rh/ferias/fruicao_ferias',
            waitMessage: 'Gerando relatório...',
            params: Ext.apply(
                {
                    outfile: 'ferias_usufruir',
                    report_name: 'Férias a Usufruir no Mês',
                    tipo: this.getType().getValue(),
                    ano: this.getYearField().getValue(),
                    mes: this.getMonthField().getValue()
                }
            ),
        }, type);
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Relatório -> Férias a Usufruir no Mês',
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

        rh.ferias.reports.HolidaysEnjoyMonth.superclass.constructor.call(this, cfg);
    }
});