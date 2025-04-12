Ext._define('rh.gfp.reports.Billet', {
    extend: 'toolkit.widget.TabPanel',

    getStartDateField: function() {
        if (!this._startDateField) {
            this._startDateField = Ext._create('Ext.form.DateField', {
                name: 'start_date',
                fieldLabel: "Data inicial",
                width: 200,
            });
        }
        return this._startDateField;
    },

    getEndDateField: function() {
        if (!this._endDateField) {
            this._endDateField = Ext._create('Ext.form.DateField', {
                name: 'end_date',
                fieldLabel: "Data final",
                width: 200,
            });
        }
        return this._endDateField;
    },

    getNameField: function() {
        if (!this._nameField) {
            this._nameField = Ext._create('Ext.form.TextField', {
                name: 'name',
                fieldLabel: 'Nome',
                anchor: '99%',
                allowBlank: true,
            });
        }
        return this._nameField;
    },

    getGenerateButton: function () {
        if (!this._generateButton) {
            this._generateButton = Ext._create('Ext.Button', {
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
            });
        }
        return this._generateButton;
    },

    getMainPanel: function (cfg) {
        if (!this._mainPanel) {
            this._mainPanel = Ext._create('Ext.Panel', {
                region: 'center',
                items: {
                    xtype: 'fieldset',
                    title: 'Boletos Gerados',
                    layout: 'form',
                    labelWidth: 70,
                    items: [
                        this.getStartDateField(),
                        this.getEndDateField(),
                        this.getNameField(),
                    ],
                    buttons: [
                        this.getGenerateButton(),
                    ],
                    buttonAlign: 'center',

                    // _SNIPPET_ "Bruxaria" pra centralizar o FieldSet
                    width: '30%',
                    style: 'margin: 20px auto',
                }
            });
        }
        return this._mainPanel;
    },

    generate: function (type) {
        var start_date = this.getStartDateField().getValue();
        var end_date = this.getEndDateField().getValue();
        var name = this.getNameField().getValue();

        if (!(start_date && end_date) && !name) {
            Ext.Msg.show({
                title: 'Validando',
                msg: 'Forneça uma data inicial e final de vencimento e/ou um nome.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
            });
            return;
        }

        engine.mq.Report.request({
            report: '/to/mpe/financeiro/boletos',
            waitMessage: 'Gerando relatório...',
            params: {
                outfile: 'boletos_gerados',
                report_name: 'Boletos Gerados',
                data_inicial: Ext.util.Format.date(start_date, 'Y-m-d'),
                data_final: Ext.util.Format.date(end_date, 'Y-m-d'),
                nome: name,
            }
        }, type);
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Relatório -> Boletos Gerados',
        });

        Ext.apply(cfg, {
            layout: 'border',
            items: this.getMainPanel(),
        });

        rh.gfp.reports.Billet.superclass.constructor.call(this, cfg);
    }
});
