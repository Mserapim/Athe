Ext._define('adm.contabilidade.budgetaryindicator.Window', {
  extend: 'core.RestfulWindow',
  rest: 'adm.contabilidade.budgetaryindicator.Restful',
  width: 486,

    getFormPanel: function() {
      if(!this._formPanel) {
        this._formPanel = Ext._create('Ext.form.FormPanel', {
        border: false,
        frame: true,
        items: [
          {
            xtype: 'numberfield',
            fieldLabel: 'Ano',
            name: 'year',
            allowBlank: false,
            maxLength: 4,
            width: 350,
            allowDecimals: false
          },
          {
            xtype: 'textfield',
            fieldLabel: 'I.O.',
            name: 'name',
            allowBlank: false,
            maxLength: 128,
            width: 350
          },
          {
            xtype: 'textfield',
            fieldLabel: 'Objeto',
            name: 'object_name',
            allowBlank: false,
            maxLength: 128,
            width: 350
          },
          {
              xtype: 'rest-autocompletefield',
              fieldLabel: "Fonte",
              allowBlank: false,
              rest: "adm.contabilidade.FonteRecursoRestful",
              name: "source",
              width: 352
          },
        ]
        });
      }

      return this._formPanel;
    }

});
