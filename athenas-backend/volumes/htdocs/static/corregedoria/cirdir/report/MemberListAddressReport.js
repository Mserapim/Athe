
Ext._define('corregedoria.cirdir.report.MemberListAddressReport', {
    extend: 'corregedoria.reportbuilder.BaseWindow',

    _report: '',

    _reportName: 'Lista de Endereço - Membros',

    _filename: 'srdir-listagem-de-endereço',

    _controller: 'CIRDIRAddressListReport',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                labelWidth: 75,
                border: false,
                items: [
                    {
                        xtype:'fieldset',
                        title: 'Lista de Endereços',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                          {
                            xtype: 'hidden',
                            value: 'M',
                            name: 'employee_type'
                          },
                          {
                            xtype: 'textfield',
                            fieldLabel: 'Ano de Referência',
                            emptyText: 'aaaa',
                            regex: /^(\d{4})$/,
                            regexText: 'Entrada inválida.<br/>Formato correto: <b>aaaa</b>.',
                            maxLength: 4,
                            maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>aaaa</b>.',
                            name: 'year_base'
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
                title: 'Relatorio',
                width: 700,
            }
        );
        corregedoria.cirdir.report.MemberListAddressReport.superclass.constructor.call(this, cfg);
    }
});
