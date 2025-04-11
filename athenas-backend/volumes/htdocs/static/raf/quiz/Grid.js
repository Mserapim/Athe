Ext._define('raf.quiz.Grid', {
    extend: 'core.RestfulGrid',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'copy', '-', 'search', '->', 'download'],

    restWindow: 'raf.quiz.Window',

    getCopyAction: function(cfg) {
        if(!this._copyAction)
            this._copyAction = Ext._create('Ext.Button', {
                text: 'Copiar',
                iconCls: 'icon-raf icon-raf-copy',
                scope: this,
                handler: this.openCopyWindow
            });

        return this._copyAction;
    },

    openCopyWindow: function() {
        var selected = this.getSelectionModel().getSelected();

        if(selected) {

            Ext._create('raf.quiz.CopyQuizWindow', {
                params: {
                    quiz: selected.get('pk'),
                    quiz_unicode: selected.get('unicode'),
                },
                callback: {
                    success: {
                        scope: this,
                        fn: function(instance) {
                            core.invokeCallback((this.callback || {}).success);
                            this.getStore().reload();
                        }
                    }
                }
            }).show();
        } else {
            Ext.Msg.show({
                title: 'Copiar',
                msg: 'Selecione o questionário que deseja copiar',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    activatedFilter: function(checked) {
        if(!checked)
            this.setFilterProperty('activated', 'true', -100);
        else
            this.removeFilterProperty('activated', -100);
    },

    disabledFilter: function(checked) {
        if(!checked)
            this.setFilterProperty('activated', 'true', 100);
        else
            this.removeFilterProperty('activated', 100);
    },

    yearFilter: function() {
        Ext._create(
            'raf.quiz.YearFilterWindow',
            {grid: this}
        ).show();
    },

    getFilterMenu: function(cfg) {
        if(!this._filterMenu)
            this._filterMenu = [
                '-',
                {
                    text: 'Ativo',
                    checked: true,
                    scope: this,
                    hideOnClick: false,
                    listeners: {
                        scope: this,
                        checkchange: function(menu, checked) {
                            this.activatedFilter(checked);
                        }
                    }
                },
                {
                    text: 'Desativado',
                    checked: false,
                    scope: this,
                    hideOnClick: false,
                    listeners: {
                        scope: this,
                        checkchange: function(menu, checked) {
                            this.disabledFilter(checked);
                        }
                    }
                },

                '-',
                {
                    text: 'Por Ano',
                    scope: this,
                    handler: this.yearFilter
                },

            ];
        return this._filterMenu;
    },


    getColumnModel: function() {

        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 40, renderer: core.rendererIconGrid, menuDisabled: true},
                    {header: 'Questionário', dataIndex: 'unicode', id: 'autoExpandColumn', hidden: true},
                    {header: 'Tipo', dataIndex: 'typequiz_unicode', width: 550, hidden: false,
                        // renderer: function(value, metaData, record) {
                        //    return '<div ext:qtip="'+record.get('list_taxonomy')+'">' + value + '</div>';
                        //  }
                    },
                    {header: 'Ano Base', dataIndex: 'yearbase_unicode', width: 200, hidden: false},
                    // {header: '', dataIndex: 'list_classes', width: 200, hidden: true},
                    {header: 'Ordem', dataIndex: 'number_order', width: 80, hidden: true},
                    {
                        header:'Ações',
                        dataIndex: 'actions',
                        xtype: 'actioncolumn',
                        scope: this,
                        width: 60,
                        items:
                        [
                            {
                                tooltip:'Ativar/Desativar',
                                icon: '/'+ global.Context + '/static/raf/images/eye.png',
                                handler:function(grid, row, col)
                                {
                                    grid.getSelectionModel().selectRow(row);
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
    },

    extraValues: function(values) {
        if(values)
            this._extraValues = values;

        return this._extraValues;
    }
});

core.RestfulGrid.register(
    'raf.quiz.Restful',
    'raf.quiz.Grid'
);
