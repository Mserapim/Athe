
Ext._define('corregedoria.cirdir.report.EmployeePendenceReport', {
    extend: 'corregedoria.reportbuilder.BaseWindow',

    _report: '',

    _listOutputFormat: [
      {
          title: 'Arquivo PDF',
          type: 'PDF',
          iconCls: 'icon-ged icon-ged-application-pdf'
      },
      {
          title: 'Arquivo CSV',
          type: 'CSV',
          iconCls: 'icon-ged icon-ged-text-plain',
      },
    ],

    _reportName: 'Servidores com pendência - DBVR',

    _filename: 'dbvr-servidores-com-pendencia',

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
                        title: 'Parâmetros',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                          {
                            xtype: 'hidden',
                            value: 'S',
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
                            name: 'year_base',
                          },
                          this.getCheckItems()
                      ],
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
            hidden: true,
            columns: 3,
            items: [
                {boxLabel: 'Bens e Direitos', name: 'property', checked: true},
                {boxLabel: 'Dívidas e Ónus', name: 'debits', checked: true},
                {boxLabel: 'IRPF', name: 'irpf', checked: true},
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
        corregedoria.cirdir.report.EmployeePendenceReport.superclass.constructor.call(this, cfg);
    }
});
