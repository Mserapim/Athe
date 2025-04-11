/**
 *
 **/
Ext._define('rh.gfp.paycheck.reports.PayCheck', {
    extend: 'Ext.Window',

    report: '/to/mpe/gfp/paycheck_by_id',

    _reportName: 'Contra Cheque',

    _filename: 'contra-cheque',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 65,
                items: [
                ]
            });

        return this._formPanel;
    },

    getValues: function() {

        var values = rh.gfp.paycheck.reports.PayCheck.superclass.getValues.call(this);
        return values;
    },

    filename: function() {
        return this._filename;
    },

    reportName: function() {
        return this._reportName;
    },

    generate: function(preventClose) {
        // var values = this.getValues();

        engine.mq.Report.request({
            report: this.report,
            params: Ext.apply(
                {},
                {

                    outfile: this.filename(),
                    report_name: this.reportName(),
                    contracheque: this._paycheck,
                    admin: 1
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

        rh.gfp.transparencychoice.reports.Support.superclass.constructor.call(this, cfg);
    }
});
