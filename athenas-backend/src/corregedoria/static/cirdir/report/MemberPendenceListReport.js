
Ext._define('corregedoria.cirdir.report.MemberPendenceListReport', {
    extend: 'corregedoria.reportbuilder.BaseWindow',

    _report: '',

    _reportName: 'Lista de Pendências - Membros',

    _filename: 'srdir-listagem-de-pendencias',

    _controller: 'CIRDIRPendenciesListReport',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                labelWidth: 75,
                border: false,
                items: [
                    {
                        xtype:'fieldset',
                        title: 'Relatório de Pendências - Listagem',
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
                          this.getCheckItems()
                      ]
                    },
                ]
        });
        return this._formPanel;
    },

    getCheckItems: function() {
        if(!this._getCheckItems)
            this._getCheckItems = Ext._create('Ext.form.CheckboxGroup', {
            xtype: 'checkboxgroup',
            fieldLabel: 'itens',
            columns: 5,
            items: [
                {boxLabel: 'Endereço', name: 'address'},
                {boxLabel: 'Bens e Direitos', name: 'property'},
                {boxLabel: 'Dívidas e Ónus', name: 'debits'},
                {boxLabel: 'Docência - 1º Semestre', name: 'teaching1'},
                {boxLabel: 'Docência - 2º Semestre', name: 'teaching2'},
                {boxLabel: 'IRPF', name: 'irpf'},
            ]
        });
        return this._getCheckItems;
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
        corregedoria.cirdir.report.MemberPendenceListReport.superclass.constructor.call(this, cfg);
    }
});
