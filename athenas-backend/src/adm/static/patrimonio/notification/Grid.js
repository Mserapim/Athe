Ext._define('adm.patrimony.notification.Grid', {
    extend: 'core.RestfulGrid',
    restWindow: 'adm.patrimony.notification.Window',
    configOrderToolBar: ['add', 'edit', 'remove', 'send'],

    getColumnModel: function() {
        if(!this._columnModel) {
            this._columnModel = Ext._create('Ext.grid.ColumnModel', [
                Ext._create('Ext.grid.RowNumberer'),
                {
                    header: '',
                    dataIndex: 'icons',
                    width: 30,
                    menuDisabled: true,
                    renderer: adm.daily.rendererIconGrid
                },
                {
                    header: 'Chave',
                    dataIndex: 'id',
                    width: 50,
                    hidden: true
                },
                {
                    header: 'Destinatário',
                    dataIndex: 'destination_unicode',
                    id: 'autoExpandColumn'
                },
                {
                    header: 'Protocolo',
                    dataIndex: 'protocol_unicode',
                    width: 120,
                    sortable: true
                },
                {
                    header: 'Enviado',
                    dataIndex: 'was_sent',
                    width: 66,
                    renderer: function (value) {
                        return (value ? 'Sim' : 'Não');
                    }
                },
                {
                    header: 'Notificado por',
                    dataIndex: 'notified_by_unicode',
                    width: 180,
                    hidden: true
                },
                {
                    header: 'Notificado em',
                    dataIndex: 'notified_at',
                    width: 90,
                    renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'),
                    hidden: true
                },
                {
                    header: 'Recebido por',
                    dataIndex: 'received_by_unicode',
                    width: 180
                },
                {
                    header: 'Recebido em',
                    dataIndex: 'received_at',
                    width: 90,
                    renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')
                },
                {
                    header: 'Criado por',
                    dataIndex: 'created_by_unicode',
                    width: 120,
                    hidden: true
                },
                {
                    header: 'Criado em',
                    dataIndex: 'created_at',
                    width: 90,
                    renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'),
                    hidden: true
                },
                {
                    header: 'Modificado por',
                    dataIndex: 'modified_by_unicode',
                    width: 120,
                    hidden: true
                },
                {
                    header: 'Modificado em',
                    dataIndex: 'modified_at',
                    width: 90,
                    renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'),
                    hidden: true
                }
            ]);
        }

        return this._columnModel;
    },

    send: function(params) {
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Notificando...'});
        mask.show();

        Ext.Ajax.request({
            url: core.callAction('PATNotification', 'send'),
            scope: this,
            params: params,
            success: function(response, options) {
                var result = Ext.decode(response.responseText);

                if (result.success) {
                    this.getStore().reload();
                    return;
                }

                Ext.Msg.show({
                    title: 'Notificação',
                    msg: result.message,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            },
            failure: function(response, options) {
                Ext.Msg.show({
                    title: 'Notificação',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            },
            callback: function(options, success, response) {
                mask.hide();
            },
        });
    },

    getSendAction: function() {
        if (this._sendAction) {
            return this._sendAction;
        }

        this._sendAction = Ext._create('Ext.Button', {
            text: 'Enviar',
            iconCls: 'icon-diarias icon-ocorrencia',
            scope: this,
            handler: function () {
                var selections = this.getSelectionModel().getSelections();

                if (!selections.length) {
                    Ext.Msg.show({
                        title: 'Notificação',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Selecione uma ou mais notificações para enviar.'
                    });
                    return;
                }

                var msg = 'Tem certeza de que deseja enviar esta notificação?';
                if (selections.length > 1) {
                    msg = 'Tem certeza de que deseja enviar estas notificações?';
                }

                Ext.Msg.show({
                    title: 'Notificação',
                    icon: Ext.Msg.QUESTION,
                    buttons: Ext.Msg.YESNO,
                    msg: msg,
                    scope: this,
                    minWidth: 250,
                    fn: function(btn) {
                        if (btn === 'no') {
                            return;
                        }
                        this.send({
                            pkset: selections.map(function(item) {
                                return item.get('pk');
                            })
                        });
                    }
                });
            }
        });

        return this._sendAction;
    },

    defaultValues: function(values) {
        if(values)
            this._defaultValues = values;

        return this._defaultValues;
    },

    createItem: function(values) {
        if(values instanceof Ext.Button)
            values = {};

        values = Ext.applyIf(
            core.nullValue(values, {}),
            this.defaultValues()
        );

        adm.patrimony.notification.Grid.superclass.createItem.call(this, values);
    },

    constructor: function(cfg) {
        cfg = cfg || {};
        Ext.applyIf(cfg, {
            columnAction: true
        });

        adm.patrimony.notification.Grid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'adm.patrimony.notification.Restful',
    'adm.patrimony.notification.Grid'
);
