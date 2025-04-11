Ext._define('raf.specialorgan.Window', {
    extend: 'core.RestfulWindow',

    rest: 'raf.specialorgan.Restful',
    width: 600,

    getOrgan: function(cfg){
        if(!this._specialOrgan){
            this._specialOrgan = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Orgão",
                allowBlank: true,
                rest: "rh.generalorgan.Restful",
                name: "location",
                gridConfig: {
                    columnAction: false,
                    allowUpdate: false,
                    allowRemove: false,
                    hideItemsToolbar: ['download'],
                    hiddenFilter: true,
                    // hideColumns: ['ativo', 'departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode', 'first_adjustment_date'],
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

        return this._specialOrgan;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                  this.getOrgan(cfg)
                ]
            });

        return this._formPanel;
    }
});
