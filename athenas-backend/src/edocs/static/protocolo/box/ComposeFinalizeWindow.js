Ext._define('edocs.protocolo.box.ComposeFinalizeWindow', {
    extend: 'edocs.protocolo.box.ComposeMovementWindow',


    getAdvicePanel: function (cfg) {
        if (!this._advicePanel)
            this._advicePanel = Ext._create('Ext.Panel', {
                title: 'Parecer',
                border: false,
                items: [{
                    xtype: 'container',
                    items: [{
                        xtype: 'ckeditor',
                        name: 'advice',
                        height: 465
                    }]
                }, ]
            });

        return this._advicePanel;
    },

    getTabPanel: function (cfg) {
        if (!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                height: 600,
                activeTab: 0,
                items: [
                    this.getAdvicePanel(cfg),
                    this.getAttachmentGrid(cfg),
                ],
                listeners: {
                    scope: this,
                    render: function (panel) {
                        panel.activate(this.getAdvicePanel());
                    }
                }
            });

        return this._tabPanel;
    },

    finalize: function () {

        var values = this.getFormPanel().getForm().getValues();
        var mask = new Ext.LoadMask(this.getEl(), {
            msg: 'Finalizando...'
        });

        values.person_destination = [];
        values.location_destination = [];
        values.group_person = [];
        values.group_location = [];

        values.attachments = {};
        values.movement = this.movement;

        values.urgency = 'off';
        values.close = 'on';
        values.opinion = 'on';
        values.physical = 'off';

        function prepareOperation(store) {
            var field = {
                create: [],
                update: [],
                delete: []
            };

            store.each(
                function(data) {
                    var operation = data.get('operation');

                    if(operation === 'C')
                        field.create.push(data.data);
                    else if(operation === 'U')
                        field.update.push(data.data);
                    else if(operation === 'D')
                        field.update.push(data.get('pk'));
                    else
                        console.warn('Unknow operation %s', operation);
                }
            );

            return Ext.encode(field);
        }

        values.attachments = prepareOperation(this.getAttachmentGrid().getStore());

        mask.show();
        Ext.Ajax.request({
            url: core.callAction('EDOCManage', 'send'),
            scope: this,
            params: values,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var rst = Ext.decode(xhr.responseText);

                if (rst.success) {
                    core.invokeCallback((this.success || {
                        fn: Ext.emptyFn
                    }), rst);
                    this.close();
                } else
                    Ext.Msg.show({
                        title: 'Finalizando',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function () {
                Ext.Msg.show({
                    title: 'Finalizando',
                    msg: 'Recurso indisponivel no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            },
        });
    },

    send: function () {
        Ext.Msg.show({
            title: 'Finalizando protocolos',
            msg: 'Tem certeza que deseja finalizar o protocolo?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (btn) {
                if (btn == 'no') return;

                this.finalize();
            }
        });
    },

    getButtons: function (cfg) {
        if (!this._buttons) {
            this._buttons = [{
                    text: 'Finalizar',
                    scope: this,
                    handler: this.send
                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: function () {
                        this.close();
                    }
                }
            ];
        }

        return this._buttons;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg, {
                title: 'Finalização de Protocolo',
                modal: true,
            }
        );

        edocs.protocolo.box.ComposeFinalizeWindow.superclass.constructor.call(this, cfg);
    }
});
