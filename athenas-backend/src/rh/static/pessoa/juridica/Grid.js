/**
 *
 **/
Ext._define('rh.pessoa.juridica.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.pessoa.juridica.Window',

    keywordFieldMessage: 'Nome ou cnpj (somente números)',

    hideItemsToolbar: ['edit', 'remove'],

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Nome', dataIndex: 'nome', width: 260, sortable:true},
                    {header: 'Cnpj', dataIndex: 'cnpj', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    },

    'getActionColumn': function() {
        if(!this._actionColumn)
            this._actionColumn = Ext._create('Ext.grid.ActionColumn', {
                'width': 70,
                'scope': this,
                'items': [
                    {
                        'iconCls': 'icon-16px icon-core icon-core-delete',
                        'tooltip': 'Remover item.',
                        'handler': function(action, index) {
                            var record = this.getStore().getAt(index);
                            record && this.defaultRemoveFunction(record);
                        }
                    }
                ]
            });

        return this._actionColumn;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg,{
            columnAction: false,
            defaultRemoveFunction: this.removeItems,
        });
        
        Ext.apply(cfg,{
            allowUpdate: false,
            allowRemove: false,
        });

        rh.pessoa.juridica.Grid.superclass.constructor.call(this, cfg);
    }
    
})