Ext._define('raf.yearbase.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'raf.yearbase.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 50, renderer: core.rendererIconGrid, menuDisabled: true},
                    {header: 'Título', dataIndex: 'unicode', id: 'autoExpandColumn'},
                    {header: 'Vigência', dataIndex: 'valid_of', width: 110, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                    {
                        xtype: 'actioncolumn',
                        header:'Ações',
                        width: 60,
                        scope: this,
                        items:
                        [
                            {
                                tooltip:'Ativar/Desativar',
                                icon: '/'+ global.Context + '/static/common/raf/images/eye.png',
                                handler:function(grid, row, col)
                                {
                                    var rest = grid.factoryRestful();
                                    var record = grid.getStore().getAt(row);
                                    rest.enable(
                                        record.get('pk'),
                                        {
                                            scope: this,
                                            fn: function(rst) {
                                                core.invokeCallback((this.callback || {}).success);
                                                grid.getStore().reload();
                                            }
                                        },
                                        {
                                            scope: this,
                                            fn: function(message) {
                                                Ext.Msg.show({
                                                    title: 'Ativar / Desativar',
                                                    msg: message,
                                                    icon: Ext.Msg.ERROR,
                                                    buttons: Ext.Msg.OK
                                                });
                                            }
                                        },
                                        {
                                            scope: this,
                                            fn: function() {}
                                        }
                                    );
                                },
                                scope:this
                            },
                        ]
                    }
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'raf.yearbase.Restful',
    'raf.yearbase.Grid'
);
