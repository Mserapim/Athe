Ext._define('rh.reports.CorrespondenceCSV', {
    extend: 'Ext.Window',
    getFormPanel: function(cfg) {
        if(!this.formPanel)
            this.formPanel = new Ext.form.FormPanel({
                items: [
                ],
            });

        return this.formPanel;
    },

    execute: function(){
       engine.mq.Report.request({
            report: '/to/mpe/cesaf/extrato_lotacao',
            waitMessage: 'Gerando relatório...',
            params: {
                outfile: 'extrato_lotacao',
                report_name: 'Extrato de Lotações'
            }
        }, 'CSV');
    },

    constructor: function(cfg) {
        if(!cfg) cfg = {}

        Ext.apply(
            cfg,
            {
                title: 'Extrato de Lotações',
                closable: true,
                resizable: false,
                width: 500,
                border: false,
                modal: true,
                items: [
                    this.getFormPanel(cfg),
                ],
                buttons: [
                    {
                        text: 'Gerar',
                        scope: this,
                        handler: this.execute
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        handler: this.destroy
                    }
                ]
            }
        );

        rh.reports.CorrespondenceCSV.superclass.constructor.call(this, cfg);
    }
});