/**
 *
 **/
Ext._define('common.siatu.atendente.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.siatu.atendente.Window',

    keywordFieldMessage: 'usuário',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'busy', width: 20, renderer: common.siatu.rendererIconGrid},
                    {header: 'Usuario', dataIndex: 'username', width: 110},
                    {header: 'Nome', dataIndex: 'nome', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    },

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            hideItems = cfg.hideItemsToolbar || this.hideItemsToolbar;
            this._toolbar = common.siatu.atendente.Grid.superclass.getToolbar.call(this, cfg);

            if(hideItems.indexOf('notificacao') < 0){
                this._toolbar.add([
                    {
                        text: 'Notificação',
                        iconCls: 'icon-core icon-core-edit',
                        scope: this,
                        handler: this.windowNotificacao
                    }
                ])
            }
        }

        return this._toolbar;
    },

    windowNotificacao: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            Ext._create('common.siatu.atendente.WindowNotificacao',{
                action: 'update',
                oId: selected.get('pk'),
                title: 'Configuração - Notificação',
                values: 'remote',
                params: {},
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                }
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Notificação',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item.'
            });
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                hideItemsToolbar: ['edit', 'download']
            }
        );

        Ext.apply(
            cfg,
            {
                allowUpdate: false,
                columnAction: false,
            }
        );

        common.siatu.atendente.Grid.superclass.constructor.call(this, cfg);
    }

})
