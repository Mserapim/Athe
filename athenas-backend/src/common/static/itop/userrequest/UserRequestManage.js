Ext._define('common.itop.userrequest.UserRequestManage', {
    extend: 'toolkit.widget.TabPanel',

    getUserRequestGrid: function () {
        if (!this._userRequestGrid) {
            this._userRequestGrid = Ext._create('common.itop.userrequest.UserRequestGrid', {
                region: 'center',
            });

            this._userRequestGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function (selm) {
                    var selection = selm.getSelections();
                    if (selection.length > 0) {
                        this.userRequest(selection[0]);
                    } else {
                        this.userRequest(null);
                    }
                }
            });

            this._userRequestGrid.getStore().on({
                scope: this,
                load: function () {
                    this.observeUserRequest();
                }
            });
        }

        return this._userRequestGrid;
    },

    getPageContainer: function () {
        if (!this._pageContainer)
            this._pageContainer = Ext._create('Ext.Container', {
                autoEl: 'div',
                cls: 'papper-model'
            });

        return this._pageContainer;
    },

    formatHtmlNotifications: function (content) {
        if (!this._formatHtmlNotitications) {
            this._formatHtmlNotitications = Ext._create('Ext.Container', {
                autoEl: 'div',
                cls: 'notification-display',
                html: content
            });
        }
        return this._formatHtmlNotitications;
    },

    getNotifications: function () {
        if (!this._notificationDiplay) {
            this._notificationDiplay = Ext._create('Ext.form.FormPanel', {
                title: 'Informativos',
                labelWidth: 10,
                height: 300,
                width: '60%',
                items: [
                    {
                        xtype: 'displayfield',
                        name: 'title',
                        style: {
                            'font-size': 'small',
                            'font-weight': 'bold',
                            'padding': '10px 0 0 0'
                        }
                    },
                    this.formatHtmlNotifications()

                ],
            })
        }

        return this._notificationDiplay;
    },

    displayContacts: function () {
        if (!this._displayContacts) {
            this._displayContacts = Ext._create('Ext.form.FormPanel', {
                title: 'Central de Serviço - Canais de Comunicação',
                border: true,
                labelWidth: 60,
                height: 300,
                width: '40%',
                items: [
                    {
                        xtype: 'displayfield',
                        name: 'telefone',
                        fieldLabel: 'Telefone',
                        labelStyle: 'font-weight:bold; padding: 10px 0 0 10px',
                        value: '(63) 3216-8888',
                        style: {
                            'padding': '10px 0 0 0',
                        }
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Email',
                        name: 'email',
                        labelStyle: 'font-weight:bold; padding: 10px 0 0 10px',
                        value: 'suporte.ti@mpto.mp.br',
                        style: {
                            'padding': '10px 0 0 0'
                        }
                    },
                ],
            });
        }
        return this._displayContacts;
    },

    getQuickContent: function () {
        if (!this._quickContent) {
            var updateNotification = {
                run: function () {
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action('CIQuickContent', 'get_notifications'),
                        disableCaching: false,
                        method: 'GET',
                        success: function (request) {
                            var obj = Ext.decode(request.responseText);
                            Ext.each(obj.data, function (item) {
                                me.getNotifications().getForm().findField('title').setValue(item.title)
                                // var htmlText = item.description_notify;
                                me.formatHtmlNotifications().update(item.description_notify);
                            }, me);
                        }
                    });
                },
                interval: 60 * 1000 //1 minute
            };

            this._quickContent = Ext._create('Ext.Panel', {
                region: 'south',
                title: 'Conteúdos Rápidos',
                layout: {
                    type: 'hbox',
                    align: 'strech'
                },
                frame: false,
                split: true,
                border: false,
                height: 300,
                items: [
                    this.getNotifications(),
                    this.displayContacts()
                ],
                listeners: {
                    scope: this,
                    render: function () {
                        me = this;
                        Ext.TaskMgr.start(updateNotification);
                    },
                    destroy: function () {
                        Ext.TaskMgr.stop(updateNotification);
                    }
                }
            });
        }
        return this._quickContent;
    },

    getMainPanel: function () {
        if (!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel', {
                region: 'center',
                layout: 'border',
                split: true,
                items: [
                    this.getUserRequestGrid(),
                    this.getQuickContent(),
                ]
            });

        return this._mainPanel;
    },

    getUserRequestDetailTilePanel: function () {
        if (!this._userRequestDetailTilePanel)
            this._userRequestDetailTilePanel = Ext._create('core.TilePagePanel', {
                title: 'Resumo',
                region: 'east',
                height: '100%',
                width: '40%',
                split: true
            });

        return this._userRequestDetailTilePanel;
    },

    rendererDocument: function (id) {
        var mask = new Ext.LoadMask(this.getUserRequestDetailTilePanel().getEl(), { msg: 'Buscando documento...' });
        mask.show();

        Ext.Ajax.request({
            url: core.callAction('CIUserRequest', 'renderer_document'),
            scope: this,
            method: 'GET',
            params: { id: id },
            success: function (response, options) {
                var obj = Ext.decode(response.responseText);

                if (obj.success) {
                    // Apresentando os dados da requisição do usuário
                    this.getUserRequestDetailTilePanel().enable();
                    this.getUserRequestDetailTilePanel().setPageContent(obj.document.content);
                }
                else {
                    // Caso ocorra erro ao buscar a requisição do usuário
                    Ext.Msg.show({
                        title: this.title,
                        icon: Ext.Msg.WARNING,
                        buttons: Ext.Msg.OK,
                        msg: obj.message
                    });
                }
            },
            failure: function (response, options) {
                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: response.status
                });
            },
            callback: function (options, success, response) {
                mask.hide();
            }
        });
    },

    cleanDocument: function () {
        this.getUserRequestDetailTilePanel().setPageContent('');
        this.getUserRequestDetailTilePanel().disable();
    },

    userRequest: function (value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined) {
            this._userRequestGrid = value;

            if (observe)
                this.observeUserRequest();
        }

        return this._userRequestGrid;
    },

    observeUserRequest: function () {
        var value = this.userRequest();

        if (value) {
            this.rendererDocument(value.id);
        } else {
            this.cleanDocument();
        }
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                title: 'Abrir Chamado',
                layout: 'border',
                items: [
                    this.getMainPanel(),
                    this.getUserRequestDetailTilePanel()
                ]
            }
        );

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function (instance) {
                    this.userRequest(instance.pk);
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        this.userRequest(cfg.oId === undefined ? null : cfg.oId);
        common.itop.userrequest.UserRequestManage.superclass.constructor.call(this, cfg);
    }
});
