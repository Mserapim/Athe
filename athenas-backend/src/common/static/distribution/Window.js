Ext._define('common.distribution.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.distribution.Restful',

    width: 500,

    getEmployeeOriginField: function (cfg) {
        if (!this._employeeOriginField) {
            var url = core.callAction('CDDistribution', 'employee_locations');

            this._employeeOriginField = Ext._create('core.fields.ComboField', {
                    fieldLabel: 'Origem',
                    hiddenName: 'origin',
                    valueField: 'pk',
                    displayField: 'description',
                    anchor: '99%',
                    emptyText: 'Departamento de origem...',
                    store: Ext._create('Ext.data.Store', {
                        proxy: Ext._create('Ext.data.HttpProxy', {url: url}),
                        reader: Ext._create('Ext.data.JsonReader', {
                            totalProperty: 'count',
                            root: 'collection',
                            fields: [
                                {name: 'pk', type: 'int'},
                                {name: 'description', type: 'string'}
                            ]
                        })
                    }),
                    allowBlank: false
                }
            );
        }
        return this._employeeOriginField;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 50,
                labelAlign: 'right',
                items: [
                    this.getEmployeeOriginField(cfg),
                    {
                        xtype: "textfield",
                        fieldLabel: "Título",
                        name: "title",
                        maxLength: 100,
                        anchor: '99%',
                        allowBlank: false
                    }
                ]
            });
        }
        return this._formPanel;
    }
});
