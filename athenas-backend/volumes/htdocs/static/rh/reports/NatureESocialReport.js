Ext._define('rh.reports.NatureESocialReport', {
    extend: 'toolkit.widget.TabPanel',

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
                                title: 'Nature (eSocial)',
                                width: "50%",
                                style: 'margin: 5px',
                                align: 'center',
                                items: [
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

            engine.mq.Report.request({
                report: '/mt/mpe/gfp/nature_esocial',
                waitMessage: 'Gerando relatório...',
                params: Ext.apply(
                    {
                        outfile: 'natureza_esocial' + new Date().format("d/m/Y"),
                        report_name: 'Relatório - Natureza (eSocial)',
                    }
                ),
            }, type_report
        );
    },

    constructor: function (cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Relatório -> Natureza (eSocial)',
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

        rh.reports.NatureESocialReport.superclass.constructor.call(this, cfg);
    }
});