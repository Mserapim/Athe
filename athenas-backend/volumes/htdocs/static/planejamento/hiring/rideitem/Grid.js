Ext._define('planning.hiring.rideitem.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.rideitem.Window',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'cancel'],

    getColumnModel: function() {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel', [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Grupo', dataIndex: 'group', sortable: true, width: 100 },
                    { header: 'Linha', dataIndex: 'line', sortable: true, width: 100 },
                    { header: 'Descrição', dataIndex: 'item_unicode', sortable: true, id: 'autoExpandColumn' },
                ]
            );

        return this._columnModel;
    },

    getInsertAction: function() {
        if(!this._insertAction)
            this._insertAction = Ext._create('Ext.Button', {
                text: 'Adicionar',
                iconCls: 'icon-agree icon-agree-add',
                scope: this,
                handler: this._insertData
            });

        return this._insertAction;
    },

    _insertData: function() {
        Ext._create('planning.hiring.rideitem.Window', {
            params: {
                minute: this.params.minute,
            },
            action: 'create',
            callback: {
            success: {
                scope: this,
                fn: function(args) {
                    this.getStore().reload();
                }
            }
            },
        }).show();
    },

    execCancelAction: function (num) {
        if (this.getSelectionModel().getSelected()) {
            var title = 'Alterando item...';
            var msg = 'Informe uma justificativa para alterar o item?';
            var scope = this;
            var multiline = true;
            var fn_callback = function (btn, text) {
                if (btn == 'cancel') return;
                
                Ext.Ajax.request({
                    url: core.callAction('PHMRideItem', 'change_status_ride_item'),
                    scope: this,
                    params: {
                        item: this.getSelectionModel().getSelections().map(
                            function (record) {
                                return record.get('pk')
                            }
                        ).join(),
                        justificative: text ? text : '',
                        action: num // ação
                    },
                    success: function (request) {
                        var rst = Ext.decode(request.responseText);

                        if (rst.success)
                            this.getStore().reload();
                        else
                            Ext.Msg.show({
                                title: 'Ocorreu erro',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: rst.message
                            });
                    }
                });
            };

            Ext.Msg.prompt(title, msg, fn_callback, scope, multiline);

        } else {
            Ext.Msg.show({
                title: 'Atenção',
                icon: Ext.Msg.INFO,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item para cancelar'
            });
        }
    },

    getCancelAction: function () {
        if (!this._cancelAction)
            this._cancelAction = Ext._create('Ext.Button', {
                text: 'Cancelar',
                iconCls: 'icon-core icon-core-minus',
                scope: this,
                handler: function () {
                    this.execCancelAction(2) // 2 para ação cancelar
                }
            });
        return this._cancelAction;
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            columnAction: false,
        });

        planning.hiring.rideitem.Grid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'planning.hiring.rideitem.Restful',
    'planning.hiring.rideitem.Grid'
);