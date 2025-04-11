Ext._define('corregedoria.cirdir.report.BaseWindow', {
    extend: 'Ext.Window',

    report: undefined,

    controller: undefined,

    _filename: 'undefined',

    _reportName: 'undefined',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false
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
                        text: 'Fechar',
                        scope: this,
                        handler: this.destroy
                    }
                ]
            }
        );

        corregedoria.cirdir.report.BaseWindow.superclass.constructor.call(this, cfg);
    }
});
