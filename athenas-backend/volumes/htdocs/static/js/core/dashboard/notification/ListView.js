Ext._define('core.dashboard.notification.ListView', {
    extend: 'Ext.list.ListView',

    mixins: { '1': 'core.utils.LoadMaskMixin' },

    _totalUnread: 0,

    _selectionChangeEvent: function (listView, selections) {
        var selected = this.getSelectedRecord();

        if (!selected) {
            return;
        }

        Ext._create('core.dashboard.notification.Window', {
            message: selected.get('message'),
            listeners: {
                scope: this,
                destroy: function () {
                    this.markSelectedAsRead();
                },
            },
        }).show();
    },

    markSelectedAsRead: function () {
        var selected = this.getSelectedRecord();

        if (!selected || selected.get('status') !== 2) {
            return;
        }

        Ext.Ajax.request({
            url: core.callAction('ENGNotification', 'read'),
            params: {
                notif: selected.get('id'),
            },
            scope: this,
            success: function (xhr) {
                var result = Ext.decode(xhr.responseText);

                if (result.success) {
                    this.getStore().reload();
                    return;
                }

                Ext.Msg.show({
                    title: 'Notificação',
                    msg: result.error,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                });
            },
            failure: function (xhr) {
                Ext.Msg.show({
                    title: 'Notificação',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                });
            },
        });
    },

    getSelectedRecord: function () {
        if (this.getSelectedRecords().length > 0) {
            return this.getSelectedRecords()[0];
        }

        return null;
    },

    getXTemplate: function (cfg) {
        if (this._template) {
            return this._template;
        }

        this._template = new Ext.XTemplate(
            '<div class="dashboard-notif-container">',
                '<div class="dashboard-notif-item">',
                    '<tpl if="status==1"><div ext:qtip="Não enviado" class="icon-notification icon-notification-not-sended"></tpl>',
                    '<tpl if="status==2"><div ext:qtip="Não lido" class="icon-notification icon-notification-unread"></div></tpl>',
                    '<tpl if="status==4"><div ext:qtip="Erro" class="icon-notification icon-notification-error"></div></tpl>',
                    '<tpl if="status==8"><div ext:qtip="Lido" class="icon-notification icon-notification-read"></div></tpl>',
                '</div>',
                '<div class="dashboard-notif-item"><span>De:&nbsp;&nbsp;</span>{origin}</div>',

                '<div class="dashboard-notif-item">',
                    '<tpl if="media_type==\'EMAIL\'"><div ext:qtip="Correio Eletrônico" class="icon-notification icon-notification-type-email"></div></tpl>',
                    '<tpl if="media_type==\'ONTOP\'"><div ext:qtip="Notificação em destaque" class="icon-notification icon-notification-warn"></div></tpl>',
                    '<tpl if="media_type==\'SMS\'"><div ext:qtip="Mensagem para celular" class="icon-notification icon-notification-type-sms"></div></tpl>',
                    '<tpl if="media_type==\'SYS\'"><div ext:qtip="Sistema" class="icon-notification icon-notification-type-system"></div></tpl>',
                '</div>',
                '<div class="dashboard-notif-item"><span>Assunto:&nbsp;&nbsp;</span>{subject}</div>',

                '<div class="dashboard-notif-item">',
                    '<tpl if="message_type==\'INFO\'"><div ext:qtip="Informação" class="icon-notification icon-notification-info"></div></tpl>',
                    '<tpl if="message_type==\'WARN\'"><div ext:qtip="Atenção" class="icon-notification icon-notification-warn"></div></tpl>',
                    '<tpl if="message_type==\'ERROR\'"><div ext:qtip="Problema" class="icon-notification icon-notification-error"></div></tpl>',
                '</div>',
                '<div class="dashboard-notif-item"><span>Data:&nbsp;&nbsp;</span>{created_at}</div>',
            '</div>',
        );

        return this._template;
    },

    getFields: function () {
        if (this._fields) {
            return this._fields;
        }

        this._fields = [
            'id',
            'origin',
            'destination',
            'subject',
            'message',
            'status',
            'media_type',
            'message_type',
            'created_at',
        ];

        return this._fields;
    },

    getTotalUnread: function () {
        return this._totalUnread;
    },

    getHttpProxy: function () {
        if (this._httpProxy) {
            return this._httpProxy;
        }

        this._httpProxy = Ext._create('Ext.data.HttpProxy', {
            url: core.callAction('RHServidor', 'notifications'),
            method: 'GET',
        });

        return this._httpProxy;
    },

    getJsonReader: function () {
        if (this._jsonReader) {
            return this._jsonReader;
        }

        this._jsonReader = Ext._create('Ext.data.JsonReader', {
            fields: this.getFields(),
            root: 'collection',
            totalProperty: 'count',
        });

        return this._jsonReader;
    },

    _beforeLoadEvent: function (store, options) {
        this.showMask();  // mixin
    },

    _loadEvent: function (store, records, options) {
        this.hideMask();  // mixin

        if (this.getJsonReader().jsonData) {
            this._totalUnread = this.getJsonReader().jsonData['totalUnread'];
        }
    },

    // O Store irá disparar o evento exception se a
    // propriedade 'success' do JSON de resposta for false.
    // É um comportamento que a documentação não explica.
    _exceptionEvent: function (misc) {
        this.hideMask();  // mixin

        var reader = this.getJsonReader();

        if (reader.jsonData && reader.jsonData.message) {
            console.error('Notificações:', reader.jsonData.message);
        }
    },

    getStore: function () {
        if (this._store) {
            return this._store;
        }

        this._store = Ext._create('Ext.data.Store', {
            proxy: this.getHttpProxy(),
            reader: this.getJsonReader(),
            baseParams: {start: 0, limit: 10},
            autoLoad: true,
            listeners: {
                scope: this,
                beforeload: this._beforeLoadEvent,
                load: this._loadEvent,
                exception: this._exceptionEvent,
            },
        });

        return this._store;
    },

    getEmptyBody: function () {
        return [
            '<div ',
            'class="dashboard-emptybody-text" ',
            'style="padding-top: 42px"',
            '>',
                '&lt;',
                ' Nenhuma notificação encontrada ',
                '&gt;',
            '</div>'
        ].join('');
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            loadingMessage: 'Carregando dados...',  // mixin
            hideHeaders: true,
        });

        Ext.apply(cfg, {
            emptyText: this.getEmptyBody(),
            //loadingText: 'Carregando notificações...',
            singleSelect: true,
            columns: [{
                //header: 'Mensagens',
                tpl: this.getXTemplate(cfg),
            }],
            store: this.getStore(),
            listeners: {
                scope: this,
                selectionchange: this._selectionChangeEvent,
            },
        });

        core.dashboard
          .notification
          .ListView
          .superclass
          .constructor
          .call(this, cfg);
    },
});
