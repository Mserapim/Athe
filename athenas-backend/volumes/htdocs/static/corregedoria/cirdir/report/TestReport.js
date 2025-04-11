
Ext._define('corregedoria.cirdir.report.TestReport', {
    extend: 'corregedoria.reportbuilder.BaseWindow',

    _report: '/to/mpe/corregedoria/srdir/teaching',

    _reportName: 'Membros que exercem docência',

    _filename: 'corregedoria-membros-exercem-docencia',

    _controller: 'CIRDIRTestReport',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                labelWidth: 75,
                border: false,
                items: [
                    {
                        xtype:'fieldset',
                        title: 'Parâmetros',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                          {
                            xtype: 'textfield',
                            fieldLabel: 'Ano de Referência',
                            emptyText: 'aaaa',
                            regex: /^(\d{4})$/,
                            regexText: 'Entrada inválida.<br/>Formato correto: <b>aaaa</b>.',
                            maxLength: 4,
                            maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>aaaa</b>.',
                            name: 'year_base',
                          },
                      ]
                    },
                ]
        });
        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Relatorio de teste',
                width: 700,
            }
        );
        corregedoria.cirdir.report.TestReport.superclass.constructor.call(this, cfg);
    }
});
