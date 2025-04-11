Ext._define('raf.trustrelationship.Window', {
    extend: 'core.RestfulWindow',

    rest: 'raf.trustrelationship.Restful',

    width: 600,

    getTrustEmployeeField: function(cfg){
        if(!this._trustField){
            this._trustField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Servidor",
                allowBlank: true,
                rest: "rh.employee.Restful",
                name: "trust_employee",
                gridConfig: {
                    columnAction: false,
                    allowUpdate: false,
                    allowRemove: false,
                    hideItemsToolbar: ['download'],
                    hiddenFilter: true,
                    hideColumns: ['ativo', 'departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode', 'first_adjustment_date'],
                    listeners: {
                        scope: this,
                        render: function(grid){
                            tbar = grid.getToolbar();
                            tbar.remove(tbar.getComponent(0));//Novo
                            tbar.remove(tbar.getComponent(0));//Editar
                            tbar.remove(tbar.getComponent(0));//Remover
                        },
                    }
                },
            });
        }

        return this._trustField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getTrustEmployeeField(cfg),
                    {
                        xtype: 'checkbox',
                        boxLabel: 'Ativo',
                        labelSeparator: '&nbsp;',
                        fieldLabel: '&nbsp;',
                        allowBlank: true,
                        name: 'activated',
                        checked: true,
                    },
                ]
            });

        return this._formPanel;
    }
});
