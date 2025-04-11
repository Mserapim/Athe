Ext._define('rh.dayoff.acquisitionperiod.HomologateWindow', {
    extend: 'Ext.Window',

    constructor: function (cfg, args) {
        cfg = core.nullValue(cfg, {});
        var _idsHomologate = cfg.idsHomologate || [];
        Ext.applyIf(
            cfg,
            {
                title: 'Homologar',
                width: 400,
                height: cfg.hasFields == true ? 180 : 80,
                border: false,
                items: [
                    this.getFormPanel(cfg)
                ],
            }
        )
        rh.dayoff.acquisitionperiod.HomologateWindow.superclass.constructor.call(this, cfg);
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                defaults: {
                    width: 260,
                    border: false
                },
                items: this.getItems(cfg),
                buttons: [
                    {
                        text: 'Homologar',
                        scope: this,
                        handler: this._homologate
                    },
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: function () {
                            this.destroy();
                        }
                    }
                ]
            });
        return this._formPanel;
    },

    getItems: function (cfg) {
        var items = [];
        if (cfg.hasFields == true) {
            items = [
                {
                    xtype: 'button',
                    text: 'Visualizar Anexo',
                    fieldLabel: 'Anexo',
                    anchor: '50%',
                    scope: this,
                    handler: function () {
                        form = this.getFormPanel().getForm();
                        attachment_value = form.findField('attachment').getValue()

                        if (attachment_value === undefined || attachment_value === "") {
                            action = 'create'
                            oId_value = null
                        }
                        else {
                            action = 'update';
                            oId_value = attachment_value;
                        }
                        Ext._create('rh.dayoff.attachment.Window', {
                            title: 'Anexo',
                            oId: oId_value,
                            action: action,
                            values: 'remote',
                            callback: {
                                success: {
                                    scope: this,
                                    fn: function (instance) {
                                        form.findField('attachment').setValue(instance.pk)
                                    }
                                }
                            }
                        }).show();
                    },
                },
                {
                    name: 'attachment',
                    fieldLabel: 'Anexo',
                    xtype: 'textfield',
                    allowBlank: true,
                    hidden: true
                },
                {
                    xtype: 'datefield',
                    fieldLabel: 'Data de Publicação',
                    name: 'publication_date',
                    allowBlank: true
                },
                {
                    xtype: 'datefield',
                    fieldLabel: 'Data de Homologação',
                    name: 'homologation_date',
                    allowBlank: true
                }
            ];
        }
        return items;
    },

    _homologate: function () {
        var homologation_date = undefined;
        var publication_date = undefined;
        var attachment = undefined;
        if (this.hasFields) {
            var form = this.getFormPanel().getForm();
            homologation_date = Ext.util.Format.date(form.findField('homologation_date').getValue(), 'd/m/Y');
            publication_date = Ext.util.Format.date(form.findField('publication_date').getValue(), 'd/m/Y');
            attachment = form.findField('attachment').getValue();
            if (!homologation_date || !attachment || !publication_date) {
                Ext.Msg.show({
                    title: 'Homologar',
                    msg: 'Publicação e Data de Publicação/Homologação obrigatório(s)',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
                return;
            }
        }
        var params = {
            actionCustom: 'homologate',
            activity: this.idsHomologate,
            homologation_date: homologation_date,
            publication_date: publication_date,
            attachment: attachment
        };

        this._process(params);
    },

    _process: function (params) {
        var rest = Ext._create(this.rest, { resource: this.resource });
        var mask = Ext._create('Ext.LoadMask', this.getEl(), { msg: 'Processando informações.' });
        var wnd = this;

        mask.show();
        rest._process(
            params,
            {
                scope: this,
                fn: function (rst) {
                    core.invokeCallback((wnd.externalCallback || { fn: Ext.emptyFn }), rst.message);
                    wnd.close();
                }
            },
            {
                fn: function (message) {
                    Ext.Msg.show({
                        title: 'Informando',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: message
                    });
                }
            },
            {
                fn: function () {
                    mask.hide();
                }
            }
        );
    },
});


