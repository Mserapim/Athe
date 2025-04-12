Ext._define('corregedoria.inspection.inspection.filling.structure.structureexternalemployees.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.filling.structure.structureexternalemployees.Restful',

    width: 600,

    getExternalEmployeesField: function(cfg) {
        if(!this._externalEmployeesField) {
            this._externalEmployeesField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Servidor Externo",
                allowBlank: true,
                rest: "corregedoria.inspection.inspection.filling.structure.personalmovement.ExternalRestful",
                name: "external_employee",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar:['add', 'edit', 'remove', '-', 'download'],
                    params: {inspection: cfg.values.inspection_id},
                }
            });
        }
        return this._externalEmployeesField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 95,
                        items: [
                            this.getExternalEmployeesField(cfg),
                        ]
                    },
                ]
            });

        return this._formPanel;
    },
});
