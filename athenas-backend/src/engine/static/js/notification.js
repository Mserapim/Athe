if(typeof(toolkit.engine.notification) == 'undefined') {
    Ext.ns('toolkit.engine.notification');

    toolkit.engine.notification.CustomView = Ext.extend(
        Ext.Panel,
        {
            constructor: function() {
                var cf = {
                    title: 'Mensagens',
                    border: false,
                    closable: false,
                    layout: 'border',
                    store: {
                        'in': undefined,
                        'out': undefined
                    },
                    boxPaginator: {
                        'in': undefined,
                        'out': undefined
                    },
                    boxColumnModel: {
                        'in': undefined,
                        'out': undefined
                    },
                    listView: {
                        'in': undefined,
                        'out': undefined
                    }
                };

                toolkit.engine.notification.CustomView.superclass.constructor.call(this, cf);
                var active = toolkit.Application.tabspace.getActiveTab();
                toolkit.Application.tabspace.remove(active);
                toolkit.Application.tabspace.add(this);

                this.add(this.getPreVisualizacao());
                this.add(this.getContentTilePanel());

                this.on('render', function() {
                    this.getStore(this.getParamsStore('in')).load();
                    this.getStore(this.getParamsStore('out')).load();
                },this);
            },

            send: function() {
                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('ENGNotificationCustom', 'is_chefe'),
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);

                        new toolkit.engine.notification.NotificationWindow({
                            father: this,
                            chefe: obj.chefe
                        }).show();
                    },
                    failure: function(request) {
                        new toolkit.engine.notification.NotificationWindow({
                            father: this,
                            chefe: false
                        }).show();
                    },
                    scope: this
                });
            },

            getKeywordInput: function(type) {
                this._keywordInput = core.nullValue(this._keywordInput, []);
                if(!this._keywordInput[type])
                    this._keywordInput[type] = Ext._create('Ext.form.TextField', {
                        width: 350,
                        emptyText: 'Busca por mensagens...',
                        enableKeyEvents: true,
                        listeners: {
                            scope: this,
                            specialkey: function(field, e) {
                                if(e.getKey() == e.ENTER || e.getKey() == e.TAB) {
                                    var store = this.getBox(type).getStore();

                                    store.baseParams.keyword = field.getValue();
                                    store.load();
                                }
                            }
                        }
                    });

                return this._keywordInput[type];
            },

            getPreVisualizacao: function() {
                if(!this.preVisualizacao) {
                    this.preVisualizacao = new Ext.TabPanel({
                        region: 'center',
                        border: true,
                        tabPosition: 'top',
                        activeTab: 0,
                        headerStyle: 'border-left: none; boder-bottom: none; border-top: none',
                        bodyStyle: 'border-left: none; boder-bottom: none; border-top: none',
                        items: [
                            this.getBoxIn(),
                            this.getBoxOut()
                        ],
                        listeners: {
                            scope: this,
                            tabchange: function(panel, tab) {
                                var selection = tab.items.first().getSelectedRecords();

                                if(selection.length > 0)
                                    this.getContentTilePanel().setPageContent(selection[0].get('msg'));
                                else
                                    this.getContentTilePanel().setPageContent('');
                            }
                        }
                    });
                }

                return this.preVisualizacao;
            },

            getBoxIn: function() {
                if(!this.boxIn)
                    this.boxIn = new Ext.Panel({
                        title: "Entrada",
                        border: false,
                        layout: 'fit',
                        tbar:[{
                                text: 'Enviar',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/engine/images/icons/athenas-0194.png',
                                handler: this.send,
                                scope: this
                            },
                            '-',
                            'Buscar: ',
                            this.getKeywordInput('in')
                        ],
                        items: this.getBox('in'),
                        bbar: this.getBoxPaginator('in')
                    });

                return this.boxIn;
            },

            getBoxOut: function() {
                if(!this.boxOut)
                    this.boxOut = new Ext.Panel({
                        title: "Saída",
                        border: false,
                        layout: 'fit',
                        tbar:[
                            'Buscar: ',
                            this.getKeywordInput('out')
                        ],
                        items: this.getBox('out'),
                        bbar: this.getBoxPaginator('out')
                    });

                return this.boxOut;
            },

            getBox: function(type) {
                if(!this.listView[type])
                    this.listView[type] = new Ext.list.ListView({
                        title: type == 'in' ? 'Entrada' : 'Saída',
                        name: type == 'in' ? 'in' : 'out',
                        id: type == 'in' ? 'in' : 'out',
                        border: false,
                        store: this.getStore(this.getParamsStore(type)),
                        singleSelect: true,
                        columns: this.getBoxColumnModel(type),
                        listeners: {
                            scope: this,
                            selectionchange: function(listview) {
                                var selection = listview.getSelectedRecords();

                                if(selection.length > 0)
                                    this.getContentTilePanel().setPageContent(selection[0].get('msg'));
                                else
                                    this.getContentTilePanel().setPageContent('');
                            }
                        }
                    });

                return this.listView[type];
            },

            getBoxPaginator: function(type) {
                if(!this.boxPaginator[type]) {
                    this.boxPaginator[type] = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStore(this.getParamsStore(type)),
                        displayInfo: true,
                        pageSize: 20,
                        prependButtons: true
                    });
                }

                return this.boxPaginator[type];
            },

            getBoxColumnModel: function(type) {
                if(!this.boxColumnModel[type]) {
                    var tpl = new Ext.XTemplate(
                        '<div class="notification-item">',
                            '<div style="float:left;">',
                                  '<div class="status-notify" style="width: 60px; display:table;">',
                                        '<tpl if="status_notify==1"><div ext:qtip="Não enviado" class="icon-notification icon-notification-not-sended"></div></tpl>',
                                        '<tpl if="status_notify==2"><div ext:qtip="Não lido" class="icon-notification icon-notification-unread"></div></tpl>',
                                        '<tpl if="status_notify==4"><div ext:qtip="Erro" class="icon-notification icon-notification-error"></div></tpl>',
                                        '<tpl if="status_notify==8"><div ext:qtip="Lido" class="icon-notification icon-notification-read"></div></tpl>',
                                  '</div>',
                                  '<div class="type-notify" style="width: 60px; display:table;">',
                                        '<tpl if="type_notify==\'SYS\'"><div ext:qtip="Sistema" class="icon-notification icon-notification-type-system"></div></tpl>',
                                        '<tpl if="type_notify==\'EMAIL\'"><div ext:qtip="Correio Eletrônico" class="icon-notification icon-notification-type-email"></div></tpl>',
                                        '<tpl if="type_notify==\'SMS\'"><div ext:qtip="Mensagem para celular" class="icon-notification icon-notification-type-sms"></div></tpl>',
                                        '<tpl if="type_notify==\'ONTOP\'"><div ext:qtip="Notificação em destaque" class="icon-notification icon-notification-warn"></div></tpl>',
                                  '</div>',
                                  '<div class="type-message" style="width: 60px; display:table;">',
                                        '<tpl if="type_msg==\'INFO\'"><div ext:qtip="Informação" class="icon-notification icon-notification-info"></div></tpl>',
                                        '<tpl if="type_msg==\'WARNING\'"><div ext:qtip="Atenção" class="icon-notification icon-notification-warn"></div></tpl>',
                                        '<tpl if="type_msg==\'ERROR\'"><div ext:qtip="Problema" class="icon-notification icon-notification-error"></div></tpl>',
                                  '</div>',
                            '</div>',
                            '<div class="notification-select-text">',
                                (type == 'in' ? '<div>De: {origem}</div>' : '<div>Para: {destino}</div>'),
                                '<div>Data: {data}</div>',
                                '<div>Assunto: {assunto}</div>',
                            '</div>',

                        '</div>',
                        '<div class="x-clear"></div>'
                    );

                    this.boxColumnModel[type] = [
                        {header: 'Mensagens', tpl: tpl},
                    ];
                }

                return this.boxColumnModel[type];
            },

            getStore: function(args) {
                if(this.store[args.type] == undefined) {
                    this.store[args.type] = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            args.controller,
                            args.method
                        ),
                        fields: args.fields,
                        root: 'result',
                        totalProperty: 'totalRows',
                        baseParams: args.baseParams,
                        autoLoad: false
                    });
                }

                return this.store[args.type];
            },

            getParamsStore: function(type) {
                return {
                    type: type == 'in' ? 'in' : 'out',
                    controller: 'ENGNotificationCustom',
                    method: 'store/'+type,
                    fields: [
                        'codigo',
                        'origem',
                        'destino',
                        'data',
                        'assunto',
                        'msg',
                        'type_msg',
                        'type_notify',
                        'status_notify'
                    ],
                    baseParams: {start: 0, limit: 20}
                };
            },

            getContentTilePanel: function() {
                if(!this._contentTilePanel)
                    this._contentTilePanel = Ext._create('core.TilePagePanel', {
                        region: 'east',
                        minWidth: 810,
                        maxWidth: 810,
                        width: 810,
                        papperModel: 'card',
                        split: true
                    });

                return this._contentTilePanel;
            },

        }
    );

    /**
     *
     **/
    toolkit.engine.notification.NotificationWindow = Ext.extend(
        Ext.Window,
        {
            constructor: function(cfg) {
                cf = {
                    title: 'Escrever mensagem',
                    closable: true,
                    modal: true,
                    width: 900,
                    buttonAlign: "right",
                    border: false,
                    buttons: [
                        {
                            text: "Enviar",
                            handler: this.commit,
                            scope: this
                        },
                        {
                            text: "Cancelar",
                            handler: function() {this.destroy();},
                            scope: this
                        }
                    ]
                };

                Ext.apply(cf, cfg);

                toolkit.engine.notification.NotificationWindow.superclass.constructor.call(this, cf);
                this.add(this.getPanelConteiner());
            },

            isSuper: function() { return (this.chefe == true) },

            /**
             * @param args.controller
             * @param args.method
             * @param args.fields
             * @param args.baseParams
             **/
            getStore: function(args) {
                if(!this.storeGrid) {
                    this.storeGrid = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            args.controller,
                            args.method
                        ),
                        fields: args.fields,
                        root: 'result',
                        totalProperty: 'totalRow',
                        baseParams: args.baseParams,
                        autoLoad: true
                    });
                }

                return this.storeGrid;
            },

            getPanelConteiner: function() {
                if(!this.panelConteiner) {
                    this.panelConteiner = new Ext.form.FormPanel({
                        frame: true,
                        border: false,
                        defaults: {width: 872},
                        labelAlign: 'top',
                        items: this.getConteinerFields()
                    });
                }

                return this.panelConteiner;
            },

            getConteinerFields: function() {
                if(!this.fields) {
                    this.fields = [
                        {
                            xtype: 'panel',
                            layout: 'hbox',
                            border: true,
                            height: 60,
                            items: [
                                {
                                    xtype: 'panel',
                                    layout: 'form',
                                    labelAlign: 'top',
                                    items:  {
                                        name: "header",
                                        fieldLabel: "Assunto",
                                        xtype: "textfield",
                                        allowBlank: false,
                                        validateOnBlur: true,
                                        maxLength: 120,
                                        blankText: "É necessário preencher este campo.",
                                        width: 735
                                    },
                                    width: 740
                                },
                                {
                                    xtype: 'panel',
                                    layout: 'form',
                                    style: 'margin-left:5px',
                                    labelAlign: 'top',
                                    items: {
                                        hiddenName: 'ontop',
                                        xtype: 'combo',
                                        fieldLabel: 'Destaque',
                                        store: [
                                            [true, 'Sim'],
                                            [false, 'Não'],
                                        ],
                                        value: false,
                                        width: 125,
                                        triggerAction: 'all',
                                        editable: false,
                                        disabled: !this.isSuper()
                                    }
                                }
                            ]
                        },
                        {
                            xtype: 'ckeditor',
                            fieldLabel: 'Mensagem',
                            name: "message",
                            height: 175
                        },
                        {
                            name: "servidor",
                            fieldLabel: "Enviar para os Servidores",
                            xtype: "multiselectbox",
                            toSearch: [],
                            allowBlank: false,
                            validateOnBlur: true,
                            height: 150,
                            border: true,
                            blankText: "É necessário preencher este campo.",
                            model: {name: "Servidor", pkg: "rh.models"},
                            controller: "RHServidor",
                            queryset: [],
                            queryAction: 'query_rh'
                        }
                    ];
                }

                return this.fields;
            },

            commit: function() {
                var form = this.getPanelConteiner().getForm();
                form.waitMsgTarget = this.getEl();
                if(form.getFieldValues(0).header == "")
                    form.findField('header').markInvalid();
                else if(form.getFieldValues(0).message == "<br><!-- Correção de bug da ExtJS -->" || form.getFieldValues(0).message == "")
                    alert('Informe a mensagem!');
                else if(form.getFieldValues(0).servidor == "")
                    alert('Informe o servidor!');
                else form.submit({
                    url: toolkit.util.Normalize.controller_action(
                        'ENGNotificationCustom',
                        'enviar'
                    ),
                    validate: 'client',
                    waitMsg: 'Enviando mensagem...',
                    success: function(form, action) {
                        this.father.getStore(this.father.getParamsStore('in')).load();
                        this.father.getStore(this.father.getParamsStore('out')).load();
                        this.getPanelConteiner().ownerCt.destroy();
                    },
                    failure: function(form, action) {alert('Falha no envio da mensagem!');},
                    scope: this
                });
            }
        }
    );

}
