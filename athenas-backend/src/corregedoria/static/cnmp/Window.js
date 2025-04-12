Ext._define('corregedoria.cnmp.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cnmp.Restful',

    width: 600,

    getEmployee: function(cfg) {
        if(!this._employee) {
            this._employee = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Membro',
                allowBlank: false,
                rest: "rh.employee.Restful",
                name: "employee",
                disabled: false,
                preFilter: [
                    {
                        'property': 'tipo',
                        'value': 'M',
                        'stage': 9999
                    }
                ],
                gridConfig: {
                    allowCreate: false,
                    allowRemove: false,
                    allowUpdate: false,
                    columnAction: false,
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                    configOrderToolBar: ['search'],
                }
            });
        }
        return this._employee;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getEmployee(cfg)
                ]
            });

        return this._formPanel;
    },
});
