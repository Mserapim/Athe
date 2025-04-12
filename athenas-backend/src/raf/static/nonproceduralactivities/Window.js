Ext._define('raf.nonproceduralactivities.Window', {
  extend: 'core.RestfulWindow',
  rest: 'raf.nonproceduralactivities.Restful',
  width: 810,

    getFormPanel: function() {
      if(!this._formPanel) {
        this._formPanel = Ext._create('Ext.form.FormPanel', {
            border: false,
            frame: true,
            items: [
                {
                    xtype: 'rest-autocompletefield',
                    fieldLabel: "Procedimento",
                    allowBlank: false,
                    rest: "judicial.taxonomy.LegalProcedureRestful",
                    name: "legal_procedure",
                    autoWidth: true,
                    gridConfig: {
                        columnAction: false,
                        configOrderToolBar: ['search'],
                        hideColumns: ['version_unicode'],
                    }
                },
                {
                    xtype: 'textfield',
                    fieldLabel: 'Título',
                    name: 'title',
                    maxLength: 128,
                    allowBlank: false,
                    width: 670
                },
                {
                    xtype: 'datefield',
                    fieldLabel: 'Data',
                    name: 'date',
                    allowBlank: false,
                },
                {
                    xtype: 'textarea',
                    fieldLabel: 'Resumo',
                    name: 'description',
                    width: 670,
                },

            ]
        });
      }
      return this._formPanel;
  },
});
