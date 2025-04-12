Ext._define('corregedoria.cirdir.evaluator.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cirdir.evaluator.Restful',

    width: 600,

    getEmployeeField: function() {
      if(!this._employeeField) {
          this._employeeField = Ext._create('core.fields.AutocompleteField', {
              xtype: "rest-autocompletefield",
              fieldLabel: 'Avaliador',
              allowBlank: true,
              rest: "corregedoria.cirdir.EmployeeRestful",
              name: "employee",
              disabled: false,
              preFilter: [
              ],
              gridConfig: {
                  columnAction: false,
                  hideColumns: ['departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode', 'ativo'],
                  hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
              }
          });
      }
      return this._employeeField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                  this.getEmployeeField(),
                  {
                      xtype: 'checkbox',
                      name: 'enabled',
                      boxLabel: 'Habilitado',
                      checked: true
                  },
                ]
            });

        return this._formPanel;
    },
});
