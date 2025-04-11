Ext._define('planning.hiring.minutesolicitation.MinuteSolicitationWindow', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.minutesolicitation.MinuteSolicitationRestful',
    resizable: false,
    width: 1000,
    autoHeight: true,

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                labelAlign: 'top',
                frame: true,
                items: [
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    {
                                        xtype: "displayfield",
                                        fieldLabel: "Edoc",
                                        allowBlank: true,
                                        name: "edoc_display",
                                    },
                                ],
                            },
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    {
                                        xtype: 'displayfield',
                                        fieldLabel: 'Situa\u00e7\u00e3o do Pedido',
                                        name: 'situation_display',
                                        anchor: '99%',
                                    },
                                ],
                            },
                        ]
                    },
                    {
                        allowBlank: false,
                        fieldLabel: "Justificativa",
                        name: "justification",
                        xtype: "ckeditor",
                    },
                    this.getMinuteSolicitationItemGrid(),
                ]
            });

        return this._formPanel;
    },

    getMinuteSolicitationItemGrid: function (cfg) {
        if (!this._minuteSolicitationItemPanel) {
            this._minuteSolicitationItemPanel = Ext._create('planning.hiring.minutesolicitation.MinuteSolicitationItemGrid', {
                title: 'Itens',
                region: 'center',
                frame: true,
                height: 300,
            });
        }
        return this._minuteSolicitationItemPanel;
    },


    solicitation: function (value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined) {
            this._minuteSolicitationGrid = value;

            if (observe)
                this.observeMinuteSolicitation();
        }

        return this._minuteSolicitationGrid;
    },

    observeMinuteSolicitation: function () {
        var value = this.solicitation();

        if (value) {
            this.getMinuteSolicitationItemGrid().enable();
            this.getMinuteSolicitationItemGrid().setParam('solicitation', value);
            this.getMinuteSolicitationItemGrid().setParam('minute', this.values.minute);
            this.getMinuteSolicitationItemGrid().setFilterProperty('solicitation', value, 0);
        } else {
            this.getMinuteSolicitationItemGrid().disable();
            this.getMinuteSolicitationItemGrid().setParam('solicitation', 0);
            this.getMinuteSolicitationItemGrid().setFilterProperty('solicitation', value, 0, false);
            this.getMinuteSolicitationItemGrid().getStore().removeAll();
        }
    },

    getButtons: function (cfg) {

        if (!this._buttons) {
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];

            if (!cfg.disableSave)
                this._buttons = [{
                    text: 'Salvar',
                    scope: this,
                    handler: function () {
                        var me = this;
                        Ext.Ajax.request({
                            scope: this,
                            url: toolkit.util.Normalize.controller_action(
                                'PHMMinute',
                                'verify_minute_validity'
                            ),
                            params: {
                                minute: this.params.minute,
                            },
                            success: function (response) {
                                var obj = Ext.decode(response.responseText);
                                if (obj.success) {
                                    if (obj.before_begin_validity)
                                        Ext.Msg.show({
                                            title: 'Ata fora da vigência',
                                            icon: Ext.Msg.QUESTION,
                                            buttons: Ext.Msg.YESNO,
                                            msg: obj.message,
                                            fn: function (bnt) {
                                                if (bnt == 'no') return;
                                                me.save(true);
                                            }
                                        });
                                        if (obj.days_for_validity)
                                            Ext.Msg.show({
                                                title: 'Ata próxima do vencimento',
                                                icon: Ext.Msg.INFO,
                                                buttons: Ext.Msg.OK,
                                                msg: obj.message,
                                                fn: function (bnt) {
                                                    if (bnt == 'ok')
                                                        me.save(true);
                                            }
                                        });
                                    else
                                        me.save(true);
                                }
                                else
                                    Ext.Msg.show({
                                        title: 'Ata fora da vigência',
                                        icon: Ext.Msg.ERROR,
                                        buttons: Ext.Msg.OK,
                                        msg: obj.message
                                    });
                            },
                            failure: function (response) {
                                Ext.Msg.show({
                                    title: 'Não foi possível preencher o conteúdo do Edoc.',
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK,
                                    msg: rst.message
                                });
                            }

                        });
                    },
                }].concat(this._buttons);

        }

        return this._buttons;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function (instance) {
                    this.solicitation(instance.pk);
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        planning.hiring.minutesolicitation.MinuteSolicitationWindow.superclass.constructor.call(this, cfg);

        this.solicitation(cfg.oId === undefined ? null : cfg.oId);
    }
});

