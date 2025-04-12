Ext._define('rh.reports.SalaryTableReport', {
    extend: 'toolkit.widget.TabPanel',


    getFormPanel: function () {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 100,
                autoHeight: true,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        hideLabel: true,
                        name: 'tabelasalarial_id',
                        displayField: 'unicode',
                        allowBlank: true,
                        rest: 'rh.gfp.estrutura_salarial.TabelaSalarialRestful',
                        width: 500,
                        gridConfig: {
                            allowCreate: false,
                            allowRemove: false,
                            allowUpdate: false,
                            columnAction: false,
                            configOrderToolBar: ['search'],
                            hideActions: ['remove', 'copy', 'edit'],
                        },
                    },
                ]
            });

        return this._formPanel;
    },

    getButtons: function () {
        if (!this._buttons) {
            var me = this;
            this._buttons = [];
            this._buttons.push({
                xtype: 'splitbutton',
                text: 'Gerar Relatório',
                iconCls: 'icon-ged icon-ged-application-pdf',
                style: 'padding:10px',

                handler: function () {
                    me.generate();
                },
                menu: {
                    items: [
                        {
                            text: 'Arquivo PDF ',
                            type: 'PDF',
                            iconCls: 'icon-ged icon-ged-application-pdf',
                            handler: function (item) {
                                me.generate(item.type);
                            }
                        },
                        {
                            text: 'Arquivo XLS',
                            type: 'XLS',
                            iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                            handler: function (item) {
                                me.generate(item.type);
                            }
                        },
                    ]
                },
            });
        }

        return this._buttons;
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
                        items: [
                            {
                                xtype: 'fieldset',
                                title: 'Tabela Salarial',
                                width: "50%",
                                style: 'margin: 5px',
                                align: 'center',
                                items: [
                                    this.getFormPanel(),
                                    this.getButtons()

                                ]
                            },

                        ]
                    }
                ]
            });

        return this._panel;
    },


    generate: function (type_report) {

        var values = this.getFormPanel().getForm().getValues();
        if ((values.tabelasalarial_id === 'undefined') || (values.tabelasalarial_id === "")) {
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.WARNING,
                buttons: Ext.Msg.OK,
                msg: 'Selecione uma Tabela Salarial para gerar o relatório.'
            });
        }
        else {
            engine.mq.Report.request({
                report: '/to/mpe/gfp/tabela_data_base',
                waitMessage: 'Gerando relatório...',
                params: Ext.apply(
                    values,
                    {
                        outfile: 'tabela_salarial_' + new Date().format("d/m/Y"),
                        report_name: 'Relatório - Tabela Salarial',
                    }
                ),
            }, type_report
            );
        }
    },

    constructor: function (cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Relatório -> Tabela Salarial',
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

        rh.reports.SalaryTableReport.superclass.constructor.call(this, cfg);
    }
});