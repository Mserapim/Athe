
Ext.ns('edocs.protocolo.box.MixinSelectionGrid');

edocs.protocolo.box.MixinSelectionGrid = {
    addSelection: function(pk) {
        if(this.selected.indexOf(pk) < 0) {
            this.selected.push(pk);
            this.setFilterProperty('pk__in', this.selected, 100);
        }
    },

    removeSelection: function(pk) {
        if(this.selected.indexOf(pk) >= 0) {
            this.selected.remove(pk);
            this.setFilterProperty('pk__in', this.selected, 100);
        }
    },

    getAddFieldAction: function(cfg) {
        if(!this._addFieldAction)
            this._addFieldAction = Ext._create('Ext.Container', {
                layout: 'form',
                border: false,
                labelWidth: 115,
                cls: 'x-toolbar-item-form',
                items: [
                    this.getAddField()
                ]
            });

        return this._addFieldAction;
    },

    getActionColumn: function() {
        if(!this._actionColumn)
            this._actionColumn = Ext._create('Ext.grid.ActionColumn', {
                width: 30,
                scope: this,
                items: [
                    {
                        iconCls: 'icon-16px icon-core icon-core-delete',
                        tooltip: 'Retirar item da seleção.',
                        handler: function(action, index) {
                            this.removeSelection(this.getStore().getAt(index).get('pk'));
                        }
                    }
                ],
            });

        return this._actionColumn;
    }
};
