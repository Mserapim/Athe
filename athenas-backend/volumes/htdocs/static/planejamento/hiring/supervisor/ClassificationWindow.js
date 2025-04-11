Ext._define('planning.hiring.supervisor.ClassificationWindow', {
  extend: 'core.RestfulWindow',
  rest: 'planning.hiring.supervisor.ClassificationRestful',

    getFormPanel: function() {
      if(!this._formPanel) {
        this._formPanel = Ext._create('Ext.form.FormPanel', {
        border: false,
        frame: true,
        items: [
          {
              xtype: 'choicefield',
              fieldLabel: 'Classificação',
              hiddenName: 'kind',
              choiceId: 'contrato.SUPERVISOR_CLASSIFICATION'
          },
          {
              xtype: 'checkbox',
              fieldLabel: '&nbsp;',
              labelSeparator: '&nbsp;',
              boxLabel: 'Ativo?',
              allowBlank: true,
              name: 'active'
          },
        ]
        });
      }

      return this._formPanel;
    }
});
