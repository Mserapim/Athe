Ext._define('rh.reports.AbsenteeismReport', {
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
                    this.getStartDate(),
                    this.getEndDate(),
                ]
            });

        return this._formPanel;
    },

    getStartDate: function () {
        if (!this._startdate)
            this._startdate = Ext._create('Ext.form.DateField', {
                name: 'start_date',
                fieldLabel: "Data Início",
                hidden: false,
                width: 350,
            });
        return this._startdate;
    },

    getEndDate: function () {
        if (!this._enddate)
            this._enddate = Ext._create('Ext.form.DateField', {
                name: 'end_date',
                fieldLabel: "Data Fim",
                hidden: false,
                width: 350,
            });
        return this._enddate;
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
                                title: 'Asbsenteísmo',
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
        var startdate = Ext.util.Format.date(this.getStartDate().getValue(), 'Y-m-d');
        var enddate = Ext.util.Format.date(this.getEndDate().getValue(), 'Y-m-d');

        engine.mq.Report.request({
            report: '/to/mpe/rh/absenteeism_absence',
            waitMessage: 'Gerando relatório...',
            params: {
                outfile: 'absenteísmo',
                report_name: 'Absenteísmo',
                from: startdate,
                at: enddate
            }
        });
    },

    constructor: function (cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Relatório -> Asbsenteísmo',
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

        rh.reports.AbsenteeismReport.superclass.constructor.call(this, cfg);
    }
});
