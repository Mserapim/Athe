Ext._define('raf.adjustment.dataadjustment.RejectWindow', {
    extend: 'Ext.Window',

    reject: function() {
        var rest = Ext._create('raf.adjustment.dataadjustment.Restful');
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Rejeitar Solicitação de Ajuste...'});
        var values = this.getFormPanel().getForm().getValues();
        values.activityadjustment = (this.values.activityadjustment || 0);
        values.dataadjustment_list = (this.values.dataadjustment_list || 0);
        values.situation = (this.values.situation || 0);
        mask.show();
        rest.action(
            values,
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        core.invokeCallback((this.callback || {}).success);
                        this.close();
                        Ext.Msg.show({
                            title: 'Rejeitar Solicitação de Ajuste',
                            msg: rst.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                    }
                    else
                        Ext.Msg.show({
                            title: 'Rejeitar Solicitação de Ajuste',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Rejeitar Solicitação de Ajuste',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: "hidden",
                        name: "situation",
                    },
                    {
                        xtype:'fieldset',
                        title: 'Parecer',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                           {
                               fieldLabel: "Resposta",
                               xtype: "ckeditor",
                               hideLabel: true,
                               allowBlank: false,
                               name: "answer",
                               submit: true,
                               height: 400,
                               toolbarGroups: [
                                   {name: 'styles', itens: ['Format']},
                                   {name: 'clipboard'},
                                   {name: 'editing'},
                                   {name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ]},
                                   {
                                       name: 'paragraph',
                                       groups: ['list', 'indent', 'blocks', 'align', 'bidi'],
                                   },
                               ],
                           }
                        ]
                    },
                ]
            });

        return this._formPanel;
    },


    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            title: 'Rejeitar Solicitação de Ajuste',
        });
        Ext.apply(cfg, {
            width: 700,
            items: [
                this.getFormPanel(cfg)
            ],
            buttons: [
                {
                    text: 'Indeferir',
                    scope: this,
                    handler: function() { this.reject(); }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });
        raf.adjustment.dataadjustment.RejectWindow.superclass.constructor.call(this, cfg);
    }
});
