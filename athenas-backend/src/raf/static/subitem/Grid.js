Ext._define('raf.subitem.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'raf.subitem.Window',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'copy', '-', 'search', '->', 'download'],

    getCopyAction: function(cfg) {
        if(!this._copyAction)
            this._copyAction = Ext._create('Ext.Button', {
                text: 'Copiar',
                iconCls: 'icon-raf icon-raf-copy',
                scope: this,
                handler: this.copy_item
            });

        return this._copyAction;
    },

    copy: function() {
        var rest = Ext._create('raf.quiz.Restful');
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Copiando questionário...'});
        var values = this.getFormPanel().getForm().getValues();
        mask.show();
        rest.copyQuiz(
            values,
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        core.invokeCallback((this.callback || {}).success);
                        this.close();

                        Ext.Msg.show({
                            title: 'Copiando questionário',
                            msg: rst.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                    }
                    else
                        Ext.Msg.show({
                            title: 'Copiando questionário',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Copiando questionário',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    copy_item: function() {
        var selected = this.getSelectionModel().getSelected();
        var rest = this.factoryRestful();
        console.log(selected);
        if(selected) {
            rest.copy_item(
                selected.get('pk'),
                {
                    scope: this,
                    fn: function(rst) {
                        core.invokeCallback((this.callback || {}).success);
                        this.getStore().reload();
                    }
                },
                {
                    scope: this,
                    fn: function(message) {
                        Ext.Msg.show({
                            title: 'Copiar',
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
        } else {
            Ext.Msg.show({
                title: 'Copiar',
                msg: 'Selecione o item que deseja copiar',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Mês Anterior', dataIndex: 'icons', width: 105, renderer: core.rendererIconGrid, menuDisabled: true},
                    {header: 'Questionário', dataIndex: 'quiz_unicode', width:650},
                    {header: 'Título', dataIndex: 'title', id: 'autoExpandColumn'},
                    {header: 'Tipo', dataIndex: 'typesubitem_display', width:200,},
                    {header: 'Ordem', dataIndex: 'number_order', width:50, hidden: true},
                    {
                        xtype: 'actioncolumn',
                        dataIndex: 'actions',
                        header:'Ações',
                        width: 60,
                        scope: this,
                        items:
                        [
                            {
                                tooltip:'Ativar/Desativar',
                                icon: '/'+ global.Context + '/static/raf/images/eye.png',
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

                            {
                                tooltip:'Mover para cima',
                                icon: '/'+ global.Context + '/static/raf/images/navigation-up.png',
                                handler:function(grid, row, col)
                                {

                                    var up = grid.getStore().getAt(row-1);

                                    if(up === undefined)
                                        return;

                                    grid.getSelectionModel().selectRow(row);
                                    var me = grid.getStore().getAt(row);
                                    var rest = grid.factoryRestful();

                                    var values = {};

                                    values.me = me.get('pk');
                                    values.other = up.get('pk');

                                    rest.changeOrder(
                                        values,
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
                                                    title: 'Modificar Ordem',
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

                            {
                                tooltip:'Mover para baixo',
                                icon: '/'+ global.Context + '/static/raf/images/navigation-down.png',
                                handler:function(grid, row, col)
                                {

                                    var down = grid.getStore().getAt(row+1);

                                    if(down === undefined)
                                        return;

                                    grid.getSelectionModel().selectRow(row);
                                    var me = grid.getStore().getAt(row);
                                    var rest = grid.factoryRestful();

                                    var values = {};

                                    values.me = me.get('pk');
                                    values.other = down.get('pk');

                                    rest.changeOrder(
                                        values,
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
                                                    title: 'Modificar Ordem',
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
    'raf.subitem.Restful',
    'raf.subitem.Grid'
);
