/**
 *
 **/
Ext._define('engine.ControllerGrid', {
    'extend': 'core.RestfulGrid',

    'restWindow': 'engine.ControllerWindow',

    'getToolbar': function(cfg) {
        if(!this._toolbar) {
            this._toolbar = engine.ControllerGrid.superclass.getToolbar.call(this, cfg);

            this._toolbar.insert(
                3,
                {
                    'text': 'Mover funcionalidade',
                    'iconCls': 'icon-core icon-core-move-fold',
                    'scope': this,
                    'handler': this.moveTo
                }
            );
            this._toolbar.insert(
                3,
                '-'
            );
        }

        return this._toolbar;
    },

    'moveTo': function() {
        var selection = this.getSelectionModel().getSelections();

        if(selection.length > 0) {
            Ext._create('core.TreeSelectWindow', {
                'title': 'Movendo funcionalidades',
                'restTree': 'engine.ApplicationTree',
                'callback': {
                    'scope': this,
                    'fn': function(instance) {
                        var rest = this.factoryRestful();
                        rest.doRequest(
                            rest.getRoute('update', null, null, {
                                'params': {
                                    'application': instance.id,
                                    'filter': Ext.encode([
                                        {
                                            'property': 'pk__in',
                                            'value': selection.map(
                                                function(item) {
                                                    return item.get('pk');
                                                }
                                            ),
                                            'stage': 0
                                        }
                                    ])
                                },
                                'scope': this,
                                'success': function(request) {
                                    var rst = Ext.decode(request.responseText);

                                    if(!rst.success)
                                        Ext.Msg.show({
                                            'title': 'Movendo funcionalidades',
                                            'icon': Ext.Msg.ERROR,
                                            'buttons': Ext.Msg.OK,
                                            'msg': rst.message
                                        });
                                    else
                                        this.getStore().reload();
                                },
                                'failure': function(request) {
                                    Ext.Msg.show({
                                        'title': 'Movendo funcionalidades',
                                        'icon': Ext.Msg.ERROR,
                                        'buttons': Ext.Msg.OK,
                                        'msg': 'Ocorreu um erro tentando acessar o recurso desejado.'
                                    });
                                }
                            })
                        );
                    }
                }
            }).show();
        }
        else
            Ext.Msg.show({
                'title': 'Movendo funcionalidades',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Primeiro selecione os itens que deseja mover.'
            });
    },

    'getColumnModel': function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    // {
                    //     'header': '',
                    //     'dataIndex': 'icons',
                    //     'width': 25,
                    //     'menuDisabled': true,
                    //     'renderer': adm.daily.rendererIconGrid
                    // },
                    {'header': 'Título', 'dataIndex': 'title', 'id': 'autoExpandColumn'},
                    {'header': 'Controlador', 'dataIndex': 'controller', 'width': 175},
                    {'header': 'Module', 'dataIndex': 'module', 'width': 175},
                    {'header': 'Criado por', 'dataIndex': 'created_by_unicode', 'width': 175},
                    {'header': 'Modificado por', 'dataIndex': 'modified_by_unicode', 'width': 175},
                    {
                        'header': 'Visivel',
                        'dataIndex': 'active',
                        'width': 65,
                        'renderer': function(value) {
                            return (value ? "SIM": "NÃO")
                        }
                    }
                ]
            );

        return this._columnModel;
    },
});

core.RestfulGrid.register(
    'engine.ControllerRestful',
    'engine.ControllerGrid'
);
