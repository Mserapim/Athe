/**
 *
 **/
Ext._define('rh.gfp.reports.DemonstrativoIgeprevWindow', {
    extend: 'Ext.Window',

    width: 500,
    title: 'Demonstrativo IGEPREV',

    // report: '/to/mpe/gfp/transparency/Payroll',
    report: '/to/mpe/gfp/demons_igeprev',

    _reportName: 'Demonstrativo IGEPREV',

    _filename: 'demonstrativo-igeprev',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 65,
                width: 500,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Folha',
                        name: 'id_folha',
                        rest: 'rh.gfp.payroll.PayrollRestful',
                        gridColumnAction: false,
                        width: 400
                    }
                ]
            });

        return this._formPanel;
    },

    getValues: function() {
        return this.getFormPanel().getForm().getValues();
    },

    filename: function() {
        return this._filename;
    },

    reportName: function() {
        return this._reportName;
    },

    generate: function(preventClose) {
        var values = this.getValues();

        engine.mq.Report.request({
            report: this.report,
            params: Ext.apply(
                values,
                {
                    outfile: this.filename(),
                    report_name: this.reportName()
                }
            ),
            el: this.getEl(),
            waitMessage: 'Gerando relatório...',
        });

        if(!preventClose) this.close();
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
                items: this.getFormPanel(),
                buttons: [
                    {
                        text: 'Gerar',
                        scope: this,
                        handler: function() { this.generate(false); }
                    },
                    {
                        text: 'Gerar e novo',
                        scope: this,
                        handler: function() { this.generate(true); }
                    },
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: this.destroy
                    }
                ]
            }
        );

        rh.gfp.reports.DemonstrativoIgeprevWindow.superclass.constructor.call(this, cfg);
    }
});
